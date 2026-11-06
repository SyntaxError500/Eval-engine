"""Phase 7: label mapping on engine traces, perturbation checks and metrics (no network)."""

from datetime import UTC, datetime
from typing import Any

import pytest

from eval_engine.schemas import TaskType, Verdict
from eval_engine.schemas.judge import ClaimError, PathConfidence
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.validation import perturb
from eval_engine.validation.corpus import trace_labels
from tests.conftest import make_rubric


def trace(met: dict[str, bool], errors: int = 0, path: str = "P1") -> EvaluationTrace:
    return EvaluationTrace(
        evaluation_id="e",
        timestamp=datetime.now(UTC),
        question_id="q",
        task_type=TaskType.ANALYTICAL,
        rubric_hash_original="h",
        rubric_hash_used="h",
        creative_route=False,
        final_rubric_source="generated",
        identified_path=path,
        path_confidences=[PathConfidence(path_id=path, confidence=0.9)],
        verdicts=[
            Verdict(criterion_id=c, met=m, evidence="", justification="j") for c, m in met.items()
        ],
        errors=[ClaimError(quote="x", explanation="y")] * errors,
    )


@pytest.mark.parametrize(
    ("met", "errors", "expected"),
    [
        ({"P1.C1": True, "P1.C2": False}, 0, ("correct", 1.0)),  # every core criterion met
        ({"P1.C1": False, "P1.C2": True}, 0, ("incorrect", 0.5)),  # partial credit
        ({"P1.C1": False, "P1.C2": False}, 0, ("incorrect", 0.0)),
        ({"P1.C1": True, "P1.C2": True}, 1, ("contradictory", 0.0)),  # any listed error
    ],
)
def test_trace_labels_use_the_phase2_mapping_on_final_verdicts(
    met: dict[str, bool], errors: int, expected: tuple[str, float]
) -> None:
    lab = trace_labels(trace(met, errors), make_rubric())
    assert (lab.three_way, lab.graded) == expected


@pytest.mark.parametrize(
    ("drops", "winner"),
    [
        ({"correctness": 0.5, "reasoning": 0.2}, "correctness"),
        ({"correctness": 0.5, "reasoning": 0.5}, "tie"),
        ({"correctness": 0.0, "reasoning": -0.1}, "none"),
        ({}, "none"),
    ],
)
def test_attribution_is_the_unique_largest_drop(drops: dict[str, float], winner: str) -> None:
    assert perturb.attributed(drops) == winner


GOOD = (
    "Heating the air inside the balloon makes it expand and become less dense than the cooler "
    "air outside. Because it is lighter than the air it displaces, buoyancy pushes it upward."
)


@pytest.mark.parametrize(
    ("kind", "edited", "problem"),
    [
        ("completeness", GOOD, "unchanged"),
        ("completeness", GOOD + " Extra words added here.", "nothing was deleted"),
        ("completeness", GOOD.split(". ")[1], None),
        ("correctness", GOOD.replace("less dense", "denser"), None),
        ("correctness", "Balloons rise.", "change only the named part"),
        ("expression", "Unrelated text about something else entirely here now.", "content words"),
        ("expression", GOOD.lower().replace("because", "becuase"), None),
    ],
)
def test_perturbation_guards(kind: str, edited: str, problem: str | None) -> None:
    found = perturb._checks(GOOD, edited, kind)
    assert (found == []) if problem is None else (found and problem in found[0])


def row(kind: str, drops: dict[str, float]) -> dict[str, Any]:
    return {"item_id": f"b/{kind}", "kind": kind, "drops": drops, "errors": 0}


def test_report_counts_detection_attribution_and_specificity() -> None:
    rows = [
        row("correctness", {"correctness": 0.5, "reasoning": 0.0}),  # detected and attributed
        row("reasoning", {"correctness": 0.5, "reasoning": 0.5}),  # detected, tie: not attributed
        row("completeness", {"completeness": 0.0, "correctness": 0.0}),  # missed
        row("expression", {"correctness": 0.0, "reasoning": 0.0}),  # unmoved: good
        row("expression", {"correctness": 0.5}),  # a content score moved
    ]
    text, s = perturb.report(rows)
    assert s["correctness"] == {"n": 1, "detected": 1, "attributed": 1}
    assert s["reasoning"] == {"n": 1, "detected": 1, "attributed": 0}
    assert s["overall"] == {"n": 3, "attributed": 1} and not s["gate_passed"]
    assert s["expression_unmoved"] == {"n": 2, "unmoved": 1}
    assert "| reasoning | 0 | 0 | 0 | 1 | 0 |" in text  # the tie column
