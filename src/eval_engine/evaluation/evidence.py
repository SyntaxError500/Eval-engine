"""Evidence check: a criterion the judge marks met must quote words that are in the answer.

A cheap guard against hallucinated passes (plan Phase 4, task 2). Quotes are compared after
normalisation, and fuzzily, since judges often fix a typo or drop a word when quoting.
"""

import re
from difflib import SequenceMatcher

from eval_engine.schemas.judge import ClaimError, Verdict
from eval_engine.schemas.rubric import Criterion

FUZZY_THRESHOLD = 0.85
_NON_WORD = re.compile(r"[^a-z0-9]+")
# Creative tests that something is ABSENT (a banned phrase) or a count have no quote to give.
_ABSENCE_OR_COUNT = re.compile(
    r"\b(does not (use|contain|include)|avoids?|without using|sentences?)\b", re.IGNORECASE
)


def _norm(text: str) -> str:
    return _NON_WORD.sub(" ", text.lower()).strip()


def evidence_supported(evidence: str, answer: str, threshold: float = FUZZY_THRESHOLD) -> bool:
    """The quote is in the answer, or, for a relational criterion ("the three phases are
    distinct"), every comma/semicolon/ellipsis-separated fragment of it is. The first live
    run quoted "G1, S phase, M phase" from three places and was wrongly downgraded."""
    if _single_supported(evidence, answer, threshold):
        return True
    fragments = [f for f in _FRAGMENT_SPLIT.split(evidence) if _norm(f)]
    return len(fragments) > 1 and all(_single_supported(f, answer, threshold) for f in fragments)


_FRAGMENT_SPLIT = re.compile(r"\.\.\.|…|;|,|\s/\s|(?<=[.!?])\s+")


def _single_supported(evidence: str, answer: str, threshold: float) -> bool:
    e, a = _norm(evidence), _norm(answer)
    if not e:
        return False
    if e in a:
        return True
    e_tokens, a_tokens = e.split(), a.split()
    n = len(e_tokens)
    if n == 0 or n > len(a_tokens) + 2:
        return False
    best = 0.0
    for size in {max(1, n - 1), n, n + 1}:
        for i in range(0, max(1, len(a_tokens) - size + 1)):
            window = " ".join(a_tokens[i : i + size])
            best = max(best, SequenceMatcher(None, window, e).ratio())
            if best >= threshold:
                return True
    return False


def needs_evidence(criterion: Criterion) -> bool:
    return not _ABSENCE_OR_COUNT.search(criterion.statement)


def same_statement(evidence: str, error_quote: str) -> bool:
    """One quote contains the other (the contained side at least 3 words, so a lone noun
    doesn't match every error mentioning it), or they are near-identical."""
    e, q = _norm(evidence), _norm(error_quote)
    if not e or not q:
        return False
    shorter, longer = sorted((e, q), key=len)
    if len(shorter.split()) >= 3 and shorter in longer:
        return True
    return SequenceMatcher(None, e, q).ratio() >= FUZZY_THRESHOLD


def apply_error_contradictions(
    verdicts: list[Verdict], errors: list[ClaimError]
) -> tuple[list[Verdict], list[str]]:
    """Downgrade met verdicts whose evidence the judge itself listed as a factual error.

    Golden set: the judge passed "states a function of carbohydrates" on "Carbohydrates are
    mainly used to build bones" while flagging that same sentence as wrong."""
    checked: list[Verdict] = []
    downgraded: list[str] = []
    for v in verdicts:
        if v.met and any(same_statement(v.evidence, e.quote) for e in errors):
            downgraded.append(v.criterion_id)
            v = v.model_copy(
                update={
                    "met": False,
                    "justification": f"[evidence listed as a factual error] {v.justification}",
                }
            )
        checked.append(v)
    return checked, downgraded


def apply_evidence_check(
    verdicts: list[Verdict], criteria: list[Criterion], answer: str
) -> tuple[list[Verdict], list[str]]:
    """Downgrade met verdicts whose quote isn't in the answer.

    Returns (verdicts, ids of the downgraded criteria)."""
    by_id = {c.criterion_id: c for c in criteria}
    checked: list[Verdict] = []
    downgraded: list[str] = []
    for v in verdicts:
        c = by_id.get(v.criterion_id)
        if (
            v.met
            and c is not None
            and needs_evidence(c)
            and not evidence_supported(v.evidence, answer)
        ):
            downgraded.append(v.criterion_id)
            v = v.model_copy(
                update={
                    "met": False,
                    "justification": f"[evidence not found in answer] {v.justification}",
                }
            )
        checked.append(v)
    return checked, downgraded
