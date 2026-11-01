"""Sentence-count criteria are decided in code, not by the judge.

Golden set: on a 10-sentence piece the judge counted to ten in its justification and still
marked "Contains between three and eight sentences" as met. Counting is mechanical, so the
pipeline overrides the verdict either way.
"""

import re

from eval_engine.schemas.judge import Verdict
from eval_engine.schemas.rubric import Criterion

_WORDS = "zero one two three four five six seven eight nine ten eleven twelve"
_NUMBERS = {w: i for i, w in enumerate(_WORDS.split(" "))}
_NUM = r"(\d+|" + "|".join(_NUMBERS) + r")"
# \u2013/\u2014 are en/em dashes, \u201d/\u2019 closing curly quotes (escaped for RUF001).
_RANGE = re.compile(rf"\b{_NUM}\s*(?:and|to|-|\u2013|\u2014)\s*{_NUM}\s+sentences\b", re.IGNORECASE)
_SENTENCE_END = re.compile(r"[.!?]+[\"'\u201d\u2019)]*(?=\s|$)")


def _num(token: str) -> int:
    return int(token) if token.isdigit() else _NUMBERS[token.lower()]


def sentence_range(statement: str) -> tuple[int, int] | None:
    m = _RANGE.search(statement)
    return (_num(m.group(1)), _num(m.group(2))) if m else None


def count_sentences(text: str) -> int:
    """Terminal punctuation followed by whitespace or the end; trailing text without a full
    stop counts as one more sentence."""
    text = text.strip()
    if not text:
        return 0
    ends = list(_SENTENCE_END.finditer(text))
    tail = text[ends[-1].end() :].strip() if ends else text
    return len(ends) + (1 if tail else 0)


def apply_count_checks(
    verdicts: list[Verdict], criteria: list[Criterion], answer: str
) -> tuple[list[Verdict], list[str]]:
    """Returns (verdicts, ids whose verdict the count changed)."""
    by_id = {c.criterion_id: c for c in criteria}
    n = count_sentences(answer)
    out: list[Verdict] = []
    changed: list[str] = []
    for v in verdicts:
        c = by_id.get(v.criterion_id)
        bounds = sentence_range(c.statement) if c else None
        if bounds is not None:
            met = bounds[0] <= n <= bounds[1]
            if met != v.met:
                changed.append(v.criterion_id)
                v = v.model_copy(
                    update={
                        "met": met,
                        "evidence": "",
                        "justification": f"[counted in code: {n} sentences] {v.justification}",
                    }
                )
        out.append(v)
    return out, changed
