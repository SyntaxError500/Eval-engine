"""Phrasing the selected points, and the code checks on what the model writes (plan Phase 6).

The model gets the chosen points, the judge's notes and the answer's own words, never the
reference answer, scores or bands. Every phrased point is checked: it speaks to the learner as
"you", quotes only the answer, lifts no run of words from the reference answer, mentions no
grading internals or prompt labels, and stays short. A point that fails twice falls back to a
plain template, so feedback is never missing and never unchecked.

A rejected route always opens with the same fixed sentence and the model supplies only the
reason, so that note keeps its distinct voice (design doc §15). In the first review-set run the
model copied the proposer's verdict instead ("does not constitute a valid new approach").
"""

import re
from typing import Any

from eval_engine.evaluation.evidence import evidence_supported
from eval_engine.feedback.select import Point, Selection
from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.schemas.feedback import Feedback, FeedbackItem, PhrasedFeedback

PHRASE_ATTEMPTS = 2  # the first, then one re-phrase carrying the problems
MAX_WORDS = 60  # the prompt asks for 50
# Words in a row shared with the reference answer that count as copying. At 5, ordinary
# phrases tripped it ("because the heated air is") in 5 of 91 points on the review set.
LEAK_NGRAM = 6

ACCEPTED_NOTE = (
    "Your approach differs from the standard routes for this question and was evaluated on "
    "its own terms."
)
DIVERGENCE_LEAD = (
    "Your answer takes a different route from the usual ones for this question, so that route "
    "was checked separately. It didn't hold up:"
)

_QUOTED = re.compile(r"[\"“]([^\"“”]+)[\"”]")
_INTERNALS = re.compile(
    r"\bP\d+\.C\d+\b|\b(?:rubric|criterion|criteria|scores?|scored|bands?|grader)\b",
    re.IGNORECASE,
)
_WORD = re.compile(r"[a-z0-9]+")
_EMPTY = frozenset({"", "null", "none", "n/a", "-"})
# Field names from this prompt and the last, which the model copied into its text.
_LABELS = re.compile(
    r"(?:^|[.\s])(?:needs|problem|note|they wrote|their words|your words|why it is wrong|"
    r"grader's note|"
    r"requirement|the answer says)\s*:",
    re.IGNORECASE,
)
_REPEATED_LEAD = re.compile(r"^(?:it didn['\u2019]t hold up\s*:\s*)+", re.IGNORECASE)
_YOU = re.compile(r"\byou(?:r|rs|rself)?\b", re.IGNORECASE)
_THIRD_PERSON = re.compile(r"\bthe (?:student|learner|writer|author)\b", re.IGNORECASE)


def give_feedback(
    client: LLMClient,
    selection: Selection,
    question: str,
    answer: str,
    reference_answer: str | None,
    *,
    rubric_text: list[str] | None = None,
    evaluation_id: str | None = None,
) -> Feedback:
    """`rubric_text`: the criteria of the path used. Feedback is meant to reference them, so
    wording they share with the reference answer is not a leak."""
    labelled = [(f"I{i}", p) for i, p in enumerate(selection.improve, start=1)]
    labelled += [(f"W{i}", p) for i, p in enumerate(selection.worked, start=1)]
    rejected = selection.approach == "rejected"
    phrased: dict[str, str] = {}
    problems: dict[str, str] = {}
    call_ids: list[str] = []
    fallbacks: list[str] = []
    allowed = " ".join(
        [
            question,
            answer,
            *(rubric_text or []),
            *(s for _, p in labelled for s in (p.statement, *p.also)),
        ]
    )

    if labelled or selection.off_topic or rejected:
        variables: dict[str, Any] = {
            "question": question,
            "answer": answer,
            "points": [_point_vars(ref, p) for ref, p in labelled],
            "divergence": selection.divergence_reason if rejected else None,
            "off_topic": selection.off_topic,
        }
        wanted = [ref for ref, _ in labelled]
        wanted += ["divergence"] * rejected + ["off_topic"] * selection.off_topic
        for _ in range(PHRASE_ATTEMPTS):
            try:
                res = client.complete(
                    "feedback_phraser",
                    "feedback_phrase",
                    {**variables, "problems": [f"{r}: {w}" for r, w in problems.items()]},
                    PhrasedFeedback,
                    evaluation_id=evaluation_id,
                )
            except (ProviderError, StructuredOutputError) as e:
                fallbacks.append(f"feedback model unavailable: {type(e).__name__}")
                break
            call_ids.append(res.call.call_id)
            texts = {p.ref: p.text.strip() for p in res.value.points}
            texts["divergence"] = (res.value.divergence or "").strip()
            texts["off_topic"] = (res.value.off_topic or "").strip()
            problems = {}
            for ref in wanted:
                if ref in phrased:
                    continue  # keep the first version that passed
                why = check_text(texts.get(ref, ""), answer, reference_answer, allowed)
                if why is None and ref == "off_topic":
                    why = _names_nothing_from(texts[ref], answer, question)
                if why:
                    problems[ref] = why
                else:
                    phrased[ref] = texts[ref]
            if not problems:
                break
        fallbacks += [f"{ref}: {why}" for ref, why in problems.items()]

    items: list[FeedbackItem] = []
    if selection.approach == "accepted":
        items.append(FeedbackItem(kind="approach", text=ACCEPTED_NOTE, source="fixed"))
    if rejected:
        if "divergence" in phrased:
            # The model tends to repeat the opener it was told its text follows.
            reason = _REPEATED_LEAD.sub("", phrased["divergence"])
            phrased["divergence"] = f"{DIVERGENCE_LEAD} {reason}"
        items.append(
            _item("divergence", phrased, "divergence", _divergence_template(selection), [])
        )
    if selection.off_topic:
        items.append(
            _item("off_topic", phrased, "off_topic", _off_topic_template(question, answer), [])
        )
    for ref, p in labelled:
        if ref.startswith("I"):
            items.append(_item("improve", phrased, ref, _improve_template(p), list(p.refs)))
    if selection.obvious and len(selection.improve) < 3:
        items.append(
            FeedbackItem(kind="originality", text=_originality(selection.obvious), source="fixed")
        )
    for ref, p in labelled:
        if ref.startswith("W"):
            items.append(_item("worked", phrased, ref, _worked_template(p), list(p.refs)))
    return Feedback(items=items, call_ids=call_ids, fallbacks=fallbacks)


def check_text(text: str, answer: str, reference: str | None, allowed: str) -> str | None:
    """Why a phrased point can't be shown to the learner, or None if it can."""
    if text.strip().lower() in _EMPTY:
        return "missing"
    label = _LABELS.search(text)
    if label:
        return f"copies a label from the instructions ({label.group(0)!r}); use your own words"
    if _THIRD_PERSON.search(text) or not _YOU.search(text):
        return 'speak to the learner as "you", not about "the answer" or "the student"'
    words = len(text.split())
    if words > MAX_WORDS:
        return f"too long ({words} words; at most 50)"
    internal = _INTERNALS.search(text)
    if internal:
        return f"mentions grading internals ({internal.group(0)!r})"
    for quote in _QUOTED.findall(text):
        quote = quote.strip(" .,;:")
        if len(quote.split()) >= 2 and not (
            evidence_supported(quote, answer) or _contains(allowed, quote)
        ):
            return f'quotes words that are not in the answer ("{quote[:60]}")'
    if reference:
        shared = _ngrams(text) & (_ngrams(reference) - _ngrams(allowed))
        if shared:
            return f"repeats wording from the model answer ({' '.join(sorted(shared)[0])!r})"
    return None


def _names_nothing_from(text: str, answer: str, question: str) -> str | None:
    """An off-topic note has to say what the answer is about instead, or it fits any answer
    (external review 1, E11)."""
    own = _content(answer) - _content(question)
    if _content(text) & own:
        return None
    return "say what their answer is about instead, using a word or two from it"


_COMMON = frozenset(
    [
        "because",
        "were",
        "that",
        "this",
        "with",
        "have",
        "from",
        "they",
        "them",
        "what",
        "about",
        "which",
        "their",
        "your",
        "does",
        "doesn",
        "answer",
        "question",
        "instead",
        "other",
    ]
)


def _content(text: str) -> set[str]:
    # A short stem, so "productivity" in the note matches "productive" in the answer
    # (external review 1 passed that note; a whole-word match rejected it).
    words = (w for w in _WORD.findall(text.lower()) if len(w) >= 4 and w not in _COMMON)
    return {w[:6] if len(w) > 6 else w.rstrip("s") for w in words}


def _point_vars(ref: str, p: Point) -> dict[str, Any]:
    return {
        "ref": ref,
        "error": p.kind == "error",
        "statement": p.statement,
        "reason": p.reason,
        "evidence": p.evidence,
        "also": list(p.also),
    }


def _item(
    kind: Any, phrased: dict[str, str], ref: str, template: str, refs: list[str]
) -> FeedbackItem:
    if ref in phrased:
        return FeedbackItem(kind=kind, text=phrased[ref], refs=refs, source="model")
    return FeedbackItem(kind=kind, text=template, refs=refs, source="template")


def _ngrams(text: str) -> set[tuple[str, ...]]:
    w = _WORD.findall(text.lower())
    return {tuple(w[i : i + LEAK_NGRAM]) for i in range(len(w) - LEAK_NGRAM + 1)}


def _contains(haystack: str, quote: str) -> bool:
    return " ".join(_WORD.findall(quote.lower())) in " ".join(_WORD.findall(haystack.lower()))


# ---------------------------------------------------------------- templates


def _imperative(statement: str) -> str:
    """'Explains how X' -> 'explain how X'; 'Identifies X' -> 'identify X'."""
    first, _, rest = statement.strip().rstrip(".").partition(" ")
    if first == "Does":
        verb = "do"
    elif first.endswith("ies"):
        verb = first[:-3] + "y"
    elif first.endswith("es") and first[:-2].endswith(("sh", "ch", "x", "ss")):
        verb = first[:-2]
    elif first.endswith("s"):
        verb = first[:-1]
    else:
        verb = first
    return f"{verb.lower()} {rest}".strip()


def _improve_template(p: Point) -> str:
    if p.kind == "error":
        return f'Check this statement: "{p.statement}". {p.reason}'.strip()
    return f"Next time, {_imperative(p.statement)}."


def _worked_template(p: Point) -> str:
    """Quotes the learner where the judge found evidence; restating the criterion alone said
    nothing about this answer (external review 1, E30)."""
    s = p.statement.strip().rstrip(".")
    met = f"{s[0].lower()}{s[1:]}"
    if p.evidence:
        return f'You wrote "{p.evidence.strip()}", which {met}.'
    return f"Your answer {met}."


def _divergence_template(selection: Selection) -> str:
    return f"{DIVERGENCE_LEAD} {selection.divergence_reason}"


def _off_topic_template(question: str, answer: str) -> str:
    opening = answer.strip().split(". ")[0].rstrip(".")
    return (
        f'Your answer is about something else ("{opening}"). Reread the question and answer '
        f"what it asks: {question}"
    )


def _originality(obvious: list[str]) -> str:
    # Labelled as a comparison, so its details aren't taken for the learner's own (review 1).
    return (
        "Your main idea is close to one of the most predictable takes on this brief. For "
        f'comparison, that take is: "{obvious[0]}" It wasn\'t marked down, but a less expected '
        "angle would stand out more."
    )
