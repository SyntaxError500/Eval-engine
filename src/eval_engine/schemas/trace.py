"""Audit records. `LLMCall` is written for every model call; `EvaluationTrace` per evaluation."""

from datetime import datetime

from pydantic import BaseModel, Field

from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.feedback import Feedback
from eval_engine.schemas.judge import ClaimError, PathConfidence, Verdict


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
    # The judge said the answer tries to answer the question (None on the creative route).
    addresses_question: bool | None = None
    # The conditions for amendment held (it can be skipped, as in the golden run).
    amendment_due: bool = False
    amendment_fired: bool = False
    amendment_proposal: str | None = None
    verifier_verdict: bool | None = None
    verifier_reasoning: str | None = None
    verifier_failure_type: str | None = None
    verifier_framing: str | None = None
    # Why the answer stayed on the original rubric; feedback reports it (design doc §15).
    divergence_reason: str | None = None
    # The stage couldn't finish (provider down, quota); the original rubric stands.
    amendment_error: str | None = None
    final_rubric_source: str
    verdicts: list[Verdict] = Field(default_factory=list)
    errors: list[ClaimError] = Field(default_factory=list)
    # Criteria the judge marked met whose evidence quote isn't in the answer; downgraded.
    evidence_downgrades: list[str] = Field(default_factory=list)
    # Criteria the judge marked met on a statement its own errors list calls wrong; downgraded.
    contradiction_downgrades: list[str] = Field(default_factory=list)
    # Sentence-count criteria decided in code, overriding the judge (LLMs miscount).
    count_overrides: list[str] = Field(default_factory=list)
    # First judge call's max path confidence was below the threshold (non-creative).
    low_confidence: bool = False
    # Creative only: obvious answers the response substantially reuses. Feedback signal,
    # never scored, because briefs don't state originality as a requirement (Phase 3 rule).
    obvious_overlap: list[str] = Field(default_factory=list)
    # Judge calls whose verdicts were combined (1, or 3 under the D6 majority vote).
    judge_votes: int = 1
    dimension_scores: dict[Dimension, float] = Field(default_factory=dict)
    # Weighted over the dimensions the path covers. Internal only (validation metrics);
    # never shown to a learner as a single score (design doc §12).
    overall_score: float | None = None
    bands: dict[Dimension, str] = Field(default_factory=dict)
    # Learner-facing feedback (Phase 6); None when the caller didn't ask for it.
    feedback: Feedback | None = None
    call_ids: list[str] = Field(default_factory=list)
