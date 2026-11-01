"""Structured output of the amendment stage (design doc §7-8, plan Phase 5)."""

from typing import Literal

from pydantic import BaseModel, Field

from eval_engine.schemas.common import Dimension

FailureType = Literal["factual_error", "invalid_inference", "missing_step", "duplicate_path"]
Framing = Literal["adversarial", "neutral"]


class ProposedCriterion(BaseModel):
    """Ids and weights are assigned in code, so a proposal can't weight its own criteria."""

    dimension: Dimension
    statement: str = Field(min_length=1, description="Binary, observable statement")
    evidence_hint: str = Field(description="What in an answer would show this is met")
    core: bool
    requires: str = Field(description="Exact words of the question that ask for this")


class ProposedPath(BaseModel):
    description: str = Field(min_length=1, description="One sentence naming the approach")
    criteria: list[ProposedCriterion] = Field(min_length=1)


class AmendmentProposal(BaseModel):
    is_new_valid_approach: bool
    proposed_path: ProposedPath | None = Field(description="null unless is_new_valid_approach")
    justification: str


class VerifierVerdict(BaseModel):
    accept: bool
    failure_type: FailureType | None = Field(description="null when accepting")
    reasons: str = Field(description="At most two sentences")

    @property
    def accepted(self) -> bool:
        """A verdict that names a failure is a rejection, whatever `accept` says."""
        return self.accept and self.failure_type is None
