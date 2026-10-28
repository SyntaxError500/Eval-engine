"""Mapping human labels and engine verdicts onto comparable scales.

Scales (fixed before running the pilot, so results can't steer them):
- 2-way:  correct | incorrect
- 3-way:  correct | contradictory | incorrect           (SemEval-2013 definition)
- graded: 1.0 correct, 0.5 partially correct, 0.0 otherwise — used for leniency and QWK

Engine side, from one JudgeOutput against its rubric path:
- any listed error                       -> contradictory, graded 0.0
- every core criterion met               -> correct,       graded 1.0
- at least one criterion met             -> incorrect,     graded 0.5 (partial credit)
- nothing met                            -> incorrect,     graded 0.0
"""

from dataclasses import dataclass

from eval_engine.schemas.judge import JudgeOutput
from eval_engine.schemas.rubric import Rubric

HUMAN_GRADED = {
    "correct": 1.0,
    "partially_correct_incomplete": 0.5,
    "contradictory": 0.0,
    "irrelevant": 0.0,
    "non_domain": 0.0,
}


def human_3way(label: str) -> str:
    return label if label in ("correct", "contradictory") else "incorrect"


def human_2way(label: str) -> str:
    return "correct" if label == "correct" else "incorrect"


@dataclass(frozen=True)
class EngineLabels:
    two_way: str
    three_way: str
    graded: float
    weighted_score: float  # sum of met criterion weights / total, before any rule


class JudgeOutputMismatch(ValueError):
    """The judge's verdicts don't line up with the rubric's criteria."""


def engine_labels(output: JudgeOutput, rubric: Rubric) -> EngineLabels:
    path_id = output.identified_path or rubric.paths[0].path_id
    try:
        path = rubric.path(path_id)
    except KeyError:
        raise JudgeOutputMismatch(f"judge identified unknown path {path_id!r}") from None

    verdicts = {v.criterion_id: v for v in output.verdicts}
    missing = [c.criterion_id for c in path.criteria if c.criterion_id not in verdicts]
    if missing:
        raise JudgeOutputMismatch(f"no verdict for criteria {missing}")

    total = sum(c.weight for c in path.criteria)
    met_weight = sum(c.weight for c in path.criteria if verdicts[c.criterion_id].met)
    score = met_weight / total
    core = [c for c in path.criteria if c.core] or list(path.criteria)
    all_core_met = all(verdicts[c.criterion_id].met for c in core)

    if output.errors:
        return EngineLabels("incorrect", "contradictory", 0.0, score)
    if all_core_met:
        return EngineLabels("correct", "correct", 1.0, score)
    return EngineLabels("incorrect", "incorrect", 0.5 if met_weight > 0 else 0.0, score)
