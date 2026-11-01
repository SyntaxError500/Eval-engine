"""Checks on a generated rubric that the schema can't express.

The schema already enforces structure (shape matches task type, unique ids, obvious answers
only for creative). These checks catch rubrics that are valid JSON but would grade badly.
Each returns plain-language problems, which are fed back to the generator on its one retry.
"""

import re
from collections import Counter

from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.rubric import Criterion, RubricDraft

# Dimensions with at least this weight for the task type must be covered by every path.
# Lower-weight dimensions are optional: forcing a criterion into them would make the rubric
# ask for things the question doesn't need (a Phase 2 lesson). Aggregation re-normalises
# over the dimensions a path actually covers.
REQUIRED_WEIGHT = 0.2

# Non-observable judgement words. A criterion must say what is in the answer, not how good
# it is. Matched as whole words in criterion statements.
VAGUE_WORDS = (
    "good",
    "well",
    "clear",
    "clearly",
    "adequate",
    "adequately",
    "appropriate",
    "appropriately",
    "sufficient",
    "sufficiently",
    "proper",
    "properly",
    "effective",
    "effectively",
    "strong",
    "insightful",
    "thoughtful",
    "compelling",
    "high-quality",
)
_VAGUE = re.compile(r"\b(" + "|".join(re.escape(w) for w in VAGUE_WORDS) + r")\b", re.I)

MIN_CRITERIA_PER_PATH = 2  # partial credit needs at least two (Phase 2 lesson)

# Criteria that grade length or sentence count measure nothing about the answer's content
# (seen in Phase 3 review: "Uses between three and five sentences", "in a single sentence").
_NUM = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|single)"
_LENGTH = re.compile(
    rf"\b{_NUM}\s*(?:(?:to|-|\u2013|\u2011|and)\s*{_NUM}\s*)?sentences?\b|\bsentence count\b|"
    r"\bword count\b|\b\d+\s*words\b",
    re.IGNORECASE,
)
MULTI_PATH_TYPES = frozenset({TaskType.ANALYTICAL, TaskType.EXPLANATORY})

# Words that judge the ANSWER's quality. A narrower list than VAGUE_WORDS for question text:
# "is a carbon tax effective" or "a strong economy" are subject matter, not answer quality.
_ANSWER_QUALITY = re.compile(
    r"\b(clear|clearly|well|good|adequate|adequately|appropriate|appropriately|sufficient|"
    r"sufficiently|proper|properly|thoughtful|insightful|compelling)\b",
    re.IGNORECASE,
)

# One criterion covering several items is all-or-nothing across them, so a partial answer
# earns nothing (Phase 2 lesson). Still produced under v3 in ~5/28 questions.
_BUNDLED = re.compile(
    r"\b(?:for each|each of the|each (?!other\b)[a-z]+)\b|at least (?:two|three|2|3) "
    r"(?:distinct |different )?(?:reasons|arguments|pieces|points|examples)",
    re.IGNORECASE,
)

# Questions that ask for several explanations/perspectives get each one turned into a
# "path", but the judge grades a single identified path, so the rest go unchecked. Seen in
# ~8/27 v2 questions and still produced under v3's prompt rule, hence a hard check.
# "two reasons"/"two arguments" for one position are parts of one answer and stay allowed.
_ALTERNATIVES = (
    r"(?:explanations?|mechanisms?|perspectives?|viewpoints?|views|ways|theories|"
    r"accounts|interpretations|approaches|models)"
)
_ASKS_FOR_SEVERAL = re.compile(
    rf"\b(?:two|three|both|each|multiple|several|different|distinct|contrasting)\b"
    rf"[^.?!]{{0,40}}?\b{_ALTERNATIVES}\b|\bone that\b[^.?!]*\banother\b",
    re.IGNORECASE,
)


def required_dimensions(task_type: TaskType, weights: dict[str, dict[str, float]]) -> set[str]:
    row = weights[task_type.value]
    return {dim for dim, w in row.items() if w >= REQUIRED_WEIGHT}


def check_rubric(
    draft: RubricDraft,
    weights: dict[str, dict[str, float]],
    requested_task_type: TaskType | None = None,
) -> list[str]:
    problems: list[str] = []
    if requested_task_type is not None and draft.task_type != requested_task_type:
        problems.append(
            f"task_type must be {requested_task_type.value!r}, got {draft.task_type.value!r}"
        )

    required = required_dimensions(draft.task_type, weights)
    # Criteria quote the question (traceability), so a judgement word in the question ("state
    # a clear position") gets copied into a criterion; keep it out of the question itself.
    q_vague = sorted({m.lower() for m in _ANSWER_QUALITY.findall(draft.question)})
    if q_vague:
        problems.append(
            f"the question uses judgement word(s) {q_vague}; ask for what is observable "
            "(e.g. 'State a clear position' -> 'State a position (for or against)')"
        )
    for path in draft.paths:
        where = f"path {path.path_id}"
        if len(path.criteria) < MIN_CRITERIA_PER_PATH:
            problems.append(
                f"{where} has {len(path.criteria)} criterion; split the idea into at least "
                f"{MIN_CRITERIA_PER_PATH} observable parts so partial answers can earn credit"
            )
        if not any(c.core for c in path.criteria):
            problems.append(f"{where} has no core criterion")
        covered = {c.dimension.value for c in path.criteria}
        missing = sorted(required - covered)
        if missing:
            problems.append(f"{where} has no criterion for dimension(s) {missing}")
        for c in path.criteria:
            # In a creative brief, length is a real constraint ("120-150 words") and is
            # graded under correctness; elsewhere a length criterion measures no content.
            length_is_constraint = (
                draft.task_type == TaskType.CREATIVE and c.dimension == Dimension.CORRECTNESS
            )
            if not length_is_constraint and _LENGTH.search(c.statement):
                problems.append(
                    f"{c.criterion_id} grades length or sentence count; criteria must be "
                    "about content"
                )
            if _BUNDLED.search(c.statement):
                problems.append(
                    f"{c.criterion_id} covers several items at once ('for each'); write one "
                    "criterion per item so a partial answer can earn some of them"
                )
            vague = sorted({m.lower() for m in _VAGUE.findall(c.statement)})
            if vague:
                problems.append(
                    f"{c.criterion_id} uses judgement word(s) {vague}; state what the answer "
                    "contains instead (e.g. 'States a clear position' -> 'States a position "
                    "(for or against)')"
                )
            problems += _traceability_problems(draft, c)
            if "clich" in c.statement.lower() and _OPEN_LIST.search(c.statement):
                problems.append(
                    f"{c.criterion_id} bans an open-ended set of clichés ('such as'); list the "
                    'exact phrases it bans (\'Does not use any of: "x", "y"\')'
                )
            if _EXACTLY.search(c.statement) and not _EXACTLY.search(draft.question):
                problems.append(
                    f"{c.criterion_id} demands 'exactly' something the question doesn't; "
                    "accept at least what the question asks for"
                )
        if draft.task_type == TaskType.ANALYTICAL and not any(
            c.core and c.dimension == Dimension.REASONING for c in path.criteria
        ):
            # The design's "free consistency check": analytical rubrics made only of factual
            # checkboxes mean something went wrong.
            problems.append(
                f"{where}: an analytical path needs a core reasoning criterion, e.g. "
                "'Explains how the first reason supports the position' (dimension "
                '"reasoning", core true, requires quoting the question\'s request for support)'
            )

    if draft.task_type in MULTI_PATH_TYPES:
        m = _ASKS_FOR_SEVERAL.search(draft.question)
        if m:
            problems.append(
                f'the question asks for several alternatives ("{m.group(0)}"). Ask for ONE '
                "argument or explanation; the different valid ways to answer belong in the "
                "rubric's paths, and a learner only needs one of them"
            )
        # Analytical: positions can always be argued more than one way. Explanatory may have a
        # single valid explanation; forcing two made the generator invent a wrong one (review
        # 1, Q29: candle yellow from "hot gases").
        if draft.task_type == TaskType.ANALYTICAL and len(draft.paths) < 2:
            problems.append(
                "analytical rubrics need at least 2 genuinely different lines of argument"
            )
        descriptions = Counter(p.description.strip().lower() for p in draft.paths)
        if any(n > 1 for n in descriptions.values()):
            problems.append("two paths have the same description; paths must differ")
        statement_sets = [
            frozenset(c.statement.strip().lower() for c in p.criteria) for p in draft.paths
        ]
        if len(set(statement_sets)) < len(statement_sets):
            problems.append("two paths have identical criteria; paths must differ")

    if draft.task_type == TaskType.CREATIVE:
        obvious = [a.strip().lower() for a in draft.obvious_answers]
        if len(set(obvious)) < len(obvious):
            problems.append("obvious_answers contains duplicates")
    return problems


# ---------------------------------------------------------------- traceability (review 1, A)

# Creative craft tests (turn, show-don't-tell, clichés) are graded by design (design doc §9)
# even though a brief rarely spells them out; they are the only criteria allowed no quote.
_CRAFT_EXEMPT = frozenset({Dimension.EXPRESSION})
_OPEN_LIST = re.compile(r"such as|e\.g\.|for example|common|overused|typical", re.IGNORECASE)
_EXACTLY = re.compile(r"\bexactly\b", re.IGNORECASE)
_NON_WORD = re.compile(r"[^a-z0-9]+")
MIN_QUOTE_CHARS = 4


def _normalise(text: str) -> str:
    return " " + _NON_WORD.sub(" ", text.lower()).strip() + " "


def _quote_in_question(quote: str, question: str) -> bool:
    """Exact (normalised) substring, or every content word of the quote appears in the
    question. The model often quotes with small paraphrases; demanding a verbatim match
    cost a full retry each time, while the safeguard only needs the words to come from the
    question."""
    if _normalise(quote) in _normalise(question):
        return True
    q_words = set(_normalise(question).split())
    content = [w for w in _normalise(quote).split() if len(w) > 3]
    return len(content) >= 2 and all(w in q_words for w in content)


def _traceability_problems(draft: RubricDraft, c: Criterion) -> list[str]:
    """Each criterion must quote the words of the question that ask for it, so a rubric can't
    quietly demand things (a numeric example, a named theory, a rebuttal) nobody asked for."""
    exempt = draft.task_type == TaskType.CREATIVE and c.dimension in _CRAFT_EXEMPT
    if exempt:
        return []
    quote = (c.requires or "").strip()
    if len(quote) < MIN_QUOTE_CHARS:
        return [
            f"{c.criterion_id} has no 'requires' quote; quote the exact words of the question "
            "that ask for it, or drop the criterion if the question doesn't ask for it"
        ]
    if not _quote_in_question(quote, draft.question):
        return [
            f"{c.criterion_id} 'requires' quote \"{quote[:80]}\" is not in the question; quote "
            "the question's own words, or drop the criterion if the question doesn't ask for it"
        ]
    return []
