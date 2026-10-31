# Phase 2: findings and decisions

**Status: closed, 2026-10-31.** The judge is **Gemini 3.5 Flash Lite**, with the known weaknesses listed below. Detailed tables are in `REPORT.md` (v2, three judges) and `test_v3/REPORT.md` (final run).

## Setup

**Data:** SciEntsBank and Beetle, SemEval-2013 Task 7 (Dzikovska et al., 2013), CC BY 4.0, via huggingface.co/datasets/nkazi.

**Held-out test set:** 302 answers from the unseen-answers `test_ua` splits.
- SciEntsBank: 38 questions × 4 answers.
- Beetle: 30 questions × 5 answers.
- The same answers were used for every judge and every rubric version.

**Dev set:** 115 answers from the `train` split, on 23 questions that **do not appear** in the test sample. This matters because SciEntsBank's test and train answers share questions.

**Rubrics:** one checklist rubric per question, built by the generator (gpt-oss-120b) from the question and the reference answer only. The judge never sees the reference answer.

**Label mapping:** defined in `src/eval_engine/validation/labels.py` and fixed before any judge ran. The graded scale is 1.0 correct, 0.5 partially correct, 0.0 otherwise.

## Results

### Final run: Gemini 3.5 Flash Lite, rubric prompt v3, all 302 test answers

| Metric | Value [95% CI] | Target / note |
|---|---|---|
| Leniency | **−0.066** [−0.113, −0.018] | ±0.1. The point estimate passes; the interval reaches slightly past −0.1. |
| QWK | 0.577 [0.485, 0.662] | |
| Spearman | 0.587 [0.494, 0.671] | |
| 2-way accuracy | 78.1% [73.2, 82.5] | |
| 3-way macro-F1 | 0.595 [0.533, 0.652] | |
| Criterion flip rate | 4.7% | 50 answers × 3 runs at temperature 0 |
| Label flip rate | **12%** | 6 of 50 answers changed label across identical runs |

By dataset:

| | Leniency | QWK | 2-way accuracy |
|---|---|---|---|
| SciEntsBank | −0.132 | 0.698 | 84.2% |
| Beetle | 0.000 | 0.457 | 72.0% |

### Judge comparison: rubric prompt v2, same 302 test answers

| Judge | Scored | Leniency | QWK | 2-way accuracy |
|---|---|---|---|---|
| **Gemini 3.5 Flash Lite** | 297 | −0.088 [−0.135, −0.044] | **0.591** | **77.8%** |
| Qwen on Groq (qwen3.8-27b) | 297 | **−0.229** [−0.278, −0.185] | 0.457 | 75.1% |
| Local qwen3:8b | 284 | −0.081 [−0.136, −0.028] | 0.518 | 74.3% |

### Rubric prompt v2 vs v3

| Set | Version | Leniency | QWK | 2-way accuracy |
|---|---|---|---|---|
| Dev (115) | v2 | −0.096 | 0.565 | 80.0% |
| Dev (115) | v3 | −0.074 | 0.616 | 83.5% |
| Test (302) | v2 (297 scored) | −0.088 | 0.591 | 77.8% |
| Test (302) | v3 | −0.066 | 0.577 | 78.1% |

v3 is consistently a little less harsh. Agreement (QWK) is the same within noise. On the dev set, the paired difference wasn't significant: 13 of 115 grades changed, and 6 of those moved closer to the human grade.

## Decisions

1. **Judge: Gemini 3.5 Flash Lite.** It has the best QWK and accuracy of the three candidates and passes the leniency target on the point estimate. It is also the only free option with enough daily volume (500 requests/day).
2. **Qwen on Groq is rejected as a judge.** It is clearly harsher (−0.23) and agrees less with humans (QWK 0.46). It stays the *verifier* for now, but **Phase 5 must test that role directly** (verifier test set, false-accept rate). If it fails, the verifier needs a different model.
3. **Local qwen3:8b never grades.** Its agreement is lower, and 13 of 302 replies were unusable. It stays in non-grading roles (phrasing, perturbations).
4. **Rubric prompt v3 is kept for dataset-derived rubrics.** The production rubric generator (Phase 3) is a different prompt, so the lessons below matter more than v3 itself.

## Known weaknesses, carried into later phases

| Weakness | Evidence | Where it is handled |
|---|---|---|
| Harsh on SciEntsBank | −0.13. About half of the misses read are generous human labels, e.g. *"a lizard needs food, home, space"* marked correct for *"a separate shelter for each lizard"*; the rest is real literalness | Not chased further, so the engine isn't tuned toward lenient labels. Phase 4 golden tests include correct paraphrases. |
| No partial credit with single-criterion rubrics | All 10 partially-correct SciEntsBank dev answers scored 0 | Phase 3: criteria must be granular; at least 2 per path unless the question is a single atomic fact. |
| Rubrics adding requirements the question doesn't ask for | v1 rubrics required explanations the reference never gave | Phase 3: the rubric lint rule "nothing beyond the stated idea". |
| Weak contradiction detection | Of 65 human-"contradictory" answers, only 21 were flagged as contradictory (32%). Wrong claims often need context the question text doesn't give | Phase 4/7: measure again with the "insert a factual error" perturbation, where the context is known. |
| 12% label flips at temperature 0 | Stability run | **New decision D6** (plan §3): an identical resubmission is answered from the cache, so it's deterministic. For borderline verdicts, Phase 4 evaluates a majority of 3 calls (3× cost) on a subset. |

## Engineering lessons (free tiers)

| Provider | Lesson |
|---|---|
| Gemini | Flash models allow only 5 RPM / 20 RPD; Flash Lite 15 / 500. The newest models return 503/504 under load. A 429 states its wait ("retry in 34 s"), and a second process can't see the first one's per-minute window. |
| Groq | 200K tokens/day per model. Qwen has an unlisted **1,000 output tokens/min** cap. Constrained-JSON mode broke on our schemas with Qwen (55% failures); plain JSON mode fixed it. Groq's daily count runs ahead of ours, so its 429 is authoritative. |
| Process | Keep the test set untouched while tuning. In this dataset, test and train share questions, so the dev set must exclude test questions. Cache keys must stay stable, or a resume re-pays for every finished call. |
