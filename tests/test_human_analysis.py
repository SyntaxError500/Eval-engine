"""Phase 7 human-set analysis, end to end on dummy grades (no network, no real grades)."""

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from eval_engine.schemas import Criterion, Dimension, TaskType, Verdict
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.validation import human_analysis as ha

CRITERIA = [
    Criterion(criterion_id=f"P1.C{i}", dimension=Dimension.CORRECTNESS, statement=f"s{i}",
              evidence_hint="", core=True, weight=1.0)
    for i in (1, 2)
]  # fmt: skip
EXPECTED = {f"A{n:02d}": ["P1.C1", "P1.C2", "false_statement", "overall"] for n in range(1, 7)}
KEY = [
    {"answer_id": a, "question_id": f"q{(n % 3) + 1}", "source": f"src{n}", "text": "t"}
    for n, a in enumerate(EXPECTED)
]
OVERALL = ["correct", "partially_correct", "incorrect", "correct", "incorrect", "partially_correct"]


def write(path: Path, marks: dict[str, dict[str, str]]) -> Path:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["answer_id", "item", "mark"])
        w.writeheader()
        for a, items in marks.items():
            for item, mark in items.items():
                w.writerow({"answer_id": a, "item": item, "mark": mark})
    return path


def marks(overall: list[str]) -> dict[str, dict[str, str]]:
    out = {}
    for a, label in zip(EXPECTED, overall, strict=True):
        met = "Y" if label == "correct" else "n"
        out[a] = {"P1.C1": met, "P1.C2": "y", "false_statement": "N", "overall": label}
    return out


def trace(met: bool) -> EvaluationTrace:
    return EvaluationTrace(
        evaluation_id="e", timestamp=datetime.now(UTC), question_id="q", task_type=TaskType.FACTUAL,
        rubric_hash_original="h", rubric_hash_used="h", creative_route=False,
        final_rubric_source="generated", identified_path="P1",
        verdicts=[Verdict(criterion_id=c.criterion_id, met=met, evidence="", justification="j")
                  for c in CRITERIA],
        dimension_scores={Dimension.CORRECTNESS: 1.0 if met else 0.0},
    )  # fmt: skip


def engine(graded: list[float]) -> dict[str, dict[str, Any]]:
    return {
        a: {"graded": g, "trace": json.loads(trace(g == 1.0).model_dump_json())}
        for a, g in zip(EXPECTED, graded, strict=True)
    }


def test_grades_are_validated_against_the_sheet(tmp_path: Path) -> None:
    good = marks(OVERALL)
    ha.load_grades(write(tmp_path / "ok.csv", good), EXPECTED)
    bad = {**good, "A02": {**good["A02"], "overall": "mostly right"}}
    with pytest.raises(ValueError, match="A02 overall"):
        ha.load_grades(write(tmp_path / "bad.csv", bad), EXPECTED)
    partial = {"A01": good["A01"]}
    ha.load_grades(write(tmp_path / "part.csv", partial), EXPECTED, partial=True)
    with pytest.raises(ValueError, match="A03: not graded"):
        ha.load_grades(write(tmp_path / "part2.csv", partial), EXPECTED)


def test_low_agreement_stops_before_any_engine_figure(tmp_path: Path) -> None:
    g1 = ha.load_grades(write(tmp_path / "1.csv", marks(OVERALL)), EXPECTED)
    flipped = ["incorrect", "correct", "correct", "incorrect", "correct", "incorrect"]
    g2 = ha.load_grades(write(tmp_path / "2.csv", marks(flipped)), EXPECTED)
    text, out = ha.analyse(KEY, g1, g2, EXPECTED, engine([1.0] * 6), {"h": CRITERIA})
    assert out["stopped"] and "STOP" in text and "Leniency" not in text


def test_full_analysis_on_agreeing_graders(tmp_path: Path) -> None:
    g1 = ha.load_grades(write(tmp_path / "1.csv", marks(OVERALL)), EXPECTED)
    g2 = ha.load_grades(write(tmp_path / "2.csv", marks(OVERALL)), EXPECTED)
    graded = [1.0, 0.5, 0.0, 1.0, 0.0, 0.5]  # the engine matches the graders exactly
    text, out = ha.analyse(KEY, g1, g2, EXPECTED, engine(graded), {"h": CRITERIA})
    assert out["agreement"]["overall_weighted_kappa"] == pytest.approx(1.0)
    assert out["leniency"][0] == pytest.approx(0.0) and out["gate_passed"]
    assert out["qwk"]["grader1"][0] == pytest.approx(1.0)
    assert "cluster bootstrap over 3 questions" in text and "Same band" in text


def test_cluster_bootstrap_resamples_questions_not_answers() -> None:
    seen: list[list[str]] = []

    def stat(qs: list[str]) -> float:
        seen.append(qs)
        return float(len(qs))

    point, lo, hi = ha.cluster_bootstrap(stat, ["q1", "q2", "q3"], n=50)
    assert point == lo == hi == 3.0  # always as many clusters as there are questions
    assert all(set(s) <= {"q1", "q2", "q3"} for s in seen[1:])
