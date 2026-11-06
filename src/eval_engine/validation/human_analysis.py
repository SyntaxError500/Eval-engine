"""Phase 7 task 3 analysis, pre-registered (senior review step 5): written and committed before any
human grade exists, so the results can't shape it.

Order and rules, fixed now:
1. Validate both grade files: every answer and item present, marks in range.
2. Inter-rater agreement, first: Cohen's kappa pooled over all requirement marks, on the
   false-statement flag, and quadratic-weighted kappa on the 3-level overall label. If the overall
   kappa is below STOP_KAPPA, stop and report only that. Low agreement means the sheet is the
   problem, and engine numbers against it would mean little.
3. Engine against humans. The engine side is the majority of 3 judge v3 calls per answer, mapped
   with the Phase 2 label mapping (`labels.py`).
   - Leniency and Spearman are against the mean of the two graders (0, 0.25, ..., 1), so no
     adjudication is needed.
   - QWK is against each grader separately, because it needs the 3-level scale.
4. Intervals: a cluster bootstrap by question, because answers are uneven across questions (12 on
   the hot-air balloon).
5. Gate: absolute leniency at most 0.1, the same as the corpus.
6. Band calibration (plan task 5) uses adjudicated requirement marks: met only if both graders mark
   Y (disagreement goes to the stricter mark). Human dimension scores are aggregated exactly as the
   engine's are, and per-dimension bands are compared.
"""

import csv
import json
import random
import sqlite3
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sklearn.metrics import cohen_kappa_score

from eval_engine.evaluation.aggregate import dimension_scores, load_bands
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.rubric import Criterion
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import metrics as m
from eval_engine.validation import perturb
from eval_engine.validation.corpus import trace_labels
from eval_engine.validation.human_set import HUMAN_DIR, OVERALL

STOP_KAPPA = 0.6
LENIENCY_TARGET = 0.1
VOTES = 3
N_BOOT = 2000
SEED = 13
GRADED = {"correct": 1.0, "partially_correct": 0.5, "incorrect": 0.0}
GRADES_DIR = HUMAN_DIR / "grades"  # graders' returned CSVs: grader1.csv, grader2.csv


@dataclass
class Grades:
    marks: dict[str, dict[str, str]]  # answer_id -> item -> mark


def load_grades(path: Path, expected: dict[str, list[str]], partial: bool = False) -> Grades:
    """Read one grader's CSV and check it against the sheet. `partial` allows missing answers
    (a dry run of a few rows); a present answer must still be complete and in range."""
    marks: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            mark = (row.get("mark") or "").strip().lower()
            if mark:
                marks.setdefault(row["answer_id"].strip(), {})[row["item"].strip()] = mark
    problems = []
    for answer_id, items in expected.items():
        got = marks.get(answer_id)
        if got is None:
            if not partial:
                problems.append(f"{answer_id}: not graded")
            continue
        for item in items:
            mark = got.get(item)
            allowed = OVERALL if item == "overall" else ("y", "n")
            if mark not in allowed:
                problems.append(f"{answer_id} {item}: {mark!r} is not one of {list(allowed)}")
    unknown = sorted(set(marks) - set(expected))
    problems += [f"{a}: not an answer on the sheet" for a in unknown]
    if problems:
        raise ValueError(f"{path.name}: " + "; ".join(problems[:20]))
    return Grades(marks)


def expected_items(conn: sqlite3.Connection, out_dir: Path = HUMAN_DIR) -> dict[str, list[str]]:
    questions, rubrics = QuestionStore(conn), RubricStore(conn)
    out = {}
    for a in json.loads((out_dir / "key.json").read_text(encoding="utf-8")):
        q = questions.get(a["question_id"])
        criteria = [c.criterion_id for c in rubrics.get(q.rubric_hash).paths[0].criteria]
        out[a["answer_id"]] = [*criteria, "false_statement", "overall"]
    return out


def agreement(g1: Grades, g2: Grades, expected: dict[str, list[str]]) -> dict[str, Any]:
    req1, req2, fs1, fs2, ov1, ov2 = [], [], [], [], [], []
    for answer_id, items in expected.items():
        a, b = g1.marks[answer_id], g2.marks[answer_id]
        for item in items:
            if item == "false_statement":
                fs1.append(a[item])
                fs2.append(b[item])
            elif item == "overall":
                ov1.append(OVERALL.index(a[item]))
                ov2.append(OVERALL.index(b[item]))
            else:
                req1.append(a[item])
                req2.append(b[item])
    return {
        "requirements_kappa": _kappa(req1, req2),
        "requirements_agree": _agree(req1, req2),
        "false_statement_kappa": _kappa(fs1, fs2),
        "overall_weighted_kappa": _kappa(ov1, ov2, weights="quadratic"),
        "overall_agree": _agree(ov1, ov2),
        "n_answers": len(expected),
    }


def _kappa(a: Sequence[Any], b: Sequence[Any], weights: str | None = None) -> float:
    if len(set(a) | set(b)) < 2:
        return float("nan")
    return float(cohen_kappa_score(a, b, weights=weights))


def _agree(a: Sequence[Any], b: Sequence[Any]) -> float:
    same = sum(1 for x, y in zip(a, b, strict=True) if x == y)
    return same / len(a)


def engine_scores(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = HUMAN_DIR
) -> dict[str, dict[str, Any]]:
    """Majority-of-3 v3 judgements for every answer, cached to `engine_maj3.json`."""
    path = out_dir / "engine_maj3.json"
    done: dict[str, dict[str, Any]] = (
        json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    )
    rubrics = RubricStore(conn)
    questions = QuestionStore(conn)
    for a in json.loads((out_dir / "key.json").read_text(encoding="utf-8")):
        if a["answer_id"] in done:
            continue
        store_r, store_q, store_e = perturb._scratch(conn, a["question_id"])
        t = evaluate(
            client, store_r, store_q, store_e, a["question_id"], a["text"],
            votes=VOTES, vote_all=True, amend=False,
        )  # fmt: skip
        rubric = rubrics.get(questions.get(a["question_id"]).rubric_hash)
        lab = trace_labels(t, rubric)
        done[a["answer_id"]] = {
            "graded": lab.graded,
            "trace": json.loads(t.model_dump_json()),
        }
        path.write_text(json.dumps(done, indent=1), encoding="utf-8")
    return done


def cluster_bootstrap(
    stat: Callable[[list[str]], float], clusters: list[str], n: int = N_BOOT, seed: int = SEED
) -> tuple[float, float, float]:
    """`stat` takes a resampled list of cluster ids (with repeats) and returns the statistic."""
    rng = random.Random(seed)
    point = stat(clusters)
    draws = sorted(
        v for v in (stat([rng.choice(clusters) for _ in clusters]) for _ in range(n)) if v == v
    )
    if not draws:
        return point, float("nan"), float("nan")
    return point, draws[int(0.025 * len(draws))], draws[int(0.975 * len(draws)) - 1]


def analyse(
    key: list[dict[str, Any]],
    g1: Grades,
    g2: Grades,
    expected: dict[str, list[str]],
    engine: dict[str, dict[str, Any]],
    criteria: dict[str, list[Criterion]],
) -> tuple[str, dict[str, Any]]:
    """Pure: grades, engine scores and each used rubric path's criteria (by rubric hash) in;
    report text and figures out."""
    agree = agreement(g1, g2, expected)
    lines = [
        "# Human-graded set: results",
        "",
        "Pre-registered in `src/eval_engine/validation/human_analysis.py` before any grade "
        "arrived.",
        "",
        "## 1. Inter-rater agreement",
        "",
        f"- Requirements: kappa {agree['requirements_kappa']:.3f}, raw agreement "
        f"{agree['requirements_agree']:.1%}.",
        f"- False-statement flag: kappa {agree['false_statement_kappa']:.3f}.",
        f"- Overall label: quadratic-weighted kappa {agree['overall_weighted_kappa']:.3f}, raw "
        f"agreement {agree['overall_agree']:.1%}.",
    ]
    out: dict[str, Any] = {"agreement": agree}
    if not agree["overall_weighted_kappa"] >= STOP_KAPPA:
        lines += [
            "",
            f"**STOP: overall-label kappa is below {STOP_KAPPA}.** The sheet is the problem; "
            "engine figures against these grades are not reported.",
        ]
        out["stopped"] = True
        return "\n".join(lines), out

    by_q: dict[str, list[str]] = {}
    for a in key:
        by_q.setdefault(a["question_id"], []).append(a["answer_id"])
    human = {
        a: (GRADED[g1.marks[a]["overall"]] + GRADED[g2.marks[a]["overall"]]) / 2 for a in expected
    }
    eng = {a: float(engine[a]["graded"]) for a in expected}

    def ids(qs: list[str]) -> list[str]:
        return [a for q in qs for a in by_q[q]]

    clusters = sorted(by_q)
    len_est = cluster_bootstrap(
        lambda qs: m.leniency([eng[a] for a in ids(qs)], [human[a] for a in ids(qs)]), clusters
    )
    sp_est = cluster_bootstrap(
        lambda qs: m.spearman([eng[a] for a in ids(qs)], [human[a] for a in ids(qs)]), clusters
    )

    def qwk_against(g: Grades) -> Callable[[list[str]], float]:
        def stat(qs: list[str]) -> float:
            labels = [GRADED[g.marks[a]["overall"]] for a in ids(qs)]
            return m.qwk([eng[a] for a in ids(qs)], labels)

        return stat

    qwks = {
        "grader1": cluster_bootstrap(qwk_against(g1), clusters),
        "grader2": cluster_bootstrap(qwk_against(g2), clusters),
    }
    passed = abs(len_est[0]) <= LENIENCY_TARGET
    out.update({"leniency": len_est, "spearman": sp_est, "qwk": qwks, "gate_passed": passed})
    lines += [
        "",
        "## 2. Engine (judge v3, majority of 3) against the graders",
        "",
        f"95% intervals: cluster bootstrap over {len(clusters)} questions, {N_BOOT} resamples.",
        "",
        "| Measure | Value [95% CI] |",
        "|---|---|",
        f"| Leniency vs mean of graders | {_fmt(len_est)} |",
        f"| Spearman vs mean of graders | {_fmt(sp_est)} |",
        f"| QWK vs grader 1 | {_fmt(qwks['grader1'])} |",
        f"| QWK vs grader 2 | {_fmt(qwks['grader2'])} |",
        "",
        f"Gate (absolute leniency at most {LENIENCY_TARGET}): {'PASS' if passed else 'FAIL'}",
        "",
        "Engine full marks where both graders gave less:",
        "",
    ]
    lines += [
        f"- {a} ({next(k['source'] for k in key if k['answer_id'] == a)}): graders "
        f"{g1.marks[a]['overall']} / {g2.marks[a]['overall']}"
        for a in expected
        if eng[a] == 1.0 and human[a] < 1.0
    ] or ["- none"]
    lines += [
        "",
        "## 3. Bands (task 5), against adjudicated requirement marks",
        "",
        *_bands(key, g1, g2, expected, engine, criteria),
    ]
    return "\n".join(lines), out


def _bands(
    key: list[dict[str, Any]],
    g1: Grades,
    g2: Grades,
    expected: dict[str, list[str]],
    engine: dict[str, dict[str, Any]],
    criteria: dict[str, list[Criterion]],
) -> list[str]:
    bands = load_bands()
    same = total = 0
    gaps: list[float] = []
    for a in key:
        t = EvaluationTrace.model_validate(engine[a["answer_id"]]["trace"])
        rubric_criteria = {v.criterion_id for v in t.verdicts}
        human_verdicts = [
            v.model_copy(
                update={
                    "met": g1.marks[a["answer_id"]][v.criterion_id] == "y"
                    and g2.marks[a["answer_id"]][v.criterion_id] == "y"
                }
            )
            for v in t.verdicts
            if v.criterion_id in rubric_criteria and v.criterion_id in expected[a["answer_id"]]
        ]
        both_false = (
            g1.marks[a["answer_id"]]["false_statement"] == "y"
            and g2.marks[a["answer_id"]]["false_statement"] == "y"
        )
        hs = dimension_scores(
            criteria[t.rubric_hash_used],
            human_verdicts,
            n_errors=int(both_false),
            task_type=t.task_type,
        )
        for d, s in t.dimension_scores.items():
            if d in hs:
                total += 1
                same += bands.label(s) == bands.label(hs[d])
                gaps.append(abs(s - hs[d]))
    if not total:
        return ["- no comparable dimension scores"]
    return [
        f"- Same band: {same}/{total} dimension scores ({same / total:.0%}).",
        f"- Mean absolute score gap: {sum(gaps) / len(gaps):.3f}.",
    ]


def criteria_by_hash(
    conn: sqlite3.Connection, engine: dict[str, dict[str, Any]]
) -> dict[str, list[Criterion]]:
    """The criteria of the path each engine judgement used (all rubrics here are single-path)."""
    rubrics = RubricStore(conn)
    out = {}
    for entry in engine.values():
        t = EvaluationTrace.model_validate(entry["trace"])
        rubric = rubrics.get(t.rubric_hash_used)
        path = rubric.path(t.identified_path) if t.identified_path else rubric.paths[0]
        out[t.rubric_hash_used] = list(path.criteria)
    return out


def _fmt(e: tuple[float, float, float]) -> str:
    return f"{e[0]:+.3f} [{e[1]:+.3f}, {e[2]:+.3f}]"
