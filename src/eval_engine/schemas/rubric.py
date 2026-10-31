"""Rubric schemas.

`RubricDraft` is what the generator model returns. `Rubric` is the stored, versioned,
hash-frozen form. Structural invariants live here so a malformed generator reply fails
validation (and gets one repair attempt) instead of reaching the store.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eval_engine.hashing import hash_data
from eval_engine.schemas.common import (
    OBVIOUS_ANSWER_COUNT,
    SHAPE_FOR_TASK,
    SINGLE_PATH_SHAPES,
    Dimension,
    RubricShape,
    TaskType,
)


class Criterion(BaseModel):
    model_config = ConfigDict(frozen=True)

    criterion_id: str = Field(min_length=1)
    dimension: Dimension
    statement: str = Field(min_length=1, description="Binary, observable statement")
    evidence_hint: str = Field(description="What in an answer would show this is met")
    core: bool = Field(description="Core criteria outrank stylistic ones in feedback")
    weight: float = Field(gt=0, le=10)
    # Exact words of the question that ask for this criterion (traceability, review 1 cause A).
    # Left out of dumps when None, so rubrics stored before this field keep their hashes.
    requires: str | None = Field(
        default=None,
        exclude_if=lambda v: v is None,
        description="Exact words quoted from the question that ask for this; null only for "
        "creative craft tests (turn, show-don't-tell, clichés)",
    )


class SolutionPath(BaseModel):
    model_config = ConfigDict(frozen=True)

    path_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    criteria: list[Criterion] = Field(min_length=1)


class RubricDraft(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str = Field(min_length=1)
    task_type: TaskType
    shape: RubricShape
    paths: list[SolutionPath] = Field(min_length=1)
    obvious_answers: list[str] = Field(
        default_factory=list, description="Creative tasks only: the most obvious answers"
    )

    @model_validator(mode="after")
    def _check_structure(self) -> Self:
        expected = SHAPE_FOR_TASK[self.task_type]
        if self.shape != expected:
            raise ValueError(
                f"task_type {self.task_type} requires shape {expected}, got {self.shape}"
            )
        if self.shape in SINGLE_PATH_SHAPES and len(self.paths) != 1:
            raise ValueError(f"shape {self.shape} must have exactly one path")

        path_ids = [p.path_id for p in self.paths]
        if len(set(path_ids)) != len(path_ids):
            raise ValueError("path_id values must be unique")
        criterion_ids = [c.criterion_id for p in self.paths for c in p.criteria]
        if len(set(criterion_ids)) != len(criterion_ids):
            raise ValueError("criterion_id values must be unique across the rubric")

        if self.task_type == TaskType.CREATIVE:
            if len(self.obvious_answers) != OBVIOUS_ANSWER_COUNT:
                raise ValueError(
                    f"creative rubrics need exactly {OBVIOUS_ANSWER_COUNT} obvious_answers"
                )
        elif self.obvious_answers:
            raise ValueError("obvious_answers is only allowed for creative tasks")
        return self


class Rubric(RubricDraft):
    """Stored rubric. Immutable; a change is a new version with `parent_hash` set."""

    rubric_id: str = Field(min_length=1)
    topic: str
    version: int = Field(ge=1)
    parent_hash: str | None = None
    source: Literal["generated", "amendment", "dataset"]
    hash: str | None = None

    def compute_hash(self) -> str:
        return hash_data(self.model_dump(mode="json", exclude={"hash"}))

    def freeze(self) -> "Rubric":
        return self.model_copy(update={"hash": self.compute_hash()})

    @property
    def is_frozen(self) -> bool:
        return self.hash is not None and self.hash == self.compute_hash()

    def path(self, path_id: str) -> SolutionPath:
        for p in self.paths:
            if p.path_id == path_id:
                return p
        raise KeyError(path_id)
