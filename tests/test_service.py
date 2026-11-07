"""Phase 8 service: question bank, submissions, queueing and the degradation rules (no network)."""

import json
import random
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from eval_engine import service as service_module
from eval_engine.generation.generate import GeneratedQuestion, GenerationError
from eval_engine.providers.base import ProviderError, QuotaExhausted
from eval_engine.providers.fake import FakeProvider
from eval_engine.schemas import Question, TaskType
from eval_engine.service import (
    AnswerRejected,
    EngineService,
    GenerationFailed,
    RecheckUnavailable,
    TopicRejected,
    TutorUnavailable,
)
from eval_engine.storage import RubricStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.tutor import FALLBACK_REPLY
from tests.conftest import make_config, make_rubric

ROLE = {"temperature": 0.0, "max_output_tokens": 512}
ANSWER = "Rome fell because heavy taxation ruined its economy and the armies went unpaid."


def judge_reply(conf: float = 0.9) -> str:
    return json.dumps(
        {
            "identified_path": "P1",
            "path_confidences": [{"path_id": "P1", "confidence": conf}],
            "addresses_question": True,
            "verdicts": [
                {"criterion_id": "P1.C1", "met": True, "evidence": "heavy taxation",
                 "justification": "j"},
                {"criterion_id": "P1.C2", "met": False, "evidence": "", "justification": "j"},
            ],
            "errors": [],
        }
    )  # fmt: skip


PHRASED = json.dumps(
    {
        "points": [
            {"ref": "I1", "text": "You give no economic fact; add one."},
            {"ref": "W1", "text": "You link taxation to the fall."},
        ],
        "divergence": None,
        "off_topic": None,
    }
)


@pytest.fixture
def svc(make_client: Any, conn: sqlite3.Connection, tmp_path: Path) -> EngineService:
    config = make_config(
        providers={
            "alpha": {"api_key_env": None, "limits": {"rpm": 100, "rpd": 5}},
            "beta": {"api_key_env": None, "limits": {"rpm": 100}},
        },
        roles={
            "judge": {"provider": "alpha", "model": "j", "family": "a", **ROLE},
            "amendment_proposer": {"provider": "beta", "model": "p", "family": "b", **ROLE},
            "verifier": {"provider": "beta", "model": "v", "family": "c", **ROLE},
            "feedback_phraser": {"provider": "beta", "model": "f", "family": "d", **ROLE},
            "tutor": {"provider": "beta", "model": "t", "family": "d", **ROLE},
            "rechecker": {"provider": "alpha", "model": "j", "family": "a", **ROLE},
        },
    )
    rubric = make_rubric()
    RubricStore(conn).save(rubric)
    assert rubric.hash
    for qid, topic in (("q1", "history"), ("q2", "history"), ("q3", "science")):
        QuestionStore(conn).save(
            Question(
                question_id=qid,
                topic=topic,
                text=rubric.question,
                task_type=TaskType.ANALYTICAL,
                rubric_id=rubric.rubric_id,
                rubric_hash=rubric.hash,
                reference_answer="One possible answer.",
            )
        )
    bank = tmp_path / "accepted.json"
    bank.write_text(json.dumps([{"question_id": q} for q in ("q1", "q2", "q3")]))
    return EngineService(conn, make_client(config), config, bank_file=bank, rng=random.Random(1))


def test_questions_come_from_the_reviewed_bank(svc: EngineService) -> None:
    assert svc.topics() == ["history", "science"]
    first = svc.question_for("history")
    assert svc.question_for("history", exclude={first.question_id}).question_id != first.question_id
    assert svc.question_for("science").question_id == "q3"


def test_a_graded_submission_has_feedback(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push(judge_reply())
    providers["beta"].push(PHRASED)
    sub = svc.submit("q1", ANSWER)
    trace = svc.trace(sub)
    assert sub.status == "done" and trace is not None and trace.feedback is not None
    assert [i.source for i in trace.feedback.items] == ["model", "model"]
    assert svc.recent()[0].submission_id == sub.submission_id


@pytest.mark.parametrize(
    "failure",
    [QuotaExhausted("daily limit"), ProviderError("gemini 503: high demand", retryable=False)],
)
def test_judge_unavailable_queues_and_never_grades_with_another_model(
    svc: EngineService, providers: dict[str, FakeProvider], failure: ProviderError
) -> None:
    providers["alpha"].push(failure)
    sub = svc.submit("q1", ANSWER)
    assert sub.status == "queued" and sub.evaluation_id is None and sub.attempts == 1
    assert not providers["beta"].requests  # no proposer, verifier or phraser stood in
    assert [s.submission_id for s in svc.queued()] == [sub.submission_id]

    providers["alpha"].push(judge_reply())
    providers["beta"].push(PHRASED)
    (retried,) = svc.retry_queued()
    assert retried.status == "done" and retried.attempts == 2 and not svc.queued()


def test_feedback_model_down_still_gives_marked_feedback(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push(judge_reply())
    providers["beta"].push(ProviderError("cannot reach Ollama", retryable=False))
    sub = svc.submit("q1", ANSWER)
    trace = svc.trace(sub)
    assert sub.status == "done" and trace is not None and trace.feedback is not None
    assert {i.source for i in trace.feedback.items} == {"template"}
    assert "unavailable" in trace.feedback.fallbacks[0]


def test_verifier_down_grades_on_the_original_rubric(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    proposal = json.dumps(
        {
            "is_new_valid_approach": True,
            "proposed_path": {
                "description": "Epidemic disease",
                "criteria": [
                    {"dimension": "reasoning", "statement": "Links a plague to the fall of the "
                     "empire through a mechanism", "evidence_hint": "e", "core": True,
                     "requires": "Why did the Western Roman Empire fall"},
                    {"dimension": "correctness", "statement": "Names an epidemic that struck the "
                     "empire", "evidence_hint": "e", "core": False,
                     "requires": "Why did the Western Roman Empire fall"},
                ],
            },
            "justification": "Disease is a different cause.",
        }
    )  # fmt: skip
    providers["alpha"].push(judge_reply(conf=0.1))
    providers["beta"].push(proposal, ProviderError("verifier down", retryable=False), PHRASED)
    sub = svc.submit("q1", ANSWER)
    trace = svc.trace(sub)
    assert sub.status == "done" and trace is not None
    assert trace.amendment_fired and "verifier down" in (trace.amendment_error or "")
    assert trace.final_rubric_source == "generated" and len(svc.rubric_history("q1")) == 1


@pytest.mark.parametrize("answer", ["", "   ", "x" * 4001])
def test_unusable_answers_are_rejected_before_anything_is_stored(
    svc: EngineService, answer: str
) -> None:
    with pytest.raises(AnswerRejected):
        svc.submit("q1", answer)
    assert not svc.recent()


def test_quota_counts_requests_against_the_daily_limit(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push(judge_reply())
    providers["beta"].push(PHRASED)
    svc.submit("q1", ANSWER)
    judge = next(q for q in svc.quota() if q.role == "judge")
    assert (judge.used, judge.limit, judge.remaining) == (1, 5, 4)
    phraser = next(q for q in svc.quota() if q.role == "feedback_phraser")
    assert phraser.limit is None and phraser.remaining is None


# ---------------------------------------------------------------- live generation


def test_generated_questions_are_marked_unreviewed(
    svc: EngineService, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[str, TaskType]] = []

    def fake_generate(client: Any, rubrics: Any, questions: Any, topic: str, tt: TaskType) -> Any:
        calls.append((topic, tt))
        q = QuestionStore(conn).get("q1").model_copy(update={"question_id": "new1", "topic": topic})
        questions.save(q)
        return GeneratedQuestion(q, RubricStore(conn).get(q.rubric_hash), 1)

    monkeypatch.setattr(service_module, "generate_question", fake_generate)
    q = svc.generate("  how   vaccines train\nthe immune system ", TaskType.EXPLANATORY)
    assert calls == [("how vaccines train the immune system", TaskType.EXPLANATORY)]
    assert not svc.is_reviewed(q.question_id) and svc.is_reviewed("q1")
    assert "how vaccines train the immune system" not in svc.topics()  # bank topics only


@pytest.mark.parametrize("topic", ["", " a ", "x" * 201])
def test_bad_topics_are_rejected_before_any_call(
    svc: EngineService, providers: dict[str, FakeProvider], topic: str
) -> None:
    with pytest.raises(TopicRejected):
        svc.generate(topic, TaskType.FACTUAL)
    assert not providers["alpha"].requests and not providers["beta"].requests


@pytest.mark.parametrize(
    "failure",
    [GenerationError("failed", ["judgement word 'clear'"]), QuotaExhausted("daily limit")],
)
def test_generation_failures_become_one_clear_error(
    svc: EngineService, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    def broken(*args: Any, **kwargs: Any) -> Any:
        raise failure

    monkeypatch.setattr(service_module, "generate_question", broken)
    with pytest.raises(GenerationFailed):
        svc.generate("photosynthesis", TaskType.FACTUAL)


# ---------------------------------------------------------------- discussion


def graded(svc: EngineService, providers: dict[str, FakeProvider]) -> str:
    providers["alpha"].push(judge_reply())
    providers["beta"].push(PHRASED)
    return svc.submit("q1", ANSWER).submission_id


def tutor(reply: str, kind: str = "question", accepts: list[str] | None = None) -> str:
    return json.dumps(
        {"learner_point": "they ask", "kind": kind, "accepts": accepts or [], "reply": reply}
    )


REPLY_A = (
    "Your answer links taxation to the fall, which is right, but it gives no accurate economic "
    "fact such as currency debasement, so that correctness check was not met."
)
REPLY_B = "Try naming one concrete economic fact: what happened to the silver content of coins?"


def test_discussion_is_stored_and_sent_back_as_history(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    bands = svc.trace(svc.get(sid)).bands  # type: ignore[union-attr]
    providers["beta"].push(tutor(REPLY_A))
    assert svc.discuss(sid, "  Why was I marked down? ").text == REPLY_A
    providers["beta"].push(tutor(REPLY_B))
    svc.discuss(sid, "What about inflation?")

    first, second = providers["beta"].requests[-2:]
    # The tutor is told how each band was reached, including the no-wrong-statements check.
    assert "correctness: " in first.user and "Makes no wrong statements" in first.user
    assert "Not met: States at least one accurate economic fact" in first.user
    assert "Tutor: " + REPLY_A in second.user  # history carried over
    assert "Your earlier replies" in second.user and REPLY_A in second.user
    assert [(t.role, t.text) for t in svc.discussion(sid)] == [
        ("learner", "Why was I marked down?"),
        ("tutor", REPLY_A),
        ("learner", "What about inflation?"),
        ("tutor", REPLY_B),
    ]
    assert svc.trace(svc.get(sid)).bands == bands  # type: ignore[union-attr]


def test_a_repeated_reply_is_rejected_and_redrafted(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    """Repeated objection: the model copies its earlier reply; code rejects the draft and
    asks again with the learner's point, and the new draft is used."""
    sid = graded(svc, providers)
    providers["beta"].push(tutor(REPLY_A, kind="challenge"))
    svc.discuss(sid, "I think the grading is too strict.")
    providers["beta"].push(tutor(REPLY_A, kind="challenge"))  # word-for-word copy
    providers["beta"].push(tutor(REPLY_B, kind="challenge"))
    turn = svc.discuss(sid, "You are repeating yourself. My point is that the link is right.")
    assert turn.text == REPLY_B and turn.meta["rejected_drafts"] == 1
    assert not turn.meta["fallback"]
    assert "It repeats your earlier reply" in providers["beta"].requests[-1].user


def test_a_reply_that_keeps_repeating_falls_back_to_a_plain_statement(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    providers["beta"].push(tutor(REPLY_A, kind="challenge"))
    svc.discuss(sid, "The grading is wrong.")
    providers["beta"].push(tutor(REPLY_A, kind="challenge"))
    providers["beta"].push(tutor(REPLY_A + " Really.", kind="challenge"))
    turn = svc.discuss(sid, "The grading is still wrong.")
    assert turn.text == FALLBACK_REPLY and turn.meta["fallback"]
    assert turn.meta["rejected_drafts"] == 2


def test_a_reply_claiming_the_grade_changed_is_rejected(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    providers["beta"].push(tutor("Fair enough, I've updated your grade to Strong.", "challenge"))
    providers["beta"].push(tutor(REPLY_B, kind="challenge"))
    assert svc.discuss(sid, "Give me Strong.").text == REPLY_B
    assert "You can't change results" in providers["beta"].requests[-1].user


def test_an_accepted_correction_is_settled_and_not_explained_again(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    providers["beta"].push(tutor(REPLY_A, "acknowledgement", ["no economic fact given"]))
    svc.discuss(sid, "OK, I accept I gave no economic fact.")
    providers["beta"].push(tutor(REPLY_B))
    svc.discuss(sid, "What should I study next?")
    request = providers["beta"].requests[-1].user
    assert "Already settled" in request and "- no economic fact given" in request


def test_tutor_down_stores_nothing(svc: EngineService, providers: dict[str, FakeProvider]) -> None:
    sid = graded(svc, providers)
    providers["beta"].push(ProviderError("cannot reach Ollama", retryable=False))
    with pytest.raises(TutorUnavailable):
        svc.discuss(sid, "Why?")
    assert svc.discussion(sid) == []


def test_no_discussion_before_grading_or_with_empty_message(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push(QuotaExhausted("daily limit"))
    queued = svc.submit("q1", ANSWER)
    with pytest.raises(AnswerRejected):
        svc.discuss(queued.submission_id, "Why?")
    sid = graded(svc, providers)
    with pytest.raises(AnswerRejected):
        svc.discuss(sid, "   ")


def test_a_reported_grading_problem_is_stored_but_not_sent_to_the_tutor(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    assert not svc.is_flagged(sid)
    svc.flag(sid, "The ending has no instruction but it was counted.")
    assert svc.is_flagged(sid)
    providers["beta"].push(tutor("Fair point."))
    svc.discuss(sid, "Why?")
    assert "has no instruction" not in providers["beta"].requests[-1].user
    assert [t.role for t in svc.discussion(sid)] == ["flag", "learner", "tutor"]


# ---------------------------------------------------------------- re-check


def recheck_reply(decision: str, evidence: str = "", stands: list[bool] | None = None) -> str:
    return json.dumps(
        {
            "criteria": [
                {"criterion_id": "P1.C2", "decision": decision, "evidence": evidence,
                 "reason": "r"},
            ],
            "errors": [{"error": i + 1, "stands": st, "reason": "r"}
                       for i, st in enumerate(stands or [])],
            "correct_parts": ["links taxation to the fall"],
            "incorrect_statement": None,
            "severity": "none",
            "rubric_concern": None,
            "summary": "You link taxation to the fall correctly.",
        }
    )  # fmt: skip


def test_a_valid_challenge_is_upheld_by_the_judge_model_with_a_quote(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    original = svc.trace(svc.get(sid))
    providers["alpha"].push(recheck_reply("revise", "the armies went unpaid"))
    result = svc.recheck(sid, "Unpaid armies is an economic fact, so the fact check is met.")
    assert result.changed and result.revised == ["P1.C2"]
    assert result.bands_before["correctness"] != result.bands_after["correctness"]
    # Graded by the judge's provider, never the local tutor's; the original is untouched.
    assert "senior grader" in providers["alpha"].requests[-1].system
    assert svc.trace(svc.get(sid)) == original
    assert svc.is_flagged(sid)  # the argument is kept for review either way


def test_an_invalid_challenge_changes_nothing(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    """A confident appeal the answer doesn't support: the model upholds, so nothing moves."""
    sid = graded(svc, providers)
    providers["alpha"].push(recheck_reply("uphold"))
    result = svc.recheck(sid, "I obviously know the economic facts, give me the marks.")
    assert not result.changed and result.bands_after == result.bands_before


def test_a_reversal_without_a_quote_from_the_answer_is_refused(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    """If the model gives in to the appeal but can't quote the answer, code refuses it."""
    sid = graded(svc, providers)
    providers["alpha"].push(recheck_reply("revise", "currency debasement under Diocletian"))
    result = svc.recheck(sid, "I meant currency debasement.")
    assert result.refused == ["P1.C2"] and not result.changed


def test_only_one_recheck_and_the_tutor_is_told_its_outcome(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    providers["alpha"].push(recheck_reply("uphold"))
    svc.recheck(sid, "The fact check should be met because of unpaid armies.")
    with pytest.raises(AnswerRejected):
        svc.recheck(sid, "Please look again, it really should be met.")
    providers["beta"].push(tutor(REPLY_B, "challenge"))
    svc.discuss(sid, "Why did the re-check say no?")
    request = providers["beta"].requests[-1].user
    assert "Re-check already done (final): No decision changed." in request


def test_recheck_unavailable_stores_nothing(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    providers["alpha"].push(QuotaExhausted("daily limit"))
    with pytest.raises(RecheckUnavailable):
        svc.recheck(sid, "The fact check should be met because of unpaid armies.")
    assert svc.recheck_result(sid) is None and not svc.is_flagged(sid)


def test_a_recheck_needs_an_argument(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    sid = graded(svc, providers)
    with pytest.raises(AnswerRejected):
        svc.recheck(sid, "wrong")


def test_the_local_model_answers_when_the_tutor_provider_is_unavailable(
    make_client: Any,
    conn: sqlite3.Connection,
    svc: EngineService,
    providers: dict[str, FakeProvider],
    tmp_path: Path,
) -> None:
    """Groq rate-limited: the backup local tutor replies, and the reply is marked."""
    config = svc._config.model_copy(deep=True)
    config.roles["tutor_fallback"] = config.roles["tutor"].model_copy(
        update={"provider": "alpha", "model": "local"}
    )
    bank = tmp_path / "bank.json"
    bank.write_text(json.dumps([{"question_id": "q1"}]))
    with_backup = EngineService(conn, make_client(config), config, bank_file=bank)
    sid = graded(with_backup, providers)
    providers["beta"].push(QuotaExhausted("groq daily limit"))
    providers["alpha"].push(tutor(REPLY_B))
    turn = with_backup.discuss(sid, "Why?")
    assert turn.text == REPLY_B and turn.meta["role"] == "tutor_fallback"


def test_the_tutor_never_sees_the_reference_answer(
    svc: EngineService, providers: dict[str, FakeProvider]
) -> None:
    """D2 as tightened in Phase 3: reference answers stay away from learners, so the tutor
    can't pass one on (review found errors in about a third)."""
    sid = graded(svc, providers)
    providers["beta"].push(tutor(REPLY_B))
    svc.discuss(sid, "What would a full answer say?")
    assert "One possible answer." not in providers["beta"].requests[-1].user
