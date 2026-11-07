"""Discussing a graded answer (Phase 8 app): the tutor's inputs, its code checks, and the
re-check of disputed decisions. Pure functions; `service.py` makes the calls and stores turns.

Why this exists (live Java session, 2026-11-07): across 7 objections the tutor gave 3 replies
word for word identical to earlier ones and never answered the learner's argument. Causes:
- the history went into the prompt as a transcript, and the 8B model copied its own last
  reply out of it; nothing checked for that;
- the tutor wasn't told how the bands were reached, and was forbidden to talk about them, so
  "why is correctness Not yet?" had no answer it could give;
- the grade is fixed and the tutor can't change it, and nothing else could, so a learner
  with a fair point met a wall and the model fell back to restating the correction.
So: the tutor gets the grade breakdown and what has been said and settled; code rejects
near-repeats and claims that a result changed; and a dispute can go to one re-check by the
judge model (never the local tutor), which can reverse a decision only with a quote.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from eval_engine.evaluation.aggregate import Bands, dimension_scores
from eval_engine.evaluation.evidence import evidence_supported, same_statement
from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.feedback import RecheckOutput
from eval_engine.schemas.rubric import Criterion, Rubric
from eval_engine.schemas.trace import EvaluationTrace

# A reply sharing this share of its word triples with an earlier reply is a repeat. Measured on
# the Java session's 7 replies: word-for-word copies 0.89-1.00, the same correction reworded
# 0.39-0.67. A lexical check can't catch every paraphrase; the prompt's settled points and
# earlier replies handle those.
REPEAT_THRESHOLD = 0.5
EARLIER_SHOWN = 4  # earlier tutor replies listed as "don't repeat"
MAX_SETTLED = 8
TUTOR_ATTEMPTS = 2
NO_ERRORS_CHECK = "Makes no wrong statements"

FALLBACK_REPLY = (
    "I've already explained my view on this and have nothing new to add, so I won't repeat it. "
    "If you think a decision is wrong, ask for a re-check below the chat: the grader looks at "
    "the disputed decisions once more, and your argument is saved for review."
)

_CLAIMS_CHANGE = re.compile(
    r"\b(i('ve| have| will|'ll)? (now )?(changed|updated|raised|revised|adjusted|increased)"
    r"|(your|the) (grade|result|band|mark|score)s? (is|are|has been|have been|will be) "
    r"(now )?(changed|updated|raised|revised|adjusted|increased))\b",
    re.IGNORECASE,
)
_WORD = re.compile(r"[a-z0-9']+")


def path_criteria(trace: EvaluationTrace, rubric: Rubric) -> list[Criterion]:
    path_id = trace.identified_path or rubric.paths[0].path_id
    return list(rubric.path(path_id).criteria)


def grade_breakdown(trace: EvaluationTrace, criteria: list[Criterion]) -> list[dict[str, Any]]:
    """Per assessed dimension: its band and every check behind it, including the code's
    'no wrong statements' check on correctness, so the tutor can say why a band is what it is."""
    verdicts = {v.criterion_id: v for v in trace.verdicts}
    checks: dict[Dimension, list[dict[str, Any]]] = {}
    for c in criteria:
        v = verdicts.get(c.criterion_id)
        if v is not None:
            checks.setdefault(c.dimension, []).append(
                {"met": v.met, "statement": c.statement, "note": v.justification}
            )
    if trace.task_type != TaskType.CREATIVE:
        note = "; ".join(f'"{e.quote}" - {e.explanation}' for e in trace.errors)
        checks.setdefault(Dimension.CORRECTNESS, []).append(
            {"met": not trace.errors, "statement": NO_ERRORS_CHECK, "note": note}
        )
    return [
        {"name": d.value, "band": trace.bands[d], "checks": cs}
        for d, cs in checks.items()
        if d in trace.bands
    ]


def _triples(text: str) -> set[tuple[str, ...]]:
    words = _WORD.findall(text.lower())
    return {tuple(words[i : i + 3]) for i in range(len(words) - 2)}


def repeat_of(reply: str, earlier: list[str]) -> str | None:
    """The earlier reply this one mostly repeats, if any."""
    mine = _triples(reply)
    if not mine:
        return None
    for e in earlier:
        theirs = _triples(e)
        if theirs and len(mine & theirs) / min(len(mine), len(theirs)) >= REPEAT_THRESHOLD:
            return e
    return None


def reply_problems(reply: str, earlier: list[str], learner_point: str) -> list[str]:
    problems = []
    if (prev := repeat_of(reply, earlier)) is not None:
        problems.append(
            f'It repeats your earlier reply ("{prev[:80]}..."). Say something new that answers '
            f"their latest point: {learner_point}"
        )
    if _CLAIMS_CHANGE.search(reply):
        problems.append("It says a result changed or will change. You can't change results.")
    return problems


def settled_points(metas: list[dict[str, Any]]) -> list[str]:
    """Corrections the learner has accepted so far, oldest first, without duplicates."""
    out: list[str] = []
    for m in metas:
        for a in m.get("accepts", []):
            a = " ".join(str(a).split())
            if a and a.lower() not in {o.lower() for o in out}:
                out.append(a)
    return out[-MAX_SETTLED:]


# ------------------------------------------------------------------------------ re-check


@dataclass
class RecheckResult:
    output: RecheckOutput
    revised: list[str] = field(default_factory=list)  # criteria now met
    refused: list[str] = field(default_factory=list)  # "revise" without a quote in the answer
    # "revise" whose quote is a statement still listed as wrong (the grading pipeline's own
    # rule: live check R5 revised three wrong functions to met, "the criteria only require
    # you to state a function").
    contradicted: list[str] = field(default_factory=list)
    off_topic: bool = False  # the answer addresses another question: nothing can move
    errors_dropped: list[int] = field(default_factory=list)  # 1-based
    bands_before: dict[str, str] = field(default_factory=dict)
    bands_after: dict[str, str] = field(default_factory=dict)

    @property
    def changed(self) -> bool:
        return bool(self.revised or self.errors_dropped)

    def to_json(self) -> dict[str, Any]:
        return {
            "output": self.output.model_dump(mode="json"),
            "revised": self.revised,
            "refused": self.refused,
            "contradicted": self.contradicted,
            "off_topic": self.off_topic,
            "errors_dropped": self.errors_dropped,
            "bands_before": self.bands_before,
            "bands_after": self.bands_after,
            "changed": self.changed,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "RecheckResult":
        return cls(
            RecheckOutput.model_validate(data["output"]),
            revised=data["revised"],
            refused=data["refused"],
            contradicted=data.get("contradicted", []),
            off_topic=data.get("off_topic", False),
            errors_dropped=data["errors_dropped"],
            bands_before=data["bands_before"],
            bands_after=data["bands_after"],
        )

    def for_tutor(self) -> str:
        if self.changed:
            moved = [
                f"{d}: {self.bands_before[d]} -> {b}"
                for d, b in self.bands_after.items()
                if self.bands_before.get(d) != b
            ]
            outcome = "Some decisions were reversed" + (
                f" ({'; '.join(moved)})." if moved else ", though no band moved."
            )
        else:
            outcome = "No decision changed."
        return f"{outcome} The grader's summary: {self.output.summary}"


def recheck_variables(
    question: str,
    answer: str,
    trace: EvaluationTrace,
    criteria: list[Criterion],
    argument: str,
) -> dict[str, Any]:
    verdicts = {v.criterion_id: v for v in trace.verdicts}
    not_met, met = [], []
    for c in criteria:
        v = verdicts.get(c.criterion_id)
        if v is None:
            continue
        if v.met:
            met.append(c.statement)
        else:
            not_met.append(
                {"criterion_id": c.criterion_id, "statement": c.statement, "note": v.justification}
            )
    return {
        "question": question,
        "answer": answer,
        "not_met": not_met,
        "met": met,
        "errors": [e.model_dump() for e in trace.errors],
        "argument": argument,
    }


def apply_recheck(
    trace: EvaluationTrace,
    criteria: list[Criterion],
    answer: str,
    out: RecheckOutput,
    bands: Bands,
) -> RecheckResult:
    """Only decisions that counted against the answer can move. The same rules as grading:
    a criterion becomes met only with a quote that is in the answer and isn't a statement
    still listed as wrong. An answer to a different question can't move at all: its listed
    "error" is often that it answers something else, and dropping it would credit it."""
    not_met = {v.criterion_id for v in trace.verdicts if not v.met}
    result = RecheckResult(out, off_topic=trace.addresses_question is False)
    result.bands_before = {d.value: b for d, b in trace.bands.items()}
    if result.off_topic:
        result.bands_after = dict(result.bands_before)
        return result
    result.errors_dropped = sorted(
        {e.error for e in out.errors if not e.stands and 1 <= e.error <= len(trace.errors)}
    )
    standing = [e for i, e in enumerate(trace.errors, 1) if i not in result.errors_dropped]
    for d in out.criteria:
        if d.criterion_id not in not_met or d.decision != "revise":
            continue
        if not evidence_supported(d.evidence, answer):
            result.refused.append(d.criterion_id)
        elif any(same_statement(d.evidence, e.quote) for e in standing):
            result.contradicted.append(d.criterion_id)
        else:
            result.revised.append(d.criterion_id)
    verdicts = [
        v.model_copy(update={"met": True}) if v.criterion_id in result.revised else v
        for v in trace.verdicts
    ]
    scores = dimension_scores(criteria, verdicts, n_errors=len(standing), task_type=trace.task_type)
    result.bands_after = {d.value: bands.label(s) for d, s in scores.items()}
    return result
