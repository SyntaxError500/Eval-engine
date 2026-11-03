"""Deterministic selection of what the feedback says (plan Phase 6, design doc §11).

Problems: failed criteria on the path used, plus the factual errors the judge listed (a false
statement costs correctness through the implicit no-errors check, so the learner is told about
it). Ranked core first, then by criterion weight x the task type's dimension weight. Two or
three problems, then one or two things that worked, so the learner keeps them.

One mistake often fails several criteria, and listing each would say the same thing three
times (first review-set run: "vitamins are a macronutrient" became three points). So points
are merged when:
- a criterion depends on another: it names it ("the phase named in C5"), or refers back to what
  it asks for ("explains how the example ..." after "provides a specific example"; external
  review 1, E16, where they became two points and the second misread the answer);
- the judge's note on a failed criterion is about one of its listed errors;
- two criteria are near-identical ("a first distinct reason" / "a second distinct reason").
"""

import re
from dataclasses import dataclass, field, replace
from difflib import SequenceMatcher
from typing import Literal

from eval_engine.evaluation.aggregate import NO_ERRORS_WEIGHT
from eval_engine.evaluation.counts import count_sentences, sentence_range
from eval_engine.evaluation.evidence import needs_evidence, same_statement
from eval_engine.schemas.common import Dimension
from eval_engine.schemas.judge import ClaimError
from eval_engine.schemas.rubric import Criterion
from eval_engine.schemas.trace import EvaluationTrace

MAX_PROBLEMS = 3  # a third only when it is core: "two or three", without diluting the first two
MAX_WORKED = 2
DUPLICATE_RATIO = 0.75  # statement similarity at which two criteria make one point
UNSURE_DIVERGENCE = "proposal failed the rubric checks"  # a system outcome, not a reason
# A failed criterion's note is about a listed error if it shares a run of this many words with
# the error's quote, or at least this many content words with its quote and explanation.
ERROR_RUN = 3
ERROR_WORDS = 3

_CODE_PREFIX = re.compile(r"^\[(?P<tag>[^\]]*)\]\s*")
_COUNTED = re.compile(r"counted in code: (\d+) sentences")
_DEPENDS_ON = re.compile(r"\bC(\d+)\b")
_REFERS_BACK = re.compile(r"\bthe (example|evidence|fact|event|case|quotation|quote)\b", re.I)
_WORD = re.compile(r"[a-z0-9]+")
_STOP = frozenset(
    (  # noqa: SIM905 (one string reads better than a 50-line list)
        "the and for that this with not are was its all has have had from into than rather answer "
        "does but which instead their there also any one two who what when why how about only "
        "student learner states mentions provides gives"
    ).split()
)


@dataclass(frozen=True)
class Point:
    kind: Literal["criterion", "error"]
    refs: tuple[str, ...]
    statement: str  # what the criterion asks for, or the wrong statement itself
    reason: str  # what the grader noted; "" when it can't be shown to the learner
    evidence: str  # the answer's own words, when there are any
    core: bool
    priority: float
    also: tuple[str, ...] = ()  # requirements of criteria merged into this point


@dataclass
class Selection:
    improve: list[Point] = field(default_factory=list)
    worked: list[Point] = field(default_factory=list)
    off_topic: bool = False
    obvious: list[str] = field(default_factory=list)  # creative: reused obvious answers
    approach: Literal["accepted", "rejected"] | None = None
    divergence_reason: str | None = None


def select(
    trace: EvaluationTrace,
    criteria: list[Criterion],
    dimension_weights: dict[str, float],
    answer: str,
) -> Selection:
    if trace.addresses_question is False:
        # Every criterion fails for the same single reason; listing them would bury it.
        return Selection(off_topic=True)

    by_id = {c.criterion_id: c for c in criteria}
    failed: list[Point] = []
    met: list[Point] = []
    for v in trace.verdicts:
        c = by_id.get(v.criterion_id)
        if c is None or v.criterion_id in trace.contradiction_downgrades:
            continue  # a met verdict resting on a wrong statement is told as that error
        reason = _learner_reason(v.justification, v.met)
        if sentence_range(c.statement) is not None:
            # Models miscount (Phase 4); the learner gets the code's count, met or not.
            reason = f"The answer has {count_sentences(answer)} sentences."
        priority = c.weight * dimension_weights.get(c.dimension.value, 0.0)
        point = Point(
            "criterion", (c.criterion_id,), c.statement, reason, v.evidence, c.core, priority
        )
        (met if v.met else failed).append(point)

    errors = _error_points(trace, dimension_weights)
    failed, errors = _absorb_into_errors(failed, errors, trace)
    improve = _ranked(_merge_duplicates(_merge_dependents([*failed, *errors], refers_back=True)))
    # Something the answer did beats an absence ("does not use any of ...") as what worked.
    worked = _ranked(_merge_duplicates(_merge_dependents(met, refers_back=False)))
    worked = sorted(
        [p for p in worked if p.core] or worked[:1],
        key=lambda p: not needs_evidence(by_id[p.refs[0]]),
    )
    selection = Selection(
        improve=_top(improve, MAX_PROBLEMS, third_needs_core=True),
        worked=_top(worked, MAX_WORKED, third_needs_core=False),
        obvious=list(trace.obvious_overlap),
    )
    if trace.amendment_fired:
        if trace.final_rubric_source == "amendment" and trace.verifier_verdict:
            selection.approach = "accepted"
        elif (
            trace.divergence_reason
            and not trace.amendment_error
            and not trace.divergence_reason.startswith(UNSURE_DIVERGENCE)
        ):
            selection.approach = "rejected"
            selection.divergence_reason = trace.divergence_reason
    return selection


def _error_points(trace: EvaluationTrace, dimension_weights: dict[str, float]) -> list[Point]:
    correctness = dimension_weights.get(Dimension.CORRECTNESS.value, 0.0)
    points = []
    for n, e in enumerate(trace.errors, start=1):
        merged = tuple(
            cid
            for cid in trace.contradiction_downgrades
            if any(
                v.criterion_id == cid and same_statement(v.evidence, e.quote)
                for v in trace.verdicts
            )
        )
        points.append(
            Point(
                "error",
                (f"error:{n}", *merged),
                e.quote,
                e.explanation,
                e.quote,
                True,
                NO_ERRORS_WEIGHT * correctness,
            )
        )
    return points


def _absorb_into_errors(
    failed: list[Point], errors: list[Point], trace: EvaluationTrace
) -> tuple[list[Point], list[Point]]:
    """A failed criterion whose note is about a listed error is told as part of that error."""
    if not errors:
        return failed, errors
    claims = trace.errors
    kept: list[Point] = []
    errors = list(errors)
    for p in failed:
        overlaps = [_about(p.reason, claim) for claim in claims]
        best = max(range(len(claims)), key=lambda i: overlaps[i])
        if overlaps[best] > 0:
            e = errors[best]
            errors[best] = replace(e, refs=e.refs + p.refs, also=(*e.also, p.statement))
        else:
            kept.append(p)
    return kept, errors


def _about(note: str, claim: ClaimError) -> int:
    """How strongly a criterion note is about an error: 0 means not about it."""
    note_words = _WORD.findall(note.lower())
    quote_words = _WORD.findall(claim.quote.lower())
    runs = {tuple(note_words[i : i + ERROR_RUN]) for i in range(len(note_words) - ERROR_RUN + 1)}
    shared_run = any(
        tuple(quote_words[i : i + ERROR_RUN]) in runs
        for i in range(len(quote_words) - ERROR_RUN + 1)
    )
    shared = _content(note) & _content(f"{claim.quote} {claim.explanation}")
    if shared_run or len(shared) >= ERROR_WORDS:
        return len(shared) + 1
    return 0


def _content(text: str) -> set[str]:
    words = (w.rstrip("s") for w in _WORD.findall(text.lower()) if len(w) >= 3)
    return {w for w in words if w not in _STOP}


def _merge_dependents(points: list[Point], *, refers_back: bool) -> list[Point]:
    """'... in the phase named in C5' is part of C5's point, and 'explains how the example ...'
    is part of the point asking for an example, when both are in the same list: with the first
    missing, the second can't be met either, so it isn't a separate problem. Among met criteria
    giving and explaining an example are two achievements, so `refers_back` is off there."""
    by_suffix = {p.refs[0].rsplit(".", 1)[-1]: i for i, p in enumerate(points)}
    out = list(points)
    absorbed: set[int] = set()
    for i, p in enumerate(points):
        if p.kind != "criterion":
            continue
        hosts = [by_suffix.get(f"C{n}") for n in _DEPENDS_ON.findall(p.statement)]
        for noun in _REFERS_BACK.findall(p.statement) if refers_back else []:
            hosts += [j for j, q in enumerate(points) if j < i and _introduces(q.statement, noun)]
        for j in hosts:
            if j is not None and j != i and j not in absorbed and points[j].kind == "criterion":
                host = out[j]
                out[j] = replace(host, refs=host.refs + p.refs, also=(*host.also, p.statement))
                absorbed.add(i)
                break
    return [p for i, p in enumerate(out) if i not in absorbed]


def _introduces(statement: str, noun: str) -> bool:
    """'Provides a specific historical example' introduces 'the example'."""
    pattern = rf"\b(?:a|an|one)(?:\s+[\w-]+){{0,3}}\s+{re.escape(noun.lower())}\b"
    return re.search(pattern, statement, re.IGNORECASE) is not None


def _learner_reason(justification: str, met: bool) -> str:
    """The judge's note, unless a code check overturned it: an overturned "met" verdict still
    carries the judge's reasons for passing, which would explain a failure backwards."""
    m = _CODE_PREFIX.match(justification)
    if m is None:
        return justification
    counted = _COUNTED.search(m.group("tag"))
    if counted:
        return f"The answer has {counted.group(1)} sentences."
    return "" if not met else justification[m.end() :]


def _ranked(points: list[Point]) -> list[Point]:
    # Stable: on equal rank, errors come before criteria and criteria keep rubric order.
    return sorted(points, key=lambda p: (not p.core, -p.priority, p.kind != "error"))


def _merge_duplicates(points: list[Point]) -> list[Point]:
    out: list[Point] = []
    for p in points:
        twin = next((i for i, q in enumerate(out) if _duplicate(p, q)), None)
        if twin is None:
            out.append(p)
        else:
            kept = out[twin]
            out[twin] = replace(kept, refs=kept.refs + p.refs, also=(*kept.also, *p.also))
    return out


def _duplicate(a: Point, b: Point) -> bool:
    if a.kind != "criterion" or b.kind != "criterion":
        return False
    return SequenceMatcher(None, a.statement.lower(), b.statement.lower()).ratio() >= (
        DUPLICATE_RATIO
    )


def _top(points: list[Point], limit: int, *, third_needs_core: bool) -> list[Point]:
    picked = points[: min(limit, 2)]
    if limit > 2 and len(points) > 2 and (points[2].core or not third_needs_core):
        picked.append(points[2])
    return picked
