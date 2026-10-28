"""Phase 2: judge pilot on SciEntsBank + Beetle (unseen-answers test splits).

prepare -> sample questions/answers, build one checklist rubric per question (generator role)
run     -> grade every sampled answer with one judge role; resumable via the response cache
stability -> rerun a subset fresh to measure verdict flip rate (does not touch the cache)
report  -> metrics with bootstrap CIs for every judge that has results, plus the gate verdict
"""

import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT
from eval_engine.hashing import sha256_hex
from eval_engine.providers.base import ProviderError, QuotaExhausted
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.schemas.judge import JudgeOutput
from eval_engine.schemas.rubric import Rubric, RubricDraft
from eval_engine.storage.rubric_store import RubricStore
from eval_engine.validation import metrics as m
from eval_engine.validation.datasets import (
    DATASET_DIR,
    GradedAnswer,
    load_split,
    sample_by_question,
)
from eval_engine.validation.labels import (
    HUMAN_GRADED,
    JudgeOutputMismatch,
    engine_labels,
    human_2way,
    human_3way,
)

PILOT_DIR = REPO_ROOT / "experiments" / "2_judge_pilot"
SOURCES = (("SciEntsBank", "test_ua"), ("Beetle", "test_ua"))
LENIENCY_TARGET = 0.1


@dataclass(frozen=True)
class PilotConfig:
    answers_per_dataset: int = 150
    max_per_question: int = 5  # capped at the median answers-per-question of each dataset
    seed: int = 13


def plan_sample(items: list[GradedAnswer], cfg: PilotConfig) -> tuple[int, int]:
    """(n_questions, per_question) for one dataset. SciEntsBank test_ua has exactly 4 answers
    per question; Beetle has 1 to 78, so a fixed per-question count doesn't fit both."""
    counts = sorted(Counter(i.question_key for i in items).values())
    per_q = max(1, min(cfg.max_per_question, counts[len(counts) // 2]))
    return math.ceil(cfg.answers_per_dataset / per_q), per_q


@dataclass
class ResultRow:
    item_id: str
    dataset: str
    human_label: str
    rubric_hash: str
    engine_2way: str | None = None
    engine_3way: str | None = None
    engine_graded: float | None = None
    weighted_score: float | None = None
    n_errors: int | None = None
    max_path_confidence: float | None = None
    call_id: str | None = None
    error: str | None = None


def rubric_id_for(item: GradedAnswer, prompt_hash: str = "") -> str:
    """The rubric prompt's hash is part of the id, so editing the prompt yields fresh rubrics
    instead of silently reusing ones built by an older version."""
    return "ds-" + sha256_hex(f"{item.question_key}::{prompt_hash}")[:16]


def _load_items(directory: Path) -> dict[str, GradedAnswer]:
    out: dict[str, GradedAnswer] = {}
    for dataset, split in SOURCES:
        for it in load_split(dataset, split, directory):
            out[it.item_id] = it
    return out


def prepare(
    client: LLMClient,
    store: RubricStore,
    cfg: PilotConfig | None = None,
    *,
    data_dir: Path = DATASET_DIR,
    out_dir: Path = PILOT_DIR,
) -> dict[str, Any]:
    """Idempotent: rubrics already in the store are reused, so a quota stop can resume."""
    cfg = cfg or PilotConfig()
    prompt_hash = client.prompts.get("dataset_rubric").file_hash
    items = list(_load_items(data_dir).values())
    sample: list[GradedAnswer] = []
    for dataset, _split in SOURCES:
        subset = [i for i in items if i.dataset == dataset]
        n_q, per_q = plan_sample(subset, cfg)
        sample += sample_by_question(subset, n_q, per_q, cfg.seed)

    first_per_q: dict[str, GradedAnswer] = {}
    for it in sample:
        first_per_q.setdefault(rubric_id_for(it, prompt_hash), it)

    built = reused = 0
    for rid, it in first_per_q.items():
        try:
            store.latest(rid)
            reused += 1
            continue
        except KeyError:
            pass
        res = client.complete(
            "generator",
            "dataset_rubric",
            {"question": it.question, "reference_answer": it.reference_answer},
            RubricDraft,
        )
        draft = res.value.model_dump()
        draft["question"] = it.question  # keep the corpus text exactly
        rubric = Rubric.model_validate(
            {**draft, "rubric_id": rid, "topic": it.dataset, "version": 1, "source": "dataset"}
        ).freeze()
        store.save(rubric)
        built += 1

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "config": asdict(cfg),
        "rubric_prompt_hash": prompt_hash,
        "sources": [list(s) for s in SOURCES],
        "items": [
            {"item_id": i.item_id, "rubric_id": rubric_id_for(i, prompt_hash)} for i in sample
        ],
    }
    (out_dir / "sample.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    _write_rubric_review(store, first_per_q, out_dir / "rubrics_review.md")
    return {
        "items": len(sample),
        "questions": len(first_per_q),
        "built": built,
        "reused": reused,
        "labels": dict(Counter(i.label for i in sample)),
    }


def _judge_variables(item: GradedAnswer, rubric: Rubric) -> dict[str, Any]:
    return {
        "question": item.question,
        "paths": [p.model_dump(mode="json") for p in rubric.paths],
        "answer": item.student_answer,
    }


def _grade(
    client: LLMClient,
    role: str,
    item: GradedAnswer,
    rubric: Rubric,
    *,
    fresh: bool = False,
    write_cache: bool = True,
) -> tuple[ResultRow, JudgeOutput | None]:
    assert rubric.hash is not None
    row = ResultRow(item.item_id, item.dataset, item.label, rubric.hash)
    try:
        res = client.complete(
            role,
            "path_and_score",
            _judge_variables(item, rubric),
            JudgeOutput,
            evaluation_id=f"pilot:{role}:{item.item_id}",
            fresh=fresh,
            write_cache=write_cache,
        )
    except StructuredOutputError as e:
        row.error = f"structured_output: {e}"
        return row, None
    row.call_id = res.call.call_id
    out = res.value
    try:
        lab = engine_labels(out, rubric)
    except JudgeOutputMismatch as e:
        row.error = f"mismatch: {e}"
        return row, out
    row.engine_2way, row.engine_3way = lab.two_way, lab.three_way
    row.engine_graded, row.weighted_score = lab.graded, lab.weighted_score
    row.n_errors = len(out.errors)
    row.max_path_confidence = out.max_confidence()
    return row, out


def _manifest(out_dir: Path) -> list[dict[str, str]]:
    path = out_dir / "sample.json"
    if not path.exists():
        raise FileNotFoundError("run `eval-engine pilot prepare` first")
    items: list[dict[str, str]] = json.loads(path.read_text(encoding="utf-8"))["items"]
    return items


def run(
    client: LLMClient,
    store: RubricStore,
    role: str,
    *,
    data_dir: Path = DATASET_DIR,
    out_dir: Path = PILOT_DIR,
) -> tuple[list[ResultRow], str | None]:
    """Grades all sampled items. Returns (rows, stop_reason); stop_reason is set when a quota
    or provider failure ends the run early. Rerunning resumes from the cache."""
    items = _load_items(data_dir)
    rows: list[ResultRow] = []
    stop: str | None = None
    for entry in _manifest(out_dir):
        item = items[entry["item_id"]]
        rubric = store.latest(entry["rubric_id"])
        try:
            row, _ = _grade(client, role, item, rubric)
        except QuotaExhausted as e:
            stop = f"quota: {e}"
            break
        except ProviderError as e:
            stop = f"provider: {e}"
            break
        rows.append(row)
    _write_rows(out_dir / "results" / f"{role}.jsonl", rows)
    return rows, stop


def stability(
    client: LLMClient,
    store: RubricStore,
    role: str,
    *,
    n_items: int = 50,
    repeats: int = 3,
    data_dir: Path = DATASET_DIR,
    out_dir: Path = PILOT_DIR,
) -> dict[str, Any]:
    """Reruns the first n_items `repeats` times without the cache. Uses 1 cached + (repeats-1)
    fresh calls per item, so `run` should be complete for this role first."""
    items = _load_items(data_dir)
    runs_per_item: list[list[list[bool]]] = []
    label_flips = 0
    for entry in _manifest(out_dir)[:n_items]:
        item, rubric = items[entry["item_id"]], store.latest(entry["rubric_id"])
        runs: list[list[bool]] = []
        labels: set[str | None] = set()
        for r in range(repeats):
            row, out = _grade(client, role, item, rubric, fresh=r > 0, write_cache=r == 0)
            if out is None or row.error:
                break
            by_id = {v.criterion_id: v.met for v in out.verdicts}
            sol = rubric.path(out.identified_path or rubric.paths[0].path_id)
            runs.append([by_id.get(c.criterion_id, False) for c in sol.criteria])
            labels.add(row.engine_3way)
        if len(runs) == repeats and len({len(x) for x in runs}) == 1:
            runs_per_item.append(runs)
            label_flips += len(labels) > 1
    result = {
        "role": role,
        "items": len(runs_per_item),
        "repeats": repeats,
        "criterion_flip_rate": m.flip_rate(runs_per_item),
        "label_flip_rate": label_flips / len(runs_per_item) if runs_per_item else math.nan,
    }
    path = out_dir / "results" / f"{role}.stability.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


# ---------------------------------------------------------------- report


def _write_rows(path: Path, rows: list[ResultRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(asdict(r)) + "\n")


def load_rows(path: Path) -> list[ResultRow]:
    with path.open(encoding="utf-8") as f:
        return [ResultRow(**json.loads(line)) for line in f if line.strip()]


@dataclass(frozen=True)
class JudgeMetrics:
    role: str
    scope: str
    n_scored: int
    n_total: int
    leniency: m.Estimate
    qwk: m.Estimate
    spearman: m.Estimate
    acc_2way: m.Estimate
    f1_3way: m.Estimate
    confusion_3way: dict[str, dict[str, int]]


def compute_metrics(
    role: str, rows: list[ResultRow], scope: str = "all", n_resamples: int = 1000
) -> JudgeMetrics:
    ok = [r for r in rows if r.error is None and r.engine_graded is not None]
    eg = [r.engine_graded for r in ok if r.engine_graded is not None]
    hg = [HUMAN_GRADED[r.human_label] for r in ok]
    e2 = [r.engine_2way or "" for r in ok]
    h2 = [human_2way(r.human_label) for r in ok]
    e3 = [r.engine_3way or "" for r in ok]
    h3 = [human_3way(r.human_label) for r in ok]
    confusion: dict[str, dict[str, int]] = {}
    for h, e in zip(h3, e3, strict=True):
        confusion.setdefault(h, {}).setdefault(e, 0)
        confusion[h][e] += 1
    nan = m.Estimate(math.nan, math.nan, math.nan)
    if not ok:
        return JudgeMetrics(role, scope, 0, len(rows), nan, nan, nan, nan, nan, confusion)
    return JudgeMetrics(
        role=role,
        scope=scope,
        n_scored=len(ok),
        n_total=len(rows),
        leniency=m.bootstrap(m.leniency, eg, hg, n_resamples=n_resamples),
        qwk=m.bootstrap(m.qwk, eg, hg, n_resamples=n_resamples),
        spearman=m.bootstrap(m.spearman, eg, hg, n_resamples=n_resamples),
        acc_2way=m.bootstrap(m.accuracy, e2, h2, n_resamples=n_resamples),
        f1_3way=m.bootstrap(m.macro_f1, e3, h3, n_resamples=n_resamples),
        confusion_3way=confusion,
    )


def gate(primary: JudgeMetrics, others: list[JudgeMetrics]) -> str:
    """Phase 2 exit gate for the primary judge, as written in the implementation plan."""
    if primary.n_scored == 0:
        return "NOT EVALUATED: no scored items for the primary judge."
    len_ok = abs(primary.leniency.value) <= LENIENCY_TARGET
    clearly_better = [
        o.role
        for o in others
        if o.n_scored and not math.isnan(o.qwk.value) and o.qwk.lo > primary.qwk.hi
    ]
    if len_ok and not clearly_better:
        return (
            f"PASS: |leniency| {abs(primary.leniency.value):.3f} <= {LENIENCY_TARGET} and no "
            "candidate has a QWK confidence interval entirely above the primary judge's."
        )
    reasons = []
    if not len_ok:
        reasons.append(f"|leniency| {abs(primary.leniency.value):.3f} > {LENIENCY_TARGET}")
    if clearly_better:
        reasons.append(f"clearly lower QWK than {', '.join(clearly_better)}")
    return "FAIL: " + "; ".join(reasons)


def report(
    roles: list[str],
    primary: str = "judge",
    out_dir: Path = PILOT_DIR,
    n_resamples: int = 1000,
) -> tuple[str, list[JudgeMetrics]]:
    results: list[JudgeMetrics] = []
    per_dataset: list[JudgeMetrics] = []
    stability_notes: list[str] = []
    for role in roles:
        path = out_dir / "results" / f"{role}.jsonl"
        if not path.exists():
            continue
        rows = load_rows(path)
        results.append(compute_metrics(role, rows, n_resamples=n_resamples))
        for ds, _ in SOURCES:
            subset = [r for r in rows if r.dataset == ds]
            per_dataset.append(compute_metrics(role, subset, ds, n_resamples))
        sp = out_dir / "results" / f"{role}.stability.json"
        if sp.exists():
            s = json.loads(sp.read_text(encoding="utf-8"))
            stability_notes.append(
                f"| {role} | {s['items']} | {s['repeats']} | {s['criterion_flip_rate']:.3f} | "
                f"{s['label_flip_rate']:.3f} |"
            )

    lines = [
        "# Phase 2 — Judge pilot report",
        "",
        "Generated by `eval-engine pilot report`. Corpora: SciEntsBank and Beetle "
        "(SemEval-2013 Task 7, Dzikovska et al. 2013; CC BY 4.0, via "
        "huggingface.co/datasets/nkazi), unseen-answers test splits.",
        "",
        "Scales and mapping rules are defined in `src/eval_engine/validation/labels.py` and "
        "were fixed before any judge was run. 95% bootstrap intervals in brackets.",
        "",
        "## Overall",
        "",
        "| Judge | Scored | Leniency (target ±0.1) | QWK | Spearman | 2-way acc | 3-way macro-F1 |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.role} | {r.n_scored}/{r.n_total} | {r.leniency.fmt()} | {r.qwk.fmt()} | "
            f"{r.spearman.fmt()} | {r.acc_2way.fmt()} | {r.f1_3way.fmt()} |"
        )
    lines += ["", "## By dataset", "", "| Judge | Dataset | Scored | Leniency | QWK | 2-way acc |"]
    lines.append("|---|---|---|---|---|---|")
    for r in per_dataset:
        lines.append(
            f"| {r.role} | {r.scope} | {r.n_scored}/{r.n_total} | {r.leniency.fmt()} | "
            f"{r.qwk.fmt()} | {r.acc_2way.fmt()} |"
        )
    lines += ["", "## 3-way confusion (rows: human, columns: engine)", ""]
    cols = ["correct", "contradictory", "incorrect"]
    for r in results:
        lines += [f"**{r.role}**", "", "| human \\ engine | " + " | ".join(cols) + " |"]
        lines.append("|---" * (len(cols) + 1) + "|")
        for h in cols:
            row = r.confusion_3way.get(h, {})
            lines.append(f"| {h} | " + " | ".join(str(row.get(c, 0)) for c in cols) + " |")
        lines.append("")
    if stability_notes:
        lines += [
            "## Run-to-run stability",
            "",
            "| Judge | Items | Repeats | Criterion flip rate | Label flip rate |",
            "|---|---|---|---|---|",
            *stability_notes,
            "",
        ]
    prim = next((r for r in results if r.role == primary), None)
    others = [r for r in results if r.role != primary]
    lines += ["## Gate", "", gate(prim, others) if prim else f"No results for `{primary}`.", ""]
    text = "\n".join(lines)
    (out_dir / "REPORT.md").write_text(text, encoding="utf-8")
    return text, results


def _write_rubric_review(
    store: RubricStore, first_per_q: dict[str, GradedAnswer], path: Path
) -> None:
    lines = [
        "# Rubric spot-check (Phase 2)",
        "",
        "Review at least 20. For each: are criteria binary and observable, do they capture the "
        "reference answer's key idea(s), and would a correct answer in other words pass?",
        "",
    ]
    for rid, it in sorted(first_per_q.items(), key=lambda kv: kv[1].question_key):
        try:
            r = store.latest(rid)
        except KeyError:
            continue
        lines += [
            f"## {it.dataset}: {it.question}",
            "",
            f"*Reference:* {it.reference_answer}",
            "",
        ]
        for c in r.paths[0].criteria:
            core = "core" if c.core else "non-core"
            lines.append(f"- [ ] **{c.criterion_id}** ({c.dimension}, {core}): {c.statement}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
