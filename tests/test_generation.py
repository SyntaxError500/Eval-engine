import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from eval_engine.config import load_weights
from eval_engine.generation.consistency import check_rubric, required_dimensions
from eval_engine.generation.generate import GenerationError, generate_question
from eval_engine.generation.review import build_batch, slots
from eval_engine.providers.base import CompletionRequest
from eval_engine.providers.fake import FakeProvider
from eval_engine.schemas import RubricDraft, TaskType
from eval_engine.storage import RubricStore
from eval_engine.storage.question_store import QuestionStore
from tests.conftest import make_config

WEIGHTS = load_weights()


def crit(cid: str, dim: str, core: bool = True, statement: str | None = None) -> dict[str, Any]:
    return {
        "criterion_id": cid,
        "dimension": dim,
        "statement": statement or f"States the idea checked by {cid}",
        "evidence_hint": "a sentence naming it",
        "core": core,
        "weight": 1.0 if core else 0.5,
    }


def draft(task_type: str = "analytical", **overrides: Any) -> dict[str, Any]:
    shapes = {
        "factual": "checklist",
        "analytical": "multi_path_claim_evidence",
        "explanatory": "multi_path",
        "creative": "craft_tests",
    }
    dims = ["correctness", "completeness", "reasoning", "expression"]
    n_paths = 2 if task_type in ("analytical", "explanatory") else 1
    paths = [
        {
            "path_id": f"P{p}",
            "description": f"Approach number {p}",
            "criteria": [crit(f"P{p}.C{i + 1}", d) for i, d in enumerate(dims)],
        }
        for p in range(1, n_paths + 1)
    ]
    data: dict[str, Any] = {
        "question": f"A {task_type} question?",
        "task_type": task_type,
        "shape": shapes[task_type],
        "paths": paths,
        "obvious_answers": [f"obvious {i}" for i in range(5)] if task_type == "creative" else [],
    }
    data.update(overrides)
    return data


def problems_for(data: dict[str, Any], requested: str | None = None) -> list[str]:
    req = TaskType(requested) if requested else None
    return check_rubric(RubricDraft.model_validate(data), WEIGHTS, req)


# ---------------------------------------------------------------- consistency checks


@pytest.mark.parametrize("task_type", ["factual", "analytical", "explanatory", "creative"])
def test_well_formed_drafts_pass(task_type: str) -> None:
    assert problems_for(draft(task_type), task_type) == []


def test_required_dimensions_follow_weights() -> None:
    assert required_dimensions(TaskType.FACTUAL, WEIGHTS) == {"correctness", "completeness"}
    assert "reasoning" in required_dimensions(TaskType.ANALYTICAL, WEIGHTS)
    assert required_dimensions(TaskType.CREATIVE, WEIGHTS) == {"correctness", "expression"}


def test_single_criterion_path_is_rejected() -> None:
    d = draft("factual")
    d["paths"][0]["criteria"] = [crit("P1.C1", "correctness")]
    assert any("partial answers" in p for p in problems_for(d))


def test_vague_judgement_words_rejected() -> None:
    d = draft("factual")
    d["paths"][0]["criteria"][0]["statement"] = "Gives a clear and well argued answer"
    found = [p for p in problems_for(d) if "judgement word" in p]
    assert found and "clear" in found[0] and "well" in found[0]


def test_word_inside_another_word_is_not_vague() -> None:
    d = draft("factual")
    d["paths"][0]["criteria"][0]["statement"] = "Names the wellspring of the river"
    assert not [p for p in problems_for(d) if "judgement word" in p]


def test_missing_required_dimension() -> None:
    d = draft("factual")
    d["paths"][0]["criteria"] = [crit("P1.C1", "correctness"), crit("P1.C2", "expression")]
    assert any("completeness" in p for p in problems_for(d))


def test_analytical_needs_core_reasoning() -> None:
    d = draft("analytical")
    for path in d["paths"]:
        for c in path["criteria"]:
            if c["dimension"] == "reasoning":
                c["core"] = False
    assert any("core reasoning" in p for p in problems_for(d))


def test_multi_path_types_need_two_distinct_paths() -> None:
    one = draft("explanatory")
    one["paths"] = one["paths"][:1]
    assert any("at least 2" in p for p in problems_for(one))
    same = draft("analytical")
    same["paths"][1]["description"] = same["paths"][0]["description"]
    assert any("same description" in p for p in problems_for(same))


def test_requested_task_type_mismatch() -> None:
    assert any("task_type must be" in p for p in problems_for(draft("factual"), "analytical"))


def test_duplicate_obvious_answers() -> None:
    d = draft("creative", obvious_answers=["a", "A", "b", "c", "d"])
    assert any("duplicates" in p for p in problems_for(d))


# ---------------------------------------------------------------- generation flow


def reference(req: CompletionRequest) -> str:
    return json.dumps({"path_id": "P1", "answer": "A model answer."})


@pytest.fixture
def gen_env(
    make_client: Any, providers: dict[str, FakeProvider], conn: sqlite3.Connection
) -> tuple[Any, RubricStore, QuestionStore]:
    role = {"temperature": 0.0, "max_output_tokens": 512}
    config = make_config(
        roles={
            "generator": {"provider": "alpha", "model": "gen", "family": "a", **role},
            "reference_answer": {"provider": "alpha", "model": "gen", "family": "a", **role},
        }
    )
    return make_client(config), RubricStore(conn), QuestionStore(conn)


def test_generate_freezes_stores_and_writes_reference(
    gen_env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions = gen_env
    providers["alpha"].push(json.dumps(draft("analytical")), reference)
    g = generate_question(client, rubrics, questions, "history", TaskType.ANALYTICAL)
    assert g.attempts == 1 and g.rubric.is_frozen
    stored = questions.get(g.question.question_id)
    assert stored.rubric_hash == g.rubric.hash and stored.reference_answer == "A model answer."
    assert rubrics.latest(stored.rubric_id).hash == g.rubric.hash
    # The reference prompt is given the frozen rubric, never a learner answer.
    assert "Path P1" in providers["alpha"].requests[-1].user


def test_failed_checks_get_one_retry_with_the_problems(
    gen_env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions = gen_env
    bad = draft("factual")
    bad["paths"][0]["criteria"] = [crit("P1.C1", "correctness")]
    providers["alpha"].push(json.dumps(bad), json.dumps(draft("factual")), reference)
    g = generate_question(client, rubrics, questions, "science", TaskType.FACTUAL)
    assert g.attempts == 2 and g.first_attempt_problems
    assert "rejected by automatic checks" in providers["alpha"].requests[1].user


def test_failing_twice_raises_and_stores_nothing(
    gen_env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions = gen_env
    bad = draft("factual")
    bad["paths"][0]["criteria"] = [crit("P1.C1", "correctness")]
    bad2 = {**bad, "question": "Another?"}  # differs so it isn't a cache hit
    bad3 = {**bad, "question": "A third?"}
    providers["alpha"].push(json.dumps(bad), json.dumps(bad2), json.dumps(bad3))
    with pytest.raises(GenerationError):
        generate_question(client, rubrics, questions, "science", TaskType.FACTUAL)
    assert questions.all() == []


def test_existing_questions_are_passed_as_avoid(
    gen_env: Any, providers: dict[str, FakeProvider]
) -> None:
    client, rubrics, questions = gen_env
    providers["alpha"].push(json.dumps(draft("factual")), reference)
    first = generate_question(client, rubrics, questions, "science", TaskType.FACTUAL)
    providers["alpha"].push(json.dumps(draft("factual", question="Q two?")), reference)
    generate_question(client, rubrics, questions, "science", TaskType.FACTUAL)
    gen_requests = [r for r in providers["alpha"].requests if "Topic:" in r.user]
    assert first.question.text in gen_requests[-1].user
    assert len(questions.all()) == 2


def test_batch_covers_slots_and_resumes(
    gen_env: Any, providers: dict[str, FakeProvider], tmp_path: Path
) -> None:
    client, rubrics, questions = gen_env

    def gen(req: CompletionRequest) -> str:
        task_type = req.user.split("Task type:", 1)[1].split()[0]
        return json.dumps(draft(task_type, question=f"{len(providers['alpha'].requests)}?"))

    providers["alpha"].push(*[gen, reference] * 4)
    summary = build_batch(client, rubrics, questions, per_type=1, out_dir=tmp_path)
    assert summary["built"] == 4 and summary["in_batch"] == 4
    assert (tmp_path / "review.md").read_text(encoding="utf-8").count("## ") == 4
    again = build_batch(client, rubrics, questions, per_type=1, out_dir=tmp_path)
    assert again["built"] == 0 and again["skipped"] == 4


def test_slots_are_distinct() -> None:
    s = slots(10, [f"t{i}" for i in range(10)])
    assert len(s) == 40 and len(set(s)) == 40


def test_batch_ignores_questions_from_older_prompt_versions(
    gen_env: Any, providers: dict[str, FakeProvider], tmp_path: Path
) -> None:
    client, rubrics, questions = gen_env

    def gen(req: CompletionRequest) -> str:
        task_type = req.user.split("Task type:", 1)[1].split()[0]
        return json.dumps(draft(task_type, question=f"{len(providers['alpha'].requests)}?"))

    providers["alpha"].push(*[gen, reference] * 8)
    build_batch(client, rubrics, questions, per_type=1, out_dir=tmp_path)
    for q in questions.all():  # pretend they came from an older prompt
        questions.save(q.model_copy(update={"generator_prompt_hash": "old"}))
    again = build_batch(client, rubrics, questions, per_type=1, out_dir=tmp_path)
    assert again["built"] == 4 and again["skipped"] == 0


@pytest.mark.parametrize(
    "statement",
    [
        "Uses between three and five sentences",
        "Answers in 3 to 8 sentences",
        "Presents the argument in a single sentence",
        "Keeps the answer under 100 words",
    ],
)
def test_length_criteria_rejected(statement: str) -> None:
    d = draft("factual")
    d["paths"][0]["criteria"][0]["statement"] = statement
    assert any("length" in p for p in problems_for(d))


def test_content_mentioning_sentence_is_fine() -> None:
    d = draft("factual")
    d["paths"][0]["criteria"][0]["statement"] = "Quotes the opening sentence of the speech"
    assert not [p for p in problems_for(d) if "length" in p]


@pytest.mark.parametrize(
    "question",
    [
        "Evaluate two different scientific explanations for why water expands when it freezes.",
        "Explain two distinct ways that wetlands help lessen flooding.",
        "Give two explanations: one that emphasizes energy use, and another on contrast.",
        "Evaluate two contrasting perspectives on how AI will affect employment.",
    ],
)
def test_questions_asking_for_several_alternatives_rejected(question: str) -> None:
    assert any(
        "several alternatives" in p for p in problems_for(draft("explanatory", question=question))
    )


@pytest.mark.parametrize(
    "question",
    [
        "Argue whether a basic income would reduce inequality, with two distinct arguments.",
        "Explain why smartphones use OLED rather than LCD displays.",
    ],
)
def test_single_answer_questions_allowed(question: str) -> None:
    assert not [p for p in problems_for(draft("analytical", question=question)) if "several" in p]


def test_creative_length_constraint_is_allowed() -> None:
    d = draft("creative")
    d["paths"][0]["criteria"][0]["statement"] = "The scene is between 120 and 150 words"
    d["paths"][0]["criteria"][0]["dimension"] = "correctness"
    d["paths"][0]["criteria"][0]["statement"] = "Keeps the scene to 3 to 5 sentences"
    assert not [p for p in problems_for(d) if "length" in p]
