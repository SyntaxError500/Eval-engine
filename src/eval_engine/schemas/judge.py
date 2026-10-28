"""Structured output of the merged path-identification + scoring call."""

from pydantic import BaseModel, Field


class PathConfidence(BaseModel):
    path_id: str
    confidence: float = Field(ge=0.0, le=1.0)


class Verdict(BaseModel):
    criterion_id: str
    met: bool
    evidence: str = Field(description="Verbatim quote from the answer; empty if none")
    justification: str


class ClaimError(BaseModel):
    """A wrong statement in the answer. Rubric criteria are positive ("mentions X"), so a
    false claim alongside the right ideas would otherwise go unpenalised."""

    quote: str = Field(description="Verbatim quote of the wrong statement")
    explanation: str


class JudgeOutput(BaseModel):
    # A list rather than a dict: dynamic-key objects are poorly supported by structured output.
    identified_path: str | None = Field(description="null for creative tasks")
    path_confidences: list[PathConfidence]
    verdicts: list[Verdict]
    errors: list[ClaimError] = Field(
        default_factory=list, description="Factually wrong or contradictory statements"
    )

    def max_confidence(self) -> float:
        return max((p.confidence for p in self.path_confidences), default=0.0)
