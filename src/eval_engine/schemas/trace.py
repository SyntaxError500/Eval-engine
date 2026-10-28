"""Audit records. `LLMCall` is written for every model call; `EvaluationTrace` per evaluation."""

from datetime import datetime

from pydantic import BaseModel, Field

from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.judge import PathConfidence, Verdict


class LLMCall(BaseModel):
    call_id: str
    timestamp: datetime
    role: str
    provider: str
    model: str
    prompt_name: str
    prompt_version: int
    prompt_hash: str
    request_key: str
    cache_hit: bool
    repaired: bool = False
    attempts: int = 1
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    error: str | None = None
    # Provider errors from attempts that were retried (or the final one), oldest first.
    retry_errors: list[str] = Field(default_factory=list)
    evaluation_id: str | None = None


class EvaluationTrace(BaseModel):
    """Everything needed to audit one score (design doc §15). Filled in from Phase 4 on."""

    evaluation_id: str
    timestamp: datetime
    question_id: str
    task_type: TaskType
    rubric_hash_original: str
    rubric_hash_used: str
    creative_route: bool
    path_confidences: list[PathConfidence] = Field(default_factory=list)
    identified_path: str | None = None
    amendment_fired: bool = False
    amendment_proposal: str | None = None
    verifier_verdict: bool | None = None
    verifier_reasoning: str | None = None
    verifier_framing: str | None = None
    final_rubric_source: str
    verdicts: list[Verdict] = Field(default_factory=list)
    dimension_scores: dict[Dimension, float] = Field(default_factory=dict)
    bands: dict[Dimension, str] = Field(default_factory=dict)
    feedback_items: list[str] = Field(default_factory=list)
    call_ids: list[str] = Field(default_factory=list)
