"""Aggregation in code, never in the model (design doc §4, step 10)."""

from dataclasses import dataclass
from pathlib import Path

import yaml

from eval_engine.config import REPO_ROOT
from eval_engine.schemas.amendment import Framing
from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.judge import Verdict
from eval_engine.schemas.rubric import Criterion

# Factual errors the judge lists count against correctness as one implicit check, met only
# when there are none. Every answer is expected to be accurate, so this needs no quote from
# the question (unlike rubric criteria). Not applied to creative pieces.
NO_ERRORS_WEIGHT = 1.0


@dataclass(frozen=True)
class Bands:
    thresholds: list[tuple[str, float]]  # ascending by min
    amendment_confidence_threshold: float
    verifier_framing: Framing = "adversarial"

    def label(self, score: float) -> str:
        label = self.thresholds[0][0]
        for name, minimum in self.thresholds:
            if score >= minimum:
                label = name
        return label


def load_bands(path: Path | None = None) -> Bands:
    path = path or REPO_ROOT / "config" / "bands.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    pairs = sorted(((b["label"], float(b["min"])) for b in data["bands"]), key=lambda p: p[1])
    return Bands(pairs, float(data["amendment_confidence_threshold"]), data["verifier_framing"])


def dimension_scores(
    criteria: list[Criterion],
    verdicts: list[Verdict],
    *,
    n_errors: int,
    task_type: TaskType,
) -> dict[Dimension, float]:
    """Per dimension: met weight / total weight over the path's criteria in that dimension.
    Dimensions the path doesn't cover are absent (not assessed), never zero."""
    met = {v.criterion_id: v.met for v in verdicts}
    total: dict[Dimension, float] = {}
    got: dict[Dimension, float] = {}
    for c in criteria:
        total[c.dimension] = total.get(c.dimension, 0.0) + c.weight
        if met.get(c.criterion_id, False):
            got[c.dimension] = got.get(c.dimension, 0.0) + c.weight
    if task_type != TaskType.CREATIVE:
        total[Dimension.CORRECTNESS] = total.get(Dimension.CORRECTNESS, 0.0) + NO_ERRORS_WEIGHT
        if n_errors == 0:
            got[Dimension.CORRECTNESS] = got.get(Dimension.CORRECTNESS, 0.0) + NO_ERRORS_WEIGHT
    return {d: got.get(d, 0.0) / t for d, t in total.items() if t > 0}


def overall_score(scores: dict[Dimension, float], weights: dict[str, float]) -> float | None:
    """Task-type weights re-normalised over the assessed dimensions. Internal only."""
    used = {d: weights[d.value] for d in scores if weights.get(d.value, 0) > 0}
    norm = sum(used.values())
    if norm == 0:
        return None
    return sum(scores[d] * w for d, w in used.items()) / norm
