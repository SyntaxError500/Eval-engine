"""Checks on a generated rubric that the schema can't express.

The schema already enforces structure (shape matches task type, unique ids, obvious answers
only for creative). These checks catch rubrics that are valid JSON but would grade badly.
Each returns plain-language problems, which are fed back to the generator on its one retry.
"""

import re
from collections import Counter

from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.rubric import RubricDraft

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
            vague = sorted({m.lower() for m in _VAGUE.findall(c.statement)})
            if vague:
                problems.append(
                    f"{c.criterion_id} uses judgement word(s) {vague}; state what the answer "
                    "contains instead"
                )
        if draft.task_type == TaskType.ANALYTICAL and not any(
            c.core and c.dimension == Dimension.REASONING for c in path.criteria
        ):
            # The design's "free consistency check": analytical rubrics made only of factual
            # checkboxes mean something went wrong.
            problems.append(f"{where}: an analytical path needs a core reasoning criterion")

    if draft.task_type in MULTI_PATH_TYPES:
        m = _ASKS_FOR_SEVERAL.search(draft.question)
        if m:
            problems.append(
                f'the question asks for several alternatives ("{m.group(0)}"). Ask for ONE '
                "argument or explanation; the different valid ways to answer belong in the "
                "rubric's paths, and a learner only needs one of them"
            )
        if len(draft.paths) < 2:
            problems.append(
                f"{draft.task_type.value} rubrics need at least 2 genuinely different "
                "solution paths"
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
