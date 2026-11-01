"""Phase 4: evidence check, aggregation, routing, D6 majority vote (fake judge, no network)."""

import json
import sqlite3
from typing import Any

import pytest

from eval_engine.evaluation.aggregate import Bands, dimension_scores, load_bands, overall_score
from eval_engine.evaluation.counts import apply_count_checks, count_sentences, sentence_range
from eval_engine.evaluation.evidence import (
    apply_error_contradictions,
    apply_evidence_check,
    evidence_supported,
)
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.base import CompletionRequest
from eval_engine.providers.fake import FakeProvider
from eval_engine.schemas import Criterion, Dimension, Question, Rubric, TaskType, Verdict
from eval_engine.schemas.judge import ClaimError
from eval_engine.storage import RubricStore
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from tests.conftest import make_config, make_rubric

ANSWER = (
    "Rome fell partly because heavy taxation and currency debasement ruined its economy. "
    "This led to unpaid armies and weakened defences."
)


def crit(cid: str, dim: str = "reasoning", core: bool = True, w: float = 1.0) -> Criterion:
    return Criterion(
        criterion_id=cid,
        dimension=Dimension(dim),
        statement=f"Checks {cid}",
        evidence_hint="",
        core=core,
        weight=w,
    )


def verdict(cid: str, met: bool, evidence: str = "") -> Verdict:
    return Verdict(criterion_id=cid, met=met, evidence=evidence, justification="j")


# ---------------------------------------------------------------- evidence check


@pytest.mark.parametrize(
    "quote",
    [
        "heavy taxation and currency debasement",
        "Heavy taxation, and currency debasement",  # punctuation and case differ
        "heavy taxaton and curency debasement",  # typos
        "heavy taxation ... unpaid armies",  # fragments from two places
    ],
)
def test_genuine_quotes_are_supported(quote: str) -> None:
    assert evidence_supported(quote, ANSWER)


@pytest.mark.parametrize(
    "quote",
    [
        "barbarian invasions overwhelmed the frontier",
        "heavy taxation, barbarian invasions",  # one real fragment, one invented
        "",
    ],
)
def test_invented_quotes_are_not(quote: str) -> None:
    assert not evidence_supported(quote, ANSWER)


def test_evidence_check_catch_rate_on_20_unsupported_verdicts() -> None:
    """Exit gate: deliberately unsupported 'met' verdicts must be downgraded."""
    invented = [
        "the Huns crossed the Danube",
        "Christianity weakened civic virtue",
        "lead pipes",
        "the Senate lost authority",
        "plague reduced the population",
        "Odoacer deposed Romulus",
        "the empire split in two",
        "slavery stalled innovation",
        "the Goths sacked Rome",
        "climate cooling hurt harvests",
        "corrupt emperors",
        "trade routes collapsed",
        "the army relied on mercenaries",
        "Constantinople rose",
        "inflation of 1000 percent",
        "civil wars every decade",
        "Diocletian's reforms",
        "barbarian federates",
        "loss of North Africa",
        "Vandals took Carthage",
    ]
    criteria = [crit(f"P1.C{i}") for i in range(20)]
    verdicts = [verdict(f"P1.C{i}", True, q) for i, q in enumerate(invented)]
    _, downgraded = apply_evidence_check(verdicts, criteria, ANSWER)
    assert len(downgraded) == 20  # catch rate 20/20


def test_absence_and_count_tests_need_no_quote() -> None:
    c = Criterion(
        criterion_id="P1.C1",
        dimension=Dimension.EXPRESSION,
        statement='Does not use any of: "dark", "silent"',
        evidence_hint="",
        core=True,
        weight=1.0,
        requires="x",
    )
    out, downgraded = apply_evidence_check([verdict("P1.C1", True, "")], [c], ANSWER)
    assert out[0].met and not downgraded


# ---------------------------------------------------------------- aggregation


def test_dimension_scores_and_no_errors_check() -> None:
    criteria = [
        crit("C1", "reasoning", w=1.0),
        crit("C2", "reasoning", w=1.0),
        crit("C3", "correctness", w=1.0),
    ]
    vs = [verdict("C1", True), verdict("C2", False), verdict("C3", True)]
    clean = dimension_scores(criteria, vs, n_errors=0, task_type=TaskType.ANALYTICAL)
    assert clean[Dimension.REASONING] == 0.5 and clean[Dimension.CORRECTNESS] == 1.0
    wrong = dimension_scores(criteria, vs, n_errors=2, task_type=TaskType.ANALYTICAL)
    assert wrong[Dimension.CORRECTNESS] == 0.5  # implicit "no wrong statements" fails
    assert Dimension.COMPLETENESS not in clean  # not assessed, not zero


def test_creative_has_no_implicit_accuracy_check() -> None:
    criteria = [crit("C1", "expression")]
    s = dimension_scores(criteria, [verdict("C1", True)], n_errors=3, task_type=TaskType.CREATIVE)
    assert s == {Dimension.EXPRESSION: 1.0}


def test_overall_renormalises_over_assessed_dimensions() -> None:
    w = {"correctness": 0.2, "completeness": 0.2, "reasoning": 0.45, "expression": 0.15}
    s = {Dimension.REASONING: 1.0, Dimension.CORRECTNESS: 0.0}
    assert overall_score(s, w) == pytest.approx(0.45 / 0.65)


def test_band_labels() -> None:
    b = load_bands()
    assert [b.label(x) for x in (0.0, 0.39, 0.4, 0.7, 0.85, 1.0)] == [
        "Not yet",
        "Not yet",
        "Developing",
        "Proficient",
        "Strong",
        "Strong",
    ]


# ---------------------------------------------------------------- pipeline


def judge_reply(
    met: dict[str, bool],
    path: str = "P1",
    conf: float = 0.9,
    errors: int = 0,
    evidence: str = "heavy taxation",
) -> str:
    return json.dumps(
        {
            "identified_path": path,
            "path_confidences": [
                {"path_id": "P1", "confidence": conf},
                {"path_id": "P2", "confidence": 0.1},
            ],
            "addresses_question": True,
            "verdicts": [
                {
                    "criterion_id": k,
                    "met": v,
                    "evidence": evidence if v else "",
                    "justification": "j",
                }
                for k, v in met.items()
            ],
            "errors": [{"quote": "x", "explanation": "y"}] * errors,
        }
    )


@pytest.fixture
def env(
    make_client: Any, conn: sqlite3.Connection
) -> tuple[Any, RubricStore, QuestionStore, EvaluationStore]:
    role = {"temperature": 0.0, "max_output_tokens": 512}
    client = make_client(
        make_config(roles={"judge": {"provider": "alpha", "model": "j", "family": "a", **role}})
    )
    rubrics, questions = RubricStore(conn), QuestionStore(conn)
    r = make_rubric()  # analytical, P1 (C1 core, C2 non-core), P2 (C1 core)
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


def test_pipeline_scores_and_stores(env: Any, providers: dict[str, FakeProvider]) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply({"P1.C1": True, "P1.C2": True}))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)
    assert t.identified_path == "P1" and not t.low_confidence and t.judge_votes == 1
    assert t.bands[Dimension.REASONING] == "Strong"
    assert evals.get(t.evaluation_id).evaluation_id == t.evaluation_id
    assert "reference" not in providers["alpha"].requests[0].user.lower()


def test_low_confidence_flagged_for_amendment(env: Any, providers: dict[str, FakeProvider]) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply({"P1.C1": False, "P1.C2": False}, conf=0.2))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, amend=False)
    assert t.low_confidence and t.amendment_due


def test_unknown_path_and_missing_verdicts_are_repaired(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply({"P1.C1": True}, path="P9"))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)
    assert t.identified_path == "P1"  # highest-confidence valid path
    assert [v.criterion_id for v in t.verdicts] == ["P1.C1", "P1.C2"]
    assert not t.verdicts[1].met and "no verdict" in t.verdicts[1].justification


def test_hallucinated_evidence_is_downgraded_in_pipeline(
    env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply({"P1.C1": True, "P1.C2": True}, evidence="lead pipes"))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER)
    assert set(t.evidence_downgrades) == {"P1.C1", "P1.C2"}
    assert not any(v.met for v in t.verdicts)


def test_majority_vote_on_borderline(env: Any, providers: dict[str, FakeProvider]) -> None:
    client, rubrics, questions, evals = env
    # First call: the single core criterion unmet -> borderline -> two more votes, both met.
    providers["alpha"].push(
        judge_reply({"P1.C1": False, "P1.C2": True}),
        judge_reply({"P1.C1": True, "P1.C2": True}),
        judge_reply({"P1.C1": True, "P1.C2": True}),
    )
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, votes=3)
    assert t.judge_votes == 3 and t.verdicts[0].met


def test_clear_result_is_not_revoted(env: Any, providers: dict[str, FakeProvider]) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply({"P1.C1": True, "P1.C2": True}))
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, votes=3)
    assert t.judge_votes == 1 and len(providers["alpha"].requests) == 1


def test_creative_route(
    make_client: Any, conn: sqlite3.Connection, providers: dict[str, FakeProvider]
) -> None:
    role = {"temperature": 0.0, "max_output_tokens": 512}
    client = make_client(
        make_config(roles={"judge": {"provider": "alpha", "model": "j", "family": "a", **role}})
    )
    rubrics, questions, evals = RubricStore(conn), QuestionStore(conn), EvaluationStore(conn)
    path = make_rubric().paths[0].model_dump()
    r = Rubric.model_validate(
        {
            **make_rubric().model_dump(exclude={"hash"}),
            "rubric_id": "c1",
            "task_type": "creative",
            "shape": "craft_tests",
            "paths": [path],
            "obvious_answers": list("abcde"),
        }
    ).freeze()
    rubrics.save(r)
    assert r.hash
    questions.save(
        Question(
            question_id="qc",
            topic="x",
            text=r.question,
            task_type=TaskType.CREATIVE,
            rubric_id="c1",
            rubric_hash=r.hash,
        )
    )

    def creative(req: CompletionRequest) -> str:
        assert "Obvious answers" in req.user and "Path P" not in req.user
        return json.dumps(
            {
                "verdicts": [
                    {
                        "criterion_id": "P1.C1",
                        "met": True,
                        "evidence": "heavy taxation",
                        "justification": "j",
                    },
                    {"criterion_id": "P1.C2", "met": False, "evidence": "", "justification": "j"},
                ],
                "obvious_overlap": [2],
            }
        )

    providers["alpha"].push(creative)
    t = evaluate(client, rubrics, questions, evals, "qc", ANSWER)
    assert t.creative_route and t.identified_path is None and not t.low_confidence
    assert t.obvious_overlap == ["b"]
    assert Dimension.CORRECTNESS in t.dimension_scores  # P1.C2 is a correctness criterion
    assert t.dimension_scores[Dimension.CORRECTNESS] == 0.0  # no implicit accuracy check


def test_bands_object_used(env: Any, providers: dict[str, FakeProvider]) -> None:
    client, rubrics, questions, evals = env
    providers["alpha"].push(judge_reply({"P1.C1": True, "P1.C2": True}))
    strict = Bands([("Low", 0.0), ("High", 1.01)], amendment_confidence_threshold=0.95)
    t = evaluate(client, rubrics, questions, evals, "q1", ANSWER, bands=strict, amend=False)
    assert set(t.bands.values()) == {"Low"} and t.low_confidence


# ---------------------------------------------------------------- code checks from the golden set


def test_quotes_spanning_sentences_are_split() -> None:
    assert evidence_supported("Rome fell partly. This led to unpaid armies.", ANSWER)


def test_met_on_a_flagged_error_is_downgraded() -> None:
    vs = [
        verdict("C1", True, "carbohydrates, proteins and fats"),
        verdict("C2", True, "Carbohydrates are mainly used to build bones."),
    ]
    errs = [ClaimError(quote="Carbohydrates are mainly used to build bones", explanation="no")]
    out, down = apply_error_contradictions(vs, errs)
    assert down == ["C2"] and out[0].met and not out[1].met  # a shared noun is not enough


def test_sentence_range_parsing() -> None:
    assert sentence_range("Contains between three and eight sentences") == (3, 8)
    assert sentence_range("Is 3\u20135 sentences long") == (3, 5)
    assert sentence_range("Includes a tactile detail") is None


@pytest.mark.parametrize(
    ("text", "n"),
    [("One. Two! Three?", 3), ('He said "go." She went', 2), ("No stop at all", 1), ("", 0)],
)
def test_count_sentences(text: str, n: int) -> None:
    assert count_sentences(text) == n


def test_count_check_overrides_the_judge_both_ways() -> None:
    c = Criterion(
        criterion_id="P1.C1",
        dimension=Dimension.CORRECTNESS,
        statement="Contains between three and eight sentences",
        evidence_hint="",
        core=True,
        weight=1.0,
        requires="3 to 8 sentences",
    )
    ten = " ".join(f"Sentence {i}." for i in range(10))
    out, changed = apply_count_checks([verdict("P1.C1", True)], [c], ten)
    assert changed == ["P1.C1"] and not out[0].met
    out, changed = apply_count_checks([verdict("P1.C1", False)], [c], "A. B. C. D.")
    assert changed == ["P1.C1"] and out[0].met
