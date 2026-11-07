"""The tutor's code checks and the re-check's rules (`eval_engine.tutor`), on the live Java case
that exposed the repetition, and on partial-credit cases. No network."""

from datetime import UTC, datetime

import pytest

from eval_engine.evaluation.aggregate import load_bands
from eval_engine.schemas import Criterion, Dimension, TaskType
from eval_engine.schemas.feedback import (
    CriterionRecheck,
    ErrorRecheck,
    RecheckOutput,
)
from eval_engine.schemas.judge import ClaimError, Verdict
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.tutor import (
    NO_ERRORS_CHECK,
    apply_recheck,
    grade_breakdown,
    repeat_of,
    reply_problems,
    settled_points,
)

JAVA_ANSWER = (
    "Method overriding in Java happens when a child class defines a method with the same name "
    "as the parent class but can have different parameters. It allows the child class to "
    "provide its own implementation of the method. This supports polymorphism because the same "
    "method call can behave differently depending on which object is used. For example, a "
    "parent class reference can call the overridden method of a child class. It makes code more "
    "flexible and reusable."
)
WRONG = (
    "Method overriding in Java happens when a child class defines a method with the same name "
    "as the parent class but can have different parameters."
)


def crit(cid: str, dim: str, statement: str) -> Criterion:
    return Criterion(
        criterion_id=cid,
        dimension=Dimension(dim),
        statement=statement,
        evidence_hint="",
        core=True,
        weight=1.0,
    )


JAVA_CRITERIA = [
    crit(
        "P1.C1",
        "correctness",
        "States that a subclass can provide its own implementation of a method declared in a "
        "superclass with the same signature",
    ),
    crit(
        "P1.C2",
        "completeness",
        "Notes that the overriding method must have the same return type (or a covariant "
        "type) and cannot be more restrictive in access level",
    ),
    crit(
        "P1.C3",
        "reasoning",
        "Explains that a superclass reference can invoke the overridden method, causing the "
        "subclass version to execute at runtime",
    ),
]


def java_trace(c1: bool = False, errors: int = 1) -> EvaluationTrace:
    """The live Java evaluation (2026-11-07), with the judge's own verdicts."""
    bands = load_bands()
    verdicts = [
        Verdict(criterion_id="P1.C1", met=c1, evidence="", justification="different parameters"),
        Verdict(criterion_id="P1.C2", met=False, evidence="", justification="no return types"),
        Verdict(
            criterion_id="P1.C3",
            met=True,
            evidence="a parent class reference can call the overridden method of a child class",
            justification="links the parent reference to the child method",
        ),
    ]
    errs = [ClaimError(quote=WRONG, explanation="overriding needs the same parameters")] * errors
    from eval_engine.evaluation.aggregate import dimension_scores

    scores = dimension_scores(
        JAVA_CRITERIA, verdicts, n_errors=len(errs), task_type=TaskType.EXPLANATORY
    )
    return EvaluationTrace(
        evaluation_id="e1",
        timestamp=datetime.now(UTC),
        question_id="q",
        task_type=TaskType.EXPLANATORY,
        rubric_hash_original="h",
        rubric_hash_used="h",
        creative_route=False,
        identified_path="P1",
        final_rubric_source="generated",
        verdicts=verdicts,
        errors=errs,
        dimension_scores=scores,
        bands={d: bands.label(s) for d, s in scores.items()},
    )


def recheck(*criteria: CriterionRecheck, errors: list[ErrorRecheck] | None = None) -> RecheckOutput:
    return RecheckOutput(
        criteria=list(criteria),
        errors=errors or [],
        correct_parts=["own implementation", "superclass reference, runtime dispatch"],
        incorrect_statement=WRONG,
        severity="significant",
        summary="s",
    )


# ------------------------------------------------------------------ what the tutor is told


def test_the_tutor_is_told_one_error_failed_two_correctness_checks() -> None:
    """The live case: correctness 'Not yet' came from the bundled criterion and the code's
    no-wrong-statements check failing on the same sentence. The tutor must be able to say so."""
    dims = {d["name"]: d for d in grade_breakdown(java_trace(), JAVA_CRITERIA)}
    correctness = dims["correctness"]
    assert correctness["band"] == "Not yet"
    checks = correctness["checks"]
    assert [c["met"] for c in checks] == [False, False]
    assert checks[0]["statement"].startswith("States that a subclass")
    assert checks[1]["statement"] == NO_ERRORS_CHECK
    assert "different parameters" in checks[1]["note"]
    assert dims["reasoning"]["band"] == "Strong"  # the correct concept is credited


# ------------------------------------------------------------------ repetition


LIVE_REPLY = (
    "Your answer correctly explains overriding's role in polymorphism but has a key technical "
    "error: overridden methods must have the same parameters, not different ones. This is "
    "crucial for runtime method resolution."
)


def test_a_copied_reply_is_a_repeat_and_a_new_one_is_not() -> None:
    assert repeat_of(LIVE_REPLY, [LIVE_REPLY]) == LIVE_REPLY
    fresh = (
        "You're right that the runtime part is correct and was credited under reasoning. The "
        "low correctness band comes from one sentence failing two checks."
    )
    assert repeat_of(fresh, [LIVE_REPLY]) is None


@pytest.mark.parametrize(
    ("reply", "flagged"),
    [
        ("I've updated your grade to Proficient.", True),
        ("Your result has been changed to Strong.", True),
        ("I can't change results, but you can ask for a re-check below.", False),
        ("Your grade stays as it is; the error is a misconception.", False),
    ],
)
def test_claims_that_a_result_changed_are_caught(reply: str, flagged: bool) -> None:
    assert bool(reply_problems(reply, [], "p")) is flagged


def test_settled_points_accumulate_without_duplicates() -> None:
    metas = [
        {"accepts": ["overriding needs the same parameters"]},
        {"accepts": ["Overriding needs the same  parameters", "return types matter"]},
        {},
    ]
    assert settled_points(metas) == ["overriding needs the same parameters", "return types matter"]


# ------------------------------------------------------------------ re-check rules


def test_java_appeal_upheld_keeps_the_grade() -> None:
    """The learner's appeal is about weighting, not about a wrong verdict: the bundled
    requirement needs 'same signature', which the answer contradicts. Upholding is correct."""
    out = recheck(
        CriterionRecheck(criterion_id="P1.C1", decision="uphold", evidence="", reason="r"),
        CriterionRecheck(criterion_id="P1.C2", decision="uphold", evidence="", reason="r"),
        errors=[ErrorRecheck(error=1, stands=True, reason="it is wrong")],
    )
    result = apply_recheck(java_trace(), JAVA_CRITERIA, JAVA_ANSWER, out, load_bands())
    assert not result.changed and result.bands_after == result.bands_before


def test_a_revision_needs_a_quote_from_the_answer() -> None:
    """A model that gives in to the learner must still quote the answer; a quote of what the
    answer doesn't say ('the same signature') is refused."""
    out = recheck(
        CriterionRecheck(
            criterion_id="P1.C1", decision="revise", evidence="with the same signature", reason="r"
        )
    )
    result = apply_recheck(java_trace(), JAVA_CRITERIA, JAVA_ANSWER, out, load_bands())
    assert result.refused == ["P1.C1"] and not result.changed


def test_partial_credit_one_criterion_revised_while_the_error_still_counts() -> None:
    """A valid reversal on one check raises correctness, but the standing error still costs
    the no-wrong-statements check, so the band doesn't jump to the top."""
    out = recheck(
        CriterionRecheck(
            criterion_id="P1.C1",
            decision="revise",
            evidence="provide its own implementation of the method",
            reason="r",
        ),
        errors=[ErrorRecheck(error=1, stands=True, reason="r")],
    )
    result = apply_recheck(java_trace(), JAVA_CRITERIA, JAVA_ANSWER, out, load_bands())
    assert result.revised == ["P1.C1"]
    assert result.bands_before["correctness"] == "Not yet"
    assert result.bands_after["correctness"] not in ("Not yet", "Strong")


def test_a_wrongly_listed_error_can_be_dropped_but_a_real_one_stands() -> None:
    dropped = apply_recheck(
        java_trace(c1=True),
        JAVA_CRITERIA,
        JAVA_ANSWER,
        recheck(errors=[ErrorRecheck(error=1, stands=False, reason="it is correct")]),
        load_bands(),
    )
    assert dropped.errors_dropped == [1] and dropped.bands_after["correctness"] == "Strong"
    kept = apply_recheck(
        java_trace(c1=True),
        JAVA_CRITERIA,
        JAVA_ANSWER,
        recheck(errors=[ErrorRecheck(error=1, stands=True, reason="r")]),
        load_bands(),
    )
    assert not kept.changed


def test_decisions_already_in_the_learners_favour_cannot_move() -> None:
    """Only what counted against the answer is reviewed; a 'revise' on a met criterion, or an
    unknown criterion or error number, is ignored."""
    out = recheck(
        CriterionRecheck(criterion_id="P1.C3", decision="revise", evidence="", reason="r"),
        CriterionRecheck(criterion_id="P9.C9", decision="revise", evidence="x", reason="r"),
        errors=[ErrorRecheck(error=7, stands=False, reason="r")],
    )
    result = apply_recheck(java_trace(), JAVA_CRITERIA, JAVA_ANSWER, out, load_bands())
    assert not result.changed and not result.refused


def test_a_revision_quoting_a_statement_still_listed_as_wrong_is_refused() -> None:
    """Live check R5: the model revised "states a function" to met on a wrong function. The
    grading pipeline's own rule refuses it: a wrong statement can't be evidence."""
    out = recheck(
        CriterionRecheck(criterion_id="P1.C1", decision="revise", evidence=WRONG, reason="r"),
        errors=[ErrorRecheck(error=1, stands=True, reason="still wrong")],
    )
    result = apply_recheck(java_trace(), JAVA_CRITERIA, JAVA_ANSWER, out, load_bands())
    assert result.contradicted == ["P1.C1"] and not result.changed


def test_an_answer_to_another_question_cannot_move() -> None:
    """Its listed 'error' is often just that it answers something else (live check R8)."""
    trace = java_trace().model_copy(update={"addresses_question": False})
    out = recheck(
        CriterionRecheck(
            criterion_id="P1.C1",
            decision="revise",
            evidence="provide its own implementation of the method",
            reason="r",
        ),
        errors=[ErrorRecheck(error=1, stands=False, reason="true statement")],
    )
    result = apply_recheck(trace, JAVA_CRITERIA, JAVA_ANSWER, out, load_bands())
    assert result.off_topic and not result.changed
    assert result.bands_after == result.bands_before
