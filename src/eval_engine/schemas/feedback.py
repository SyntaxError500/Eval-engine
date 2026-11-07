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


TutorKind = Literal["question", "challenge", "acknowledgement", "other"]


class TutorReply(BaseModel):
    """One reply in a discussion of a graded answer (Phase 8 app). Never changes the grade.

    The model restates the learner's point and classifies it before replying: the 8B tutor
    otherwise answered the original feedback instead of the message (seen live, 2026-11-07)."""

    learner_point: str = Field(description="The learner's latest message in one sentence")
    kind: TutorKind
    accepts: list[str] = Field(
        default_factory=list,
        description="Corrections the learner now accepts, in a few words each; [] if none",
    )
    reply: str = Field(min_length=1)


RecheckDecision = Literal["uphold", "revise"]


class CriterionRecheck(BaseModel):
    criterion_id: str
    decision: RecheckDecision
    evidence: str = Field(description="Exact words from the answer that meet it; '' if upheld")
    reason: str


class ErrorRecheck(BaseModel):
    error: int = Field(description="1-based number of the listed wrong statement")
    stands: bool
    reason: str


class RecheckOutput(BaseModel):
    """A second look at the decisions a learner disputes, by the judge model (never the
    local tutor). It can only reconsider what counted against the answer."""

    criteria: list[CriterionRecheck]
    errors: list[ErrorRecheck] = Field(default_factory=list)
    correct_parts: list[str] = Field(description="What the answer gets right")
    incorrect_statement: str | None = Field(
        default=None, description="The exact wrong statement, quoted; null if none"
    )
    severity: Literal["none", "minor", "significant"]
    rubric_concern: str | None = Field(
        default=None, description="The learner argues a requirement shouldn't be asked for"
    )
    summary: str
