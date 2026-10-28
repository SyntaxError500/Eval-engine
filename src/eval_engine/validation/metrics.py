"""Agreement metrics. Leniency follows Pathak et al. (ICER 2025): mean signed error of the
engine against human scores on a normalised 0..1 scale (target |leniency| <= 0.1).

Correlation and leniency are always reported together: correlation measures ordering and is
blind to a constant offset; leniency measures the offset.
"""

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score

GRADED_LEVELS = (0.0, 0.5, 1.0)


def leniency(engine: Sequence[float], human: Sequence[float]) -> float:
    """> 0 means the engine is more generous than humans; < 0 harsher."""
    return float(np.mean(np.asarray(engine) - np.asarray(human)))


def qwk(engine: Sequence[float], human: Sequence[float]) -> float:
    e = [GRADED_LEVELS.index(x) for x in engine]
    h = [GRADED_LEVELS.index(x) for x in human]
    if len(set(e) | set(h)) < 2:
        return math.nan
    return float(cohen_kappa_score(h, e, weights="quadratic", labels=[0, 1, 2]))


def spearman(engine: Sequence[float], human: Sequence[float]) -> float:
    if len(set(engine)) < 2 or len(set(human)) < 2:
        return math.nan
    return float(spearmanr(engine, human).statistic)


def accuracy(engine: Sequence[str], human: Sequence[str]) -> float:
    return float(accuracy_score(human, engine))


def macro_f1(engine: Sequence[str], human: Sequence[str]) -> float:
    labels = sorted(set(human) | set(engine))
    return float(f1_score(human, engine, labels=labels, average="macro", zero_division=0))


@dataclass(frozen=True)
class Estimate:
    value: float
    lo: float
    hi: float

    def fmt(self, digits: int = 3) -> str:
        if math.isnan(self.value):
            return "n/a"
        return f"{self.value:.{digits}f} [{self.lo:.{digits}f}, {self.hi:.{digits}f}]"


def bootstrap[T](
    metric: Callable[[Sequence[T], Sequence[T]], float],
    engine: Sequence[T],
    human: Sequence[T],
    *,
    n_resamples: int = 1000,
    seed: int = 0,
    alpha: float = 0.05,
) -> Estimate:
    """Percentile bootstrap CI over items."""
    point = metric(engine, human)
    rng = np.random.default_rng(seed)
    n = len(engine)
    samples: list[float] = []
    for _ in range(n_resamples):
        idx = rng.integers(0, n, n)
        v = metric([engine[i] for i in idx], [human[i] for i in idx])
        if not math.isnan(v):
            samples.append(v)
    if not samples:
        return Estimate(point, math.nan, math.nan)
    lo, hi = np.quantile(samples, [alpha / 2, 1 - alpha / 2])
    return Estimate(point, float(lo), float(hi))


def flip_rate(runs_per_item: Sequence[Sequence[Sequence[bool]]]) -> float:
    """Fraction of criterion verdicts that are not identical across repeated runs.

    runs_per_item[i][r][c] = verdict of criterion c, run r, item i.
    """
    total = flipped = 0
    for runs in runs_per_item:
        for verdicts in zip(*runs, strict=True):
            total += 1
            flipped += len(set(verdicts)) > 1
    return flipped / total if total else math.nan
