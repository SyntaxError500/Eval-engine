"""Phase 6: feedback selection, phrasing checks, templates and the learner view (no network)."""

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

import pytest

from eval_engine.evaluation.pipeline import evaluate
from eval_engine.feedback.phrase import (
    ACCEPTED_NOTE,
    DIVERGENCE_LEAD,
    _imperative,
    check_text,
    give_feedback,
)
from eval_engine.feedback.render import learner_view
from eval_engine.feedback.select import Selection, select
from eval_engine.providers.base import ProviderError
from eval_engine.providers.fake import FakeProvider
from eval_engine.schemas import Criterion, Dimension, Question, TaskType, Verdict
from eval_engine.schemas.judge import ClaimError
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from tests.conftest import make_config, make_rubric

WEIGHTS = {"correctness": 0.2, "completeness": 0.2, "reasoning": 0.45, "expression": 0.15}
ANSWER = "Rome fell because heavy taxation ruined its economy. Barbarians were all Vikings."
ROLE = {"temperature": 0.0, "max_output_tokens": 512}


def crit(cid: str, statement: str, dim: str = "reasoning", core: bool = True, w: float = 1.0):
    return Criterion(
        criterion_id=cid,
        dimension=Dimension(dim),
        statement=statement,
        evidence_hint="",
        core=core,
        weight=w,
    )


def trace(verdicts: list[tuple[str, bool]], **fields: Any) -> EvaluationTrace:
    base: dict[str, Any] = {
        "evaluation_id": "e",
        "timestamp": datetime.now(UTC),
        "question_id": "q1",
        "task_type": TaskType.ANALYTICAL,
        "rubric_hash_original": "h",
        "rubric_hash_used": "h",
        "creative_route": False,
        "final_rubric_source": "generated",
        "addresses_question": True,
        "verdicts": [
            Verdict(
                criterion_id=c,
                met=m,
                evidence="heavy taxation" if m else "",
                justification=f"note on {c}",
            )
            for c, m in verdicts
        ],
    }
    return EvaluationTrace.model_validate(base | fields)


CRITERIA = [
    crit("C1", "States a position on the cause of the fall"),
    crit("C2", "Provides a first distinct reason that supports the position"),
    crit("C3", "Provides a second distinct reason that supports the position"),
    crit("C4", "Explains how the economy affected the army", core=False, w=0.5),
    crit("C5", "Names an emperor of the period", dim="correctness", core=True),
]


# ---------------------------------------------------------------- selection


def test_problems_are_ranked_core_first_then_by_weight() -> None:
    t = trace([("C1", True), ("C2", True), ("C3", True), ("C4", False), ("C5", False)])
    s = select(t, CRITERIA, WEIGHTS, ANSWER)
    # C5 is core (correctness 0.2); C4 non-core reasoning comes after it despite 0.45 weight.
    assert [p.refs for p in s.improve] == [("C5",), ("C4",)]


def test_near_duplicate_criteria_make_one_point() -> None:
    t = trace([("C1", True), ("C2", False), ("C3", False), ("C4", True), ("C5", True)])
    s = select(t, CRITERIA, WEIGHTS, ANSWER)
    assert [p.refs for p in s.improve] == [("C2", "C3")]


def test_a_third_problem_only_when_it_is_core() -> None:
    criteria = [*CRITERIA, crit("C6", "Gives a date for the end of the empire", core=False)]
    t = trace([(c.criterion_id, False) for c in criteria])
    s = select(t, criteria, WEIGHTS, ANSWER)
    assert len(s.improve) == 3 and all(p.core for p in s.improve)  # C1, C2+C3, C5
    criteria = [CRITERIA[0], crit("C7", "Names a battle"), CRITERIA[3]]
    s = select(trace([("C1", False), ("C7", False), ("C4", False)]), criteria, WEIGHTS, ANSWER)
    assert [p.refs for p in s.improve] == [("C1",), ("C7",)]  # C4 is non-core: left out


def test_what_worked_comes_from_met_core_criteria() -> None:
    t = trace([("C1", True), ("C2", False), ("C3", False), ("C4", True), ("C5", True)])
    s = select(t, CRITERIA, WEIGHTS, ANSWER)
    assert [p.refs for p in s.worked] == [("C1",), ("C5",)]  # C4 met but not core


def test_a_factual_error_is_a_problem_and_absorbs_the_criterion_it_wrongly_passed() -> None:
    t = trace(
        [("C1", True), ("C2", False), ("C3", True), ("C4", True), ("C5", True)],
        errors=[ClaimError(quote="Barbarians were all Vikings", explanation="Not Vikings.")],
        contradiction_downgrades=["C2"],
    )
    t.verdicts[1] = t.verdicts[1].model_copy(update={"evidence": "Barbarians were all Vikings"})
    s = select(t, CRITERIA, WEIGHTS, ANSWER)
    assert s.improve[0].kind == "error" and s.improve[0].refs == ("error:1", "C2")
    assert all("C2" not in p.refs[1:] or p.kind == "error" for p in s.improve)


def test_code_overturned_verdicts_lose_the_judges_reasons_for_passing() -> None:
    t = trace([("C1", False), ("C2", True), ("C3", True), ("C4", True), ("C5", True)])
    t.verdicts[0] = t.verdicts[0].model_copy(
        update={"justification": "[evidence not found in answer] The position is clear."}
    )
    assert select(t, CRITERIA, WEIGHTS, ANSWER).improve[0].reason == ""
    t.verdicts[0] = t.verdicts[0].model_copy(
        update={"justification": "[counted in code: 10 sentences] Fits the range."}
    )
    assert select(t, CRITERIA, WEIGHTS, ANSWER).improve[0].reason == "The answer has 10 sentences."


def test_answer_about_something_else_gets_one_point_only() -> None:
    t = trace([("C1", False), ("C2", False)], addresses_question=False)
    s = select(t, CRITERIA, WEIGHTS, ANSWER)
    assert s.off_topic and not s.improve and not s.worked


@pytest.mark.parametrize(
    ("fields", "approach"),
    [
        ({"amendment_fired": True, "final_rubric_source": "amendment", "verifier_verdict": True},
         "accepted"),
        ({"amendment_fired": True, "verifier_verdict": False, "divergence_reason": "Wrong."},
         "rejected"),
        ({"amendment_fired": True, "divergence_reason": "A weak attempt."}, "rejected"),
        ({"amendment_fired": True, "divergence_reason": "proposal failed the rubric checks: x"},
         None),
        ({"amendment_fired": True, "amendment_error": "ProviderError: down"}, None),
        ({}, None),
    ],
)  # fmt: skip
def test_route_note_follows_the_amendment_outcome(fields: dict[str, Any], approach: Any) -> None:
    assert select(trace([("C1", True)], **fields), CRITERIA, WEIGHTS, ANSWER).approach == approach


# ---------------------------------------------------------------- checks on phrased text

REFERENCE = "Taxation drained the provinces until the legions went unpaid and mutinied there."


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        ('You wrote "heavy taxation ruined its economy"; add a second reason.', None),
        ('You wrote "the senate collapsed overnight"; add a reason.', "not in the answer"),
        ("Your score on P1.C2 is low.", "grading internals"),
        ("Your rubric criterion is not met.", "grading internals"),
        ("you " * 61, "too long"),
        ("", "missing"),
        ("You should say that the legions went unpaid and mutinied there.", "model answer"),
        ("Your words: heavy taxation. Add a second reason.", "label"),
        ("null", "missing"),
        ("Problem: you named no cause.", "label"),
        ("The student names no cause; add one.", "you"),
        ("The answer names no cause; add one.", "you"),
        ('You were asked "why did the Western Roman Empire fall"; answer that.', None),
    ],
)
def test_phrased_text_checks(text: str, problem: str | None) -> None:
    allowed = "Why did the Western Roman Empire fall? " + ANSWER
    why = check_text(text, ANSWER, REFERENCE, allowed)
    assert (why is None) if problem is None else (why is not None and problem in why)


def test_wording_shared_with_the_answer_is_not_a_leak() -> None:
    answer = "The legions went unpaid and mutinied in the end."
    text = "You note that the legions went unpaid and mutinied; explain why."
    assert check_text(text, answer, REFERENCE, answer) is None


@pytest.mark.parametrize(
    ("statement", "imperative"),
    [
        ("Explains how X works", "explain how X works"),
        ("Identifies the narrator", "identify the narrator"),
        ("Does not use clichés", "do not use clichés"),
        ("Names a cause.", "name a cause"),
        ("Establishes a link", "establish a link"),
    ],
)
def test_template_turns_a_criterion_into_an_action(statement: str, imperative: str) -> None:
    assert _imperative(statement) == imperative


# ---------------------------------------------------------------- give_feedback


@pytest.fixture
def client(make_client: Any) -> Any:
    return make_client(
        make_config(
            roles={
                "judge": {"provider": "alpha", "model": "j", "family": "a", **ROLE},
                "feedback_phraser": {"provider": "beta", "model": "f", "family": "b", **ROLE},
            }
        )
    )


def phrased(points: dict[str, str], divergence: str | None = None, off: str | None = None) -> str:
    return json.dumps(
        {
            "points": [{"ref": r, "text": t} for r, t in points.items()],
            "divergence": divergence,
            "off_topic": off,
        }
    )


def selection() -> Selection:
    t = trace([("C1", True), ("C2", False), ("C3", False), ("C4", True), ("C5", False)])
    return select(t, CRITERIA, WEIGHTS, ANSWER)


def test_checked_wording_is_used_in_display_order(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    providers["beta"].push(
        phrased(
            {
                "I1": "You give one reason; add a second.",
                "I2": "You name no emperor; add one.",
                "W1": "You took a side.",
            }
        )
    )
    fb = give_feedback(client, selection(), "Why did Rome fall?", ANSWER, REFERENCE)
    assert [(i.kind, i.source, i.text) for i in fb.items] == [
        ("improve", "model", "You give one reason; add a second."),
        ("improve", "model", "You name no emperor; add one."),
        ("worked", "model", "You took a side."),
    ]
    assert fb.items[0].refs == ["C2", "C3"] and not fb.fallbacks
    sent = providers["beta"].requests[0]
    assert REFERENCE not in sent.user and "score" not in sent.user.lower()


def test_a_failed_point_is_rephrased_once_then_templated(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    bad = 'You wrote "the senate collapsed"; fix it.'
    providers["beta"].push(
        phrased({"I1": bad, "I2": "You name no emperor; add one.", "W1": "You took a side."}),
        phrased({"I1": bad, "I2": "changed", "W1": "changed"}),
    )
    fb = give_feedback(client, selection(), "Why did Rome fall?", ANSWER, REFERENCE)
    texts = {i.text: i.source for i in fb.items}
    assert texts["You name no emperor; add one."] == "model"  # the first passing version is kept
    assert texts["Next time, provide a first distinct reason that supports the position."] == (
        "template"
    )
    assert "I1: quotes words" in fb.fallbacks[0]
    assert "I1:" in providers["beta"].requests[1].user  # the retry carried the problem


def test_feedback_model_down_gives_templates_not_nothing(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    providers["beta"].push(ProviderError("down", retryable=False))
    fb = give_feedback(client, selection(), "Why did Rome fall?", ANSWER, REFERENCE)
    assert {i.source for i in fb.items} == {"template"} and len(fb.items) == 3
    assert "unavailable" in fb.fallbacks[0]


def test_accepted_route_note_is_fixed_and_first(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    s = selection()
    s.approach = "accepted"
    providers["beta"].push(phrased({"I1": "You a.", "I2": "You b.", "W1": "You c."}))
    fb = give_feedback(client, s, "Why did Rome fall?", ANSWER, REFERENCE)
    assert fb.items[0].kind == "approach" and fb.items[0].text == ACCEPTED_NOTE
    assert fb.items[0].source == "fixed"


def test_rejected_route_and_off_topic_are_phrased(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    s = Selection(approach="rejected", divergence_reason="It relies on a false premise.")
    providers["beta"].push(phrased({}, divergence="Your route was checked and didn't hold."))
    fb = give_feedback(client, s, "Why did Rome fall?", ANSWER, REFERENCE)
    assert [(i.kind, i.source) for i in fb.items] == [("divergence", "model")]
    assert fb.items[0].text == f"{DIVERGENCE_LEAD} Your route was checked and didn't hold."
    providers["beta"].push(phrased({}, divergence="It didn\u2019t hold up: your premise is false."))
    fb = give_feedback(client, s, "Why did Rome fall?", ANSWER + " ", REFERENCE)
    assert fb.items[0].text == f"{DIVERGENCE_LEAD} your premise is false."  # no doubled opener
    assert "false premise" in providers["beta"].requests[0].user

    providers["beta"].push(phrased({}, off="Your answer is about Vikings, not the fall."))
    fb = give_feedback(client, Selection(off_topic=True), "Why did Rome fall?", ANSWER, None)
    assert [(i.kind, i.source) for i in fb.items] == [("off_topic", "model")]


def test_originality_note_is_fixed_and_never_crowds_out_problems(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    s = Selection(obvious=["a hero saves the day"])
    fb = give_feedback(client, s, "Write a story.", ANSWER, None)
    assert [(i.kind, i.source) for i in fb.items] == [("originality", "fixed")]
    assert not providers["beta"].requests  # nothing for the model to phrase


# ---------------------------------------------------------------- pipeline and view


def test_pipeline_adds_feedback_only_when_asked(
    client: Any, conn: sqlite3.Connection, providers: dict[str, FakeProvider]
) -> None:
    rubrics, questions = RubricStore(conn), QuestionStore(conn)
    r = make_rubric()
    rubrics.save(r)
    assert r.hash
    questions.save(
        Question(
            question_id="q1",
            topic="history",
            text=r.question,
            task_type=TaskType.ANALYTICAL,
            rubric_id=r.rubric_id,
            rubric_hash=r.hash,
            reference_answer=REFERENCE,
        )
    )
    reply = json.dumps(
        {
            "identified_path": "P1",
            "path_confidences": [{"path_id": "P1", "confidence": 0.9}],
            "addresses_question": True,
            "verdicts": [
                {"criterion_id": "P1.C1", "met": True, "evidence": "heavy taxation",
                 "justification": "j"},
                {"criterion_id": "P1.C2", "met": False, "evidence": "", "justification": "j"},
            ],
            "errors": [],
        }
    )  # fmt: skip
    providers["alpha"].push(reply, reply)
    providers["beta"].push(
        phrased({"I1": "You state no fact; add one.", "W1": "You linked a cause."})
    )
    evals = EvaluationStore(conn)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, feedback=True)
    assert t.feedback is not None and [i.kind for i in t.feedback.items] == ["improve", "worked"]
    assert evals.get(t.evaluation_id).feedback == t.feedback
    plain = evaluate(client, rubrics, questions, evals, "q1", ANSWER + " More.")
    assert plain.feedback is None and len(providers["beta"].requests) == 1


def test_learner_view_puts_feedback_before_bands_and_shows_no_numbers(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    providers["beta"].push(
        phrased(
            {
                "I1": "You give one reason; add a second.",
                "I2": "You name none; add one.",
                "W1": "You kept it.",
            }
        )
    )
    t = trace([("C1", True)], bands={Dimension.REASONING: "Developing"})
    t.dimension_scores = {Dimension.REASONING: 0.5}
    t.feedback = give_feedback(client, selection(), "Why?", ANSWER, None)
    text = "\n".join(learner_view(t))
    assert text.index("To work on:") < text.index("What worked:") < text.index("Bands:")
    assert "Developing" in text and "0.5" not in text


# ---------------------------------------------------------------- merges (first review-set run)


def test_a_criterion_that_depends_on_another_joins_its_point() -> None:
    criteria = [
        crit("P1.C5", "Names a third valid cell-cycle phase"),
        crit("P1.C6", "Provides a correct key event that occurs in the phase named in C5"),
        crit("P1.C7", "Gives the length of the whole cycle"),
    ]
    t = trace([("P1.C5", False), ("P1.C6", False), ("P1.C7", False)])
    s = select(t, criteria, WEIGHTS, ANSWER)
    assert [p.refs for p in s.improve] == [("P1.C5", "P1.C6"), ("P1.C7",)]
    assert s.improve[0].also == (criteria[1].statement,)


def test_a_failure_the_judge_pinned_on_a_listed_error_is_told_as_that_error() -> None:
    criteria = [
        crit("C1", "Names three distinct macronutrients", dim="correctness"),
        crit("C2", "States a function of the third macronutrient named", dim="correctness"),
        crit("C3", "Names a source of each nutrient", dim="completeness"),
    ]
    t = trace(
        [("C1", False), ("C2", False), ("C3", False)],
        errors=[
            ClaimError(
                quote="Vitamins are the third macronutrient",
                explanation="Vitamins are micronutrients, not macronutrients.",
            )
        ],
    )
    notes = {
        "C1": "Lists vitamins as the third macronutrient instead of fats.",
        "C2": "The third item listed is vitamins, a micronutrient, not a macronutrient.",
        "C3": "No food sources are given.",
    }
    t.verdicts = [v.model_copy(update={"justification": notes[v.criterion_id]}) for v in t.verdicts]
    s = select(t, criteria, WEIGHTS, ANSWER)
    assert [p.refs for p in s.improve] == [("error:1", "C1", "C2"), ("C3",)]
    assert s.improve[0].also == (criteria[0].statement, criteria[1].statement)


def test_sentence_counts_come_from_code_even_when_met() -> None:
    criteria = [crit("C1", "Contains between three and eight sentences", core=True)]
    s = select(trace([("C1", True)]), criteria, WEIGHTS, "One. Two. Three. Four.")
    assert s.worked[0].reason == "The answer has 4 sentences."


def test_what_worked_prefers_something_done_over_an_absence() -> None:
    criteria = [
        crit("C1", 'Does not use any of: "silver lining"', dim="expression"),
        crit("C2", "Features a character who observes the changes", dim="correctness"),
    ]
    s = select(trace([("C1", True), ("C2", True)]), criteria, WEIGHTS, ANSWER)
    assert s.worked[0].refs == ("C2",)


def test_rubric_wording_shared_with_the_reference_is_not_a_leak(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    reference = "Heating lowers its density compared to the cooler air outside, so it rises."
    text = "You never say that heating lowers its density compared to the cooler air outside."
    assert check_text(text, ANSWER, reference, ANSWER) is not None
    rubric = "States that heating lowers its density compared to the cooler air outside"
    assert check_text(text, ANSWER, reference, f"{ANSWER} {rubric}") is None


# ---------------------------------------------------------------- external review 1 fixes


def test_explaining_the_example_joins_the_point_asking_for_one() -> None:
    criteria = [
        crit("C1", "States a position that the alliances were the main cause"),
        crit("C2", "Provides a specific historical example that supports the position"),
        crit("C3", "Explains how the example demonstrates that the alliances caused the war"),
    ]
    s = select(trace([("C1", True), ("C2", False), ("C3", False)]), criteria, WEIGHTS, ANSWER)
    assert [p.refs for p in s.improve] == [("C2", "C3")]
    # With the example given, explaining it is a problem of its own.
    s = select(trace([("C1", True), ("C2", True), ("C3", False)]), criteria, WEIGHTS, ANSWER)
    assert [p.refs for p in s.improve] == [("C3",)]
    # Both met: giving and explaining an example are separate things that worked.
    s = select(trace([("C1", True), ("C2", True), ("C3", True)]), criteria, WEIGHTS, ANSWER)
    assert [p.refs for p in s.worked] == [("C1",), ("C2",)]


def test_off_topic_note_may_name_the_topic_in_another_word_form() -> None:
    from eval_engine.feedback.phrase import _names_nothing_from

    answer = "Working from home makes companies more productive and saves money."
    note = "You discuss company productivity, not work-life balance; argue that instead."
    assert _names_nothing_from(note, answer, "Does working from home help balance?") is None


def test_an_off_topic_note_must_say_what_the_answer_is_about(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    generic = "Your answer doesn't address the question; it asks why the empire collapsed."
    specific = "You write about Vikings instead of why Rome fell; explain a cause of the fall."
    providers["beta"].push(phrased({}, off=generic), phrased({}, off=specific))
    fb = give_feedback(client, Selection(off_topic=True), "Why did Rome fall?", ANSWER, None)
    assert fb.items[0].text == specific and fb.items[0].source == "model"
    assert "say what their answer is about" in providers["beta"].requests[1].user

    providers["beta"].push(phrased({}, off=generic), phrased({}, off=generic))
    fb = give_feedback(client, Selection(off_topic=True), "Why did Rome fall?", ANSWER + " ", None)
    assert fb.items[0].source == "template" and "Rome fell because heavy" in fb.items[0].text


def test_worked_template_quotes_what_the_judge_credited(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    providers["beta"].push(ProviderError("down", retryable=False))
    fb = give_feedback(client, selection(), "Why did Rome fall?", ANSWER, None)
    worked = [i.text for i in fb.items if i.kind == "worked"]
    assert worked == [
        'You wrote "heavy taxation", which states a position on the cause of the fall.'
    ]


def test_originality_note_is_labelled_as_a_comparison(
    client: Any, providers: dict[str, FakeProvider]
) -> None:
    fb = give_feedback(client, Selection(obvious=["A hero saves the day."]), "Story.", ANSWER, None)
    assert "For comparison, that take is:" in fb.items[0].text
