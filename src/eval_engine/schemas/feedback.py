"""Learner-facing feedback (design doc §11, plan Phase 6)."""

from typing import Literal

from pydantic import BaseModel, Field

# Display order: a note on the route comes first (design doc §15), then the problems, then
# what worked, so the learner doesn't rewrite the parts that were right.
FeedbackKind = Literal["approach", "divergence", "off_topic", "improve", "originality", "worked"]


class FeedbackItem(BaseModel):
    kind: FeedbackKind
    text: str
    # Rubric criterion ids, or "error:<n>" for a factual error the judge listed (1-based).
    refs: list[str] = Field(default_factory=list)
    # "model" = phrased by the feedback model; "template" = a code fallback after a failed
    # check; "fixed" = always this wording (the accepted-route note).
    source: Literal["model", "template", "fixed"]


class Feedback(BaseModel):
    items: list[FeedbackItem]
    call_ids: list[str] = Field(default_factory=list)
    # Why a phrased item was replaced by its template, one entry per replacement.
    fallbacks: list[str] = Field(default_factory=list)


class PhrasedPoint(BaseModel):
    ref: str = Field(description="The point's label, e.g. I1 or W2")
    text: str


class PhrasedFeedback(BaseModel):
    """Structured output of the feedback model."""

    points: list[PhrasedPoint]
    divergence: str | None = Field(description="Only when a different route was asked for")
    off_topic: str | None = Field(description="Only when the answer is about something else")
