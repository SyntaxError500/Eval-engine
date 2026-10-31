from pydantic import BaseModel, Field

from eval_engine.schemas.common import TaskType


class Question(BaseModel):
    question_id: str = Field(min_length=1)
    topic: str
    text: str = Field(min_length=1)
    task_type: TaskType
    rubric_id: str
    rubric_hash: str  # the frozen version-1 rubric this question was generated with
    # Written after the rubric is frozen; never passed to scoring or feedback prompts.
    reference_answer: str | None = None
    reference_path_id: str | None = None


class ReferenceAnswer(BaseModel):
    """Generator output for the reference answer, written against the frozen rubric."""

    path_id: str = Field(description="The rubric path this answer follows")
    answer: str = Field(min_length=1)
