"""Fact-check pass on a draft rubric by a model from a different family than the generator.

The generator can't reliably check its own facts: review 1 found wrong science inside paths
(candle flame from "hot gases", GIP from L cells), a false premise (ozone "emitted") and a
path missing half of what the question asked. Errors go back to the generator as problems.
"""

from typing import Literal

from pydantic import BaseModel, Field

from eval_engine.providers.client import LLMClient
from eval_engine.schemas.rubric import RubricDraft


class FactIssue(BaseModel):
    location: str = Field(description='"question", a path id, a criterion id, or "obvious_answers"')
    severity: Literal["error", "doubt"]
    problem: str = Field(description="What is wrong and what is correct")


class FactCheck(BaseModel):
    issues: list[FactIssue]


def fact_check(client: LLMClient, draft: RubricDraft) -> FactCheck:
    return client.complete(
        "fact_checker",
        "fact_check",
        {
            "question": draft.question,
            "task_type": draft.task_type.value,
            "paths": [p.model_dump(mode="json") for p in draft.paths],
            "obvious_answers": draft.obvious_answers,
        },
        FactCheck,
    ).value


def as_problems(check: FactCheck) -> list[str]:
    return [
        f"fact check ({i.location}): {i.problem}" for i in check.issues if i.severity == "error"
    ]
