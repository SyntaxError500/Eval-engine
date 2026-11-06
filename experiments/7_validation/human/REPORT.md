# Human-graded set: results

Pre-registered in `src/eval_engine/validation/human_analysis.py` before any grade arrived.

## 1. Inter-rater agreement

- Requirements: kappa 1.000, raw agreement 100.0%.
- False-statement flag: kappa 0.953.
- Overall label: quadratic-weighted kappa 1.000, raw agreement 100.0%.

## 2. Engine (judge v3, majority of 3) against the graders

95% intervals: cluster bootstrap over 13 questions, 2000 resamples.

| Measure | Value [95% CI] |
|---|---|
| Leniency vs mean of graders | -0.010 [-0.096, +0.070] |
| Spearman vs mean of graders | +0.843 [+0.783, +0.911] |
| QWK vs grader 1 | +0.821 [+0.754, +0.853] |
| QWK vs grader 2 | +0.821 [+0.754, +0.853] |

Gate (absolute leniency at most 0.1): PASS

Engine full marks where both graders gave less:

- A17 (ref-83e77d761714/correctness): graders partially_correct / partially_correct
- A23 (ref-3f8052a62a58/correctness): graders partially_correct / partially_correct
- A32 (balloon-good/reasoning): graders partially_correct / partially_correct
- A45 (balloon-good/completeness): graders partially_correct / partially_correct
- A49 (ref-b0affe8aae1b/correctness): graders partially_correct / partially_correct

## 3. Bands (task 5), against adjudicated requirement marks

- Same band: 109/121 dimension scores (90%).
- Mean absolute score gap: 0.057.
