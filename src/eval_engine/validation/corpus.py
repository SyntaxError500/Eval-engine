"""Phase 7 task 1: the Phase 2 held-out sample through the full engine.

Phase 2 validated the judge alone (`path_and_score` v1). Here the same 302 answers, rubrics and
human labels go through `evaluate`: the production judge prompt (`score_answer` v2), the code
checks (unsupported evidence, met-on-a-flagged-error, sentence counts) and aggregation. Every
rubric is a factual checklist, so amendment can't run. Each answer is also scored from the
judge's raw reply before the code checks, which separates what the prompt changed from what
the checks changed. Labels use the Phase 2 mapping (`labels.py`), so the three are comparable.
"""

import json
import sqlite3
from collections.abc import Callable
from dataclasses import asdict
from functools import partial
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.base import QuotaExhausted
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.judge import JudgeOutput, ScoredAnswer
from eval_engine.schemas.question import Question
from eval_engine.schemas.rubric import Rubric
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore, connect
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import pilot
from eval_engine.validation.datasets import DATASET_DIR
from eval_engine.validation.labels import EngineLabels, JudgeOutputMismatch, engine_labels

PHASE2_DIR = pilot.PILOT_DIR / "test_v3"  # the final Phase 2 run (rubric prompt v3)
CORPUS_DIR = REPO_ROOT / "experiments" / "7_validation" / "corpus"
RUNS = ("phase2_judge", "engine_judge_only", "engine_full")


def trace_labels(trace: EvaluationTrace, rubric: Rubric) -> EngineLabels:
    """The Phase 2 mapping applied to the engine's final verdicts (after the code checks)."""
    output = JudgeOutput(
        identified_path=trace.identified_path,
        path_confidences=trace.path_confidences,
        verdicts=trace.verdicts,
        errors=trace.errors,
    )
    return engine_labels(output, rubric)


def run(
    client: LLMClient,
    conn: sqlite3.Connection,
    out_dir: Path = CORPUS_DIR,
    data_dir: Path = DATASET_DIR,
) -> tuple[dict[str, list[pilot.ResultRow]], str | None]:
    """Grade every sample answer with the full engine. Resumable: judge replies are cached."""
    items = pilot._load_items(data_dir, "test_ua")
    real_rubrics = RubricStore(conn)
    scratch = connect(":memory:")  # dataset questions never enter the real question store
    rubrics, questions, evals = (
        RubricStore(scratch),
        QuestionStore(scratch),
        EvaluationStore(scratch),
    )
    judge_only: list[pilot.ResultRow] = []
    full: list[pilot.ResultRow] = []
    traces: list[dict[str, Any]] = []
    added: set[str] = set()
    stopped = None
    for entry in pilot._manifest(PHASE2_DIR):
        item = items[entry["item_id"]]
        rubric = real_rubrics.latest(entry["rubric_id"])
        assert rubric.hash is not None
        if rubric.rubric_id not in added:
            added.add(rubric.rubric_id)
            rubrics.save(rubric)
            questions.save(
                Question(
                    question_id=rubric.rubric_id,
                    topic=item.dataset,
                    text=item.question,
                    task_type=rubric.task_type,
                    rubric_id=rubric.rubric_id,
                    rubric_hash=rubric.hash,
                )
            )
        try:
            t = evaluate(
                client,
                rubrics,
                questions,
                evals,
                rubric.rubric_id,
                item.student_answer,
                amend=False,
            )
        except QuotaExhausted as e:
            stopped = str(e)
            break
        base = {"item_id": item.item_id, "dataset": item.dataset, "human_label": item.label}
        raw = ScoredAnswer.model_validate_json(_reply(conn, t.call_ids[0]))
        judge_only.append(_row(base, rubric, partial(engine_labels, raw, rubric), raw))
        full.append(_row(base, rubric, partial(trace_labels, t, rubric), raw))
        traces.append({"item_id": item.item_id, "trace": json.loads(t.model_dump_json())})
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("engine_judge_only", judge_only), ("engine_full", full)):
        (out_dir / f"{name}.jsonl").write_text(
            "".join(json.dumps(asdict(r)) + "\n" for r in rows), encoding="utf-8"
        )
    (out_dir / "traces.json").write_text(json.dumps(traces), encoding="utf-8")
    phase2 = pilot.load_rows(PHASE2_DIR / "results" / "judge.jsonl")
    return {"phase2_judge": phase2, "engine_judge_only": judge_only, "engine_full": full}, stopped


def _row(
    base: dict[str, Any],
    rubric: Rubric,
    label: Callable[[], EngineLabels],
    raw: ScoredAnswer,
) -> pilot.ResultRow:
    assert rubric.hash is not None
    row = pilot.ResultRow(base["item_id"], base["dataset"], base["human_label"], rubric.hash)
    try:
        lab = label()
    except JudgeOutputMismatch as e:
        row.error = f"mismatch: {e}"
        return row
    row.engine_2way, row.engine_3way = lab.two_way, lab.three_way
    row.engine_graded, row.weighted_score = lab.graded, lab.weighted_score
    row.n_errors = len(raw.errors)
    row.max_path_confidence = raw.max_confidence()
    return row


def _reply(conn: sqlite3.Connection, call_id: str) -> str:
    row = conn.execute(
        "SELECT rc.text FROM llm_calls c JOIN response_cache rc ON rc.request_key = c.request_key"
        " WHERE c.call_id = ?",
        (call_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"no cached judge reply for call {call_id}")
    return str(row[0])


def load(out_dir: Path = CORPUS_DIR) -> dict[str, list[pilot.ResultRow]]:
    runs = {"phase2_judge": pilot.load_rows(PHASE2_DIR / "results" / "judge.jsonl")}
    for name in RUNS[1:]:
        runs[name] = pilot.load_rows(out_dir / f"{name}.jsonl")
    return runs


def report(runs: dict[str, list[pilot.ResultRow]]) -> str:
    lines = [
        "| Run | n | Leniency [95% CI] | QWK | Spearman | 2-way acc | 3-way macro-F1 |",
        "|---|---|---|---|---|---|---|",
    ]
    for name in RUNS:
        for scope, rows in [("all", runs[name])] + [
            (d, [r for r in runs[name] if r.dataset == d]) for d in pilot.DATASETS
        ]:
            mx = pilot.compute_metrics(name, rows, scope=scope)
            lines.append(
                f"| {name} ({scope}) | {mx.n_scored}/{mx.n_total} | {_est(mx.leniency)} | "
                f"{_est(mx.qwk)} | {_est(mx.spearman)} | {_est(mx.acc_2way, pct=True)} | "
                f"{_est(mx.f1_3way)} |"
            )
    lines += ["", "Label changes from engine_judge_only to engine_full (the code checks):", ""]
    before = {r.item_id: r for r in runs["engine_judge_only"]}
    moved: dict[str, int] = {}
    for r in runs["engine_full"]:
        b = before.get(r.item_id)
        if b and b.engine_graded != r.engine_graded:
            key = f"{b.engine_graded} -> {r.engine_graded} (human {r.human_label})"
            moved[key] = moved.get(key, 0) + 1
    lines += [f"- {k}: {n}" for k, n in sorted(moved.items())] or ["- none"]
    return "\n".join(lines)


def _est(e: Any, pct: bool = False) -> str:
    if pct:
        return f"{e.value:.1%} [{e.lo:.1%}, {e.hi:.1%}]"
    return f"{e.value:+.3f} [{e.lo:+.3f}, {e.hi:+.3f}]"
