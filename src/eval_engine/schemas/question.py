from pydantic import BaseModel, Field

from eval_engine.schemas.common import TaskType


class Question(BaseModel):
    question_id: str = Field(min_length=1)
    topic: str
    text: str = Field(min_length=1)
    task_type: TaskType
    rubric_id: str
    # Written after the rubric is frozen; never passed to scoring or feedback prompts.
    reference_answer: str | None = None
