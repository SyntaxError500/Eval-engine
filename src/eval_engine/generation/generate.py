"""Stage 1 pipeline: generate -> check -> (one retry with the problems) -> freeze -> store ->
reference answer. Nothing here ever sees a learner's answer."""

import uuid
from dataclasses import dataclass, field
from typing import Any

from eval_engine.config import load_weights
from eval_engine.generation.consistency import check_rubric, required_dimensions
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.common import TaskType
from eval_engine.schemas.question import Question, ReferenceAnswer
from eval_engine.schemas.rubric import Rubric, RubricDraft
from eval_engine.storage.question_store import QuestionStore
from eval_engine.storage.rubric_store import RubricStore

MAX_AVOID = 20  # most recent questions on the topic passed as "write something different"


class GenerationError(Exception):
    """The generator could not produce a rubric that passes the checks in two attempts."""

    def __init__(self, message: str, problems: list[str]) -> None:
        super().__init__(message)
        self.problems = problems


@dataclass
class GeneratedQuestion:
    question: Question
    rubric: Rubric
    attempts: int
    first_attempt_problems: list[str] = field(default_factory=list)


def generate_question(
    client: LLMClient,
    rubrics: RubricStore,
    questions: QuestionStore,
    topic: str,
    task_type: TaskType,
    *,
    weights: dict[str, dict[str, float]] | None = None,
) -> GeneratedQuestion:
    weights = weights or load_weights()
    # Existing questions on the topic go into the prompt, for variety. They also make each
    # request distinct, so the response cache can't hand back a question already stored.
    avoid = [q.text for q in questions.by_topic(topic)][-MAX_AVOID:]
    variables: dict[str, Any] = {
        "topic": topic,
        "task_type": task_type.value,
        "required_dimensions": sorted(required_dimensions(task_type, weights)),
        "avoid": avoid,
        "problems": [],
    }

    first_problems: list[str] = []
    draft: RubricDraft | None = None
    for attempt in (1, 2):
        draft = client.complete("generator", "generate", variables, RubricDraft).value
        problems = check_rubric(draft, weights, task_type)
        if not problems:
            break
        if attempt == 1:
            first_problems = problems
            variables = {**variables, "problems": problems}
        else:
            raise GenerationError(
                f"rubric for {topic}/{task_type.value} failed checks twice", problems
            )
    assert draft is not None

    question_id = uuid.uuid4().hex[:12]
    rubric = Rubric.model_validate(
        {
            **draft.model_dump(),
            "rubric_id": f"q-{question_id}",
            "topic": topic,
            "version": 1,
            "source": "generated",
        }
    ).freeze()
    rubrics.save(rubric)
    assert rubric.hash is not None
    question = Question(
        question_id=question_id,
        topic=topic,
        text=draft.question,
        task_type=draft.task_type,
        rubric_id=rubric.rubric_id,
        rubric_hash=rubric.hash,
    )
    questions.save(question)
    question = write_reference(client, questions, question, rubric)
    return GeneratedQuestion(question, rubric, 2 if first_problems else 1, first_problems)


def write_reference(
    client: LLMClient, questions: QuestionStore, question: Question, rubric: Rubric
) -> Question:
    """Written against the already-frozen rubric (design §4, step 5). Display only."""
    ref = client.complete(
        "reference_answer",
        "reference_answer",
        {"question": question.text, "paths": [p.model_dump(mode="json") for p in rubric.paths]},
        ReferenceAnswer,
    ).value
    valid_path = ref.path_id in {p.path_id for p in rubric.paths}
    updated = question.model_copy(
        update={
            "reference_answer": ref.answer,
            "reference_path_id": ref.path_id if valid_path else None,
        }
    )
    questions.save(updated)
    return updated
