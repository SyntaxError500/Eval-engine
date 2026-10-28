import math

import pytest

from eval_engine.schemas import JudgeOutput
from eval_engine.validation import metrics as m
from eval_engine.validation.labels import (
    JudgeOutputMismatch,
    engine_labels,
    human_2way,
    human_3way,
)
from tests.conftest import make_rubric


def judge(met: dict[str, bool], path: str = "P1", errors: int = 0) -> JudgeOutput:
    return JudgeOutput.model_validate(
        {
            "identified_path": path,
            "path_confidences": [{"path_id": path, "confidence": 0.9}],
            "verdicts": [
                {"criterion_id": k, "met": v, "evidence": "", "justification": ""}
                for k, v in met.items()
            ],
            "errors": [{"quote": "x", "explanation": "wrong"}] * errors,
        }
    )


# P1.C1 is core (weight 1), P1.C2 non-core (weight 0.5)
@pytest.mark.parametrize(
    ("met", "errors", "expected"),
    [
        ({"P1.C1": True, "P1.C2": False}, 0, ("correct", "correct", 1.0)),
        ({"P1.C1": False, "P1.C2": True}, 0, ("incorrect", "incorrect", 0.5)),
        ({"P1.C1": False, "P1.C2": False}, 0, ("incorrect", "incorrect", 0.0)),
        ({"P1.C1": True, "P1.C2": True}, 1, ("incorrect", "contradictory", 0.0)),
    ],
)
def test_engine_labels(met: dict[str, bool], errors: int, expected: tuple[str, str, float]) -> None:
    lab = engine_labels(judge(met, errors=errors), make_rubric())
    assert (lab.two_way, lab.three_way, lab.graded) == expected


def test_weighted_score() -> None:
    lab = engine_labels(judge({"P1.C1": False, "P1.C2": True}), make_rubric())
    assert lab.weighted_score == pytest.approx(0.5 / 1.5)


def test_missing_verdict_is_mismatch() -> None:
    with pytest.raises(JudgeOutputMismatch, match="no verdict"):
        engine_labels(judge({"P1.C1": True}), make_rubric())


def test_unknown_path_is_mismatch() -> None:
    with pytest.raises(JudgeOutputMismatch, match="unknown path"):
        engine_labels(judge({"P9.C1": True}, path="P9"), make_rubric())


def test_human_label_collapsing() -> None:
    assert [human_3way(x) for x in ("correct", "contradictory", "irrelevant")] == [
        "correct",
        "contradictory",
        "incorrect",
    ]
    assert human_2way("partially_correct_incomplete") == "incorrect"


def test_leniency_sign() -> None:
    assert m.leniency([1.0, 1.0], [0.5, 0.5]) == pytest.approx(0.5)
    assert m.leniency([0.0], [1.0]) == pytest.approx(-1.0)


def test_qwk_perfect_and_nan() -> None:
    assert m.qwk([0.0, 0.5, 1.0], [0.0, 0.5, 1.0]) == pytest.approx(1.0)
    assert math.isnan(m.qwk([1.0, 1.0], [1.0, 1.0]))


def test_constant_offset_correlates_but_shows_leniency() -> None:
    # The reason both metrics are reported: a uniformly harsh grader still correlates.
    human = [0.5, 1.0, 0.5, 1.0]
    engine = [0.0, 0.5, 0.0, 0.5]
    assert m.spearman(engine, human) == pytest.approx(1.0)
    assert m.leniency(engine, human) == pytest.approx(-0.5)


def test_bootstrap_interval_contains_point() -> None:
    e = [1.0, 0.5, 0.0, 1.0, 0.5, 1.0, 0.0, 0.5]
    h = [1.0, 0.5, 0.5, 1.0, 0.0, 1.0, 0.0, 0.5]
    est = m.bootstrap(m.leniency, e, h, n_resamples=300)
    assert est.lo <= est.value <= est.hi


def test_flip_rate() -> None:
    stable = [[[True, False], [True, False], [True, False]]]
    flipping = [[[True, False], [False, False], [True, False]]]
    assert m.flip_rate(stable) == 0.0
    assert m.flip_rate(flipping) == pytest.approx(0.5)
