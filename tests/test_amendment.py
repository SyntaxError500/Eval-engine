"""Phase 5: proposer, verifier, rubric versioning, and the pipeline's amendment branch."""

import json
import sqlite3
from typing import Any

import pytest

from eval_engine.amendment.propose import PROPOSED_CRITERION_WEIGHT, as_solution_path
from eval_engine.amendment.stage import amended
from eval_engine.config import load_config
from eval_engine.evaluation.aggregate import Bands
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.base import ProviderError
from eval_engine.providers.fake import FakeProvider
from eval_engine.schemas import Dimension, Question, TaskType
from eval_engine.schemas.amendment import ProposedCriterion, ProposedPath, VerifierVerdict
from eval_engine.storage import RubricStore
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from tests.conftest import make_config, make_rubric, rubric_data

ANSWER = "Rome fell because plague emptied the cities and cut the tax base that paid the army."
ROLE = {"temperature": 0.0, "max_output_tokens": 512}


def judge_reply(
    path: str = "P1",
    conf: float = 0.1,
    addresses: bool = True,
    criteria: tuple[str, ...] = ("P1.C1", "P1.C2"),
    met: bool = False,
) -> str:
    return json.dumps(
        {
            "identified_path": path,
            "path_confidences": [{"path_id": path, "confidence": conf}],
            "addresses_question": addresses,
            "verdicts": [
                {
                    "criterion_id": c,
                    "met": met,
                    "evidence": "plague emptied the cities" if met else "",
                    "justification": "j",
                }
                for c in criteria
            ],
            "errors": [],
        }
    )


def criterion(**overrides: Any) -> dict[str, Any]:
    c = {
        "dimension": "reasoning",
        "statement": "Links a plague to the collapse of the empire through a mechanism",
        "evidence_hint": "A led-to chain from disease to state failure",
        "core": True,
        "requires": "Why did the Western Roman Empire fall",
    }
    return c | overrides


def proposal(criteria: list[dict[str, Any]] | None = None) -> str:
    default = [
        criterion(),
        criterion(
            dimension="correctness",
            statement="Names an epidemic that struck the empire",
            core=False,
        ),
    ]
    return json.dumps(
        {
            "is_new_valid_approach": True,
            "proposed_path": {"description": "Epidemic disease", "criteria": criteria or default},
            "justification": "Disease is not an economic or a military cause.",
        }
    )


NO_NEW_APPROACH = json.dumps(
    {"is_new_valid_approach": False, "proposed_path": None, "justification": "A weak attempt."}
)
ACCEPT = json.dumps({"accept": True, "failure_type": None, "reasons": "It holds."})
REJECT = json.dumps(
    {"accept": False, "failure_type": "factual_error", "reasons": "The dates are wrong."}
)


@pytest.fixture
def env(make_client: Any, conn: sqlite3.Connection) -> tuple[Any, ...]:
    """Judge on alpha, proposer and verifier on beta."""
    client = make_client(
        make_config(
            roles={
                "judge": {"provider": "alpha", "model": "j", "family": "a", **ROLE},
                "amendment_proposer": {"provider": "beta", "model": "p", "family": "b", **ROLE},
                "verifier": {"provider": "beta", "model": "v", "family": "c", **ROLE},
            }
        )
    )
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
        )
    )
    return client, rubrics, questions, EvaluationStore(conn)


def test_accepted_path_becomes_the_next_version_and_answer_is_rescored(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(
        judge_reply(), judge_reply("P3", 0.9, criteria=("P3.C1", "P3.C2"), met=True)
    )
    providers["beta"].push(proposal(), ACCEPT)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert t.amendment_fired and t.verifier_verdict is True
    assert t.final_rubric_source == "amendment" and t.identified_path == "P3"
    assert t.rubric_hash_used != t.rubric_hash_original
    assert t.low_confidence and t.dimension_scores[Dimension.REASONING] == 1.0
    assert json.loads(t.amendment_proposal or "")["proposed_path"]["description"]
    assert t.verifier_framing == "adversarial"

    latest = rubrics.latest("r1")
    assert latest.version == 2 and latest.parent_hash == t.rubric_hash_original
    assert latest.hash == t.rubric_hash_used
    assert [p.path_id for p in latest.paths] == ["P1", "P2", "P3"]
    # The judge's second call saw the new path; the first didn't.
    assert "Epidemic disease" in providers["alpha"].requests[1].user
    assert "Epidemic disease" not in providers["alpha"].requests[0].user


def test_later_answer_matches_the_stored_path_without_a_new_amendment(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(
        judge_reply(), judge_reply("P3", 0.9, criteria=("P3.C1", "P3.C2"), met=True)
    )
    providers["beta"].push(proposal(), ACCEPT)
    evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    calls = len(providers["beta"].requests)
    providers["alpha"].push(judge_reply("P3", 0.9, criteria=("P3.C1", "P3.C2"), met=True))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER + " Taxes fell with the plague.")
    assert not t.amendment_fired and t.identified_path == "P3"
    assert t.final_rubric_source == "amendment" and len(providers["beta"].requests) == calls


def test_rejected_path_leaves_the_original_rubric_and_records_why(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply())
    providers["beta"].push(proposal(), REJECT)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert t.amendment_fired and t.verifier_verdict is False
    assert t.verifier_failure_type == "factual_error"
    assert t.divergence_reason == "The dates are wrong."
    assert t.rubric_hash_used == t.rubric_hash_original and t.final_rubric_source == "generated"
    assert rubrics.latest("r1").version == 1
    assert len(providers["alpha"].requests) == 1  # no re-score


def test_a_verdict_naming_a_failure_is_a_rejection_even_if_accept_is_true() -> None:
    v = VerifierVerdict(accept=True, failure_type="invalid_inference", reasons="r")
    assert not v.accepted


def test_proposer_finding_nothing_skips_the_verifier(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply())
    providers["beta"].push(NO_NEW_APPROACH)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert t.amendment_fired and t.verifier_verdict is None and t.verifier_framing is None
    assert t.divergence_reason == "A weak attempt."
    assert len(providers["beta"].requests) == 1


def test_proposal_failing_the_checks_gets_one_retry_with_the_problems(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    bad = proposal([criterion(statement="Gives a clear account of the plague")])  # also too few
    providers["alpha"].push(
        judge_reply(), judge_reply("P3", 0.9, criteria=("P3.C1", "P3.C2"), met=True)
    )
    providers["beta"].push(bad, proposal(), ACCEPT)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert t.verifier_verdict is True
    assert "judgement word" in providers["beta"].requests[1].user
    assert "judgement word" not in providers["beta"].requests[0].user


def test_proposal_failing_the_checks_twice_never_reaches_the_verifier(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    bad = proposal([criterion(statement="Gives a clear account of the plague")])
    providers["alpha"].push(judge_reply())
    providers["beta"].push(bad, bad.replace("clear account", "clear story"))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert t.verifier_verdict is None and "rubric checks" in (t.divergence_reason or "")
    assert len(providers["beta"].requests) == 2 and rubrics.latest("r1").version == 1


def test_verifier_down_leaves_the_grade_on_the_original_rubric(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply())
    providers["beta"].push(proposal(), ProviderError("down", retryable=False))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert "down" in (t.amendment_error or "") and t.verifier_verdict is None
    assert t.final_rubric_source == "generated" and rubrics.latest("r1").version == 1


def test_answer_about_something_else_never_reaches_the_proposer(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply(addresses=False))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    assert t.low_confidence and not t.amendment_due and not t.amendment_fired
    assert t.addresses_question is False and not providers["beta"].requests


def test_checklist_rubric_has_no_other_route_to_add(
    env: Any, conn: sqlite3.Connection, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    paths = [rubric_data()["paths"][0]]
    r = make_rubric(rubric_id="r2", task_type="factual", shape="checklist", paths=paths)
    rubrics.save(r)
    assert r.hash
    questions.save(
        Question(
            question_id="q2",
            topic="history",
            text=r.question,
            task_type=TaskType.FACTUAL,
            rubric_id=r.rubric_id,
            rubric_hash=r.hash,
        )
    )
    providers["alpha"].push(judge_reply())
    t = evaluate(client, rubrics, questions, evals, "q2", ANSWER)
    assert t.low_confidence and not t.amendment_due and not providers["beta"].requests


def test_confident_answer_does_not_trigger(env: Any, providers: dict[str, FakeProvider]) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply(conf=0.8))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)
    assert not t.low_confidence and not t.amendment_due and not providers["beta"].requests


def test_amend_false_records_that_it_was_due_without_running_it(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply())
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, amend=False)
    assert t.amendment_due and not t.amendment_fired and not providers["beta"].requests


def test_proposer_never_sees_scores_and_verifier_never_sees_the_answer(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(
        judge_reply(), judge_reply("P3", 0.9, criteria=("P3.C1", "P3.C2"), met=True)
    )
    providers["beta"].push(proposal(), ACCEPT)
    evaluate(client, rubrics, questions, evals, "q1", ANSWER)

    to_proposer, to_verifier = providers["beta"].requests
    assert ANSWER in to_proposer.user and "Economic causes" in to_proposer.user
    assert "confidence" not in to_proposer.user and "verdict" not in to_proposer.user
    assert "Links an economic cause" not in to_proposer.user  # descriptions only
    assert ANSWER not in to_verifier.user and ANSWER not in to_verifier.system
    assert "Epidemic disease" in to_verifier.user
    assert "Links an economic cause" in to_verifier.user  # needed to spot a duplicate


@pytest.mark.parametrize(
    ("framing", "phrase"), [("adversarial", "break it"), ("neutral", "Assess")]
)
def test_framing_is_the_only_prompt_difference(
    env: Any, providers: dict[str, FakeProvider], framing: Any, phrase: str
) -> None:
    client, rubrics, questions, evals = env
    bands = Bands([("Low", 0.0)], 0.5, framing)
    providers["alpha"].push(judge_reply())
    providers["beta"].push(proposal(), REJECT)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, bands=bands)
    system = providers["beta"].requests[1].system
    assert t.verifier_framing == framing and phrase in system
    assert "duplicate_path" in system and "Reply with JSON only" in system


def test_amended_rubric_is_a_valid_child_version() -> None:
    r = make_rubric()
    proposed = ProposedPath(
        description="Disease",
        criteria=[
            ProposedCriterion(
                dimension=Dimension.REASONING,
                statement="s",
                evidence_hint="e",
                core=True,
                requires="fall",
            )
        ],
    )
    path = as_solution_path(r, proposed)
    assert path.path_id == "P3" and path.criteria[0].criterion_id == "P3.C1"
    assert path.criteria[0].weight == PROPOSED_CRITERION_WEIGHT
    child = amended(r, path)
    assert child.is_frozen and child.version == 2 and child.parent_hash == r.hash
    assert child.source == "amendment" and child.hash != r.hash


def test_repo_framing_setting_is_adversarial() -> None:
    from eval_engine.evaluation.aggregate import load_bands

    assert load_bands().verifier_framing == "adversarial"
    assert "amendment_proposer" in load_config().roles
