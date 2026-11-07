# Evaluation & Feedback Engine: final report

The engine grades a human's short answer against a rubric frozen with the question, never against
an LLM's own answer, and returns feedback a learner can act on. It runs on free-tier models
only. Every validation figure below can be regenerated from cached responses with one command,
`eval-engine reproduce`.

## What was built

Each question is generated with its rubric. The rubric is code-checked, fact-checked by a
different model family, and frozen with a hash. A learner's answer then goes through these steps:

1. **Grading.** One judge call identifies which of the rubric's solution paths the answer takes
   and decides each criterion (D1). Code checks follow: every "met" must quote the answer, a
   quote listed as a factual error can't count, and counts are verified. Aggregation into
   dimension scores and bands is done in code, never by a model.
2. **Amendment, rarely.** When the judge is unsure the answer follows any listed path, a proposer
   (a different model family) may propose a new path. A verifier (a third family) must accept it
   before it joins the rubric as a new version. The original version stays binding until then.
3. **Feedback.** Code chooses and ranks what to say. A local model phrases it under code checks:
   it may quote only the answer, mention no rubric internals, and leak nothing. Templates are the
   fallback.
4. **The app (Phase 8).** A learner gets a reviewed question or one generated on the spot
   (labelled unreviewed). They see feedback, then bands, and can discuss the answer with a tutor
   or ask for one re-check by the judge's model. When a model is down, there is a fixed fallback
   for each role. The judge's is a queue: an answer is never graded by another model.

## Gates

| Phase | Gate | Result | Source |
|---|---|---|---|
| 0 | Live call to every provider | Passed | `eval-engine smoke` |
| 1 | Swapping a model is a config change only | Passed | `config/roles.yaml` |
| 2 | Judge leniency on borrowed human-graded answers, absolute value at most 0.1 | **Passed** on the point estimate: −0.066 [−0.113, −0.018], 302 answers; the interval reaches slightly past −0.1 | `experiments/2_judge_pilot/test_v3/REPORT.md` |
| 3 | At least 85% of generated questions pass a strict external review | **Passed:** 37/40 (92.5%), on the third review round | `experiments/3_generation/FINDINGS.md` (human review) |
| 4 | Golden tests (10 per task type) | **Passed:** 39/40 within range under the final judge | `experiments/4_eval/golden_report.md` |
| 5 | False accepts on nonsense and misconceptions at most 10% | **Passed:** 0/23 (95% CI 0–14%) | `experiments/5_verifier/REPORT.md` |
| 6 | At least 90% of feedback passes external review | **Passed:** 27/30, exactly the threshold | `experiments/6_feedback/FINDINGS.md` (human review) |
| 7 | Leniency on the borrowed corpus and a human-graded set; perturbation attribution at least 70% | **Corpus passed** (−0.035 [−0.081, +0.013]). **Human set passed** (−0.010 [−0.096, +0.070], QWK 0.82). **Perturbation NOT MET** (19/37, 51% [36–67%]) | `docs/VALIDATION_REPORT.md` |
| 8 | Degradation paths verified; a new user reaches feedback in under 2 minutes unaided | **Degradation 3/3 passed. Usability not yet tested on a first-time user** (72 s with the builder) | `experiments/8_interface/` |
| 9 | Fresh clone runs the demo from the README; every validation figure regenerates with one command | See below | this report |

### Phase 9

| Gate item | Result |
|---|---|
| Every validation report regenerates from cached responses with one command | **9/9 identical** with `eval-engine reproduce`: no live calls (a cache miss is an error), run on a copy of the database |
| A fresh clone plus `.env` runs the demo from the README alone | **Passed** on a copy holding only what git would clone, following the README's steps with an `.env` without API keys: install from `requirements.lock`, `snapshot import`, 320 tests pass, `reproduce` 9/9 identical, the app renders a reviewed question and the server answers its health check. The first run caught a real bug: app evaluations in the snapshot made the amendment-frequency report differ (fixed; `experiments/9_hardening/FINDINGS.md`) |

Not regenerable by nature: the Phase 3 and 6 gates are human reviews, and the Phase 8 checks
break providers or call models live on purpose.

## What the validation says

- **No systematic bias, overall.** Leniency is inside ±0.1 on both the borrowed corpus and the
  human set. The human set orders answers as the graders do: Spearman 0.84, QWK 0.82.
- **The overall bias hides two errors that cancel.**
  - **Too harsh on single-error answers.** Both human graders called 7 of the 10 single-error
    answers "partially correct", while the engine's overall label gave all 10 a 0.
  - **Too lenient on missed false facts.** Some answers with a false statement both graders
    flagged got full marks.

  Fixing only the first would make the engine lenient. This is the top open decision.
- **Reasoning is the weak dimension.** Perturbation attribution is 19/37 (51%) under the strict
  rule. Criteria that ask only for "a reason" are met by an irrelevant one, whatever the judge
  prompt says.
- **Amendment is rare and safe on the test sets.** On reviewed-bank questions under the final
  judge, it would fire on 1/10 explanatory and 0/10 analytical answers. On the Phase 5 test set:
  - every valid unlisted route that fired was accepted (8/8);
  - every nonsense or misconception answer that fired was declined;
  - one "holed" path was accepted.

  The sources are `experiments/9_hardening/AMENDMENT_FREQUENCY.md` and
  `experiments/5_verifier/FINDINGS.md`.
- **Disputes.** The tutor can't change a grade. The re-check held 6/6 invalid appeals live but
  granted 0/2 valid ones: it is conservative. One live discussion exposed a judge verdict that
  contradicted its own justification.

## Limits

- **Every test answer was written to probe the engine.** None comes from a real learner, so the
  rates bound the machinery; they don't predict use.
- **The human set's two graders agree almost perfectly** (κ 1.00). That limits what agreement
  with them can show.
- **The judge changes its label on about 12% of answers** across identical runs (Phase 2).
  Identical resubmissions are answered from the cache.
- **Creative grading is the weakest part.** Its rubrics are craft tests; originality is feedback
  only (D3).
- **Free tiers may train on what they receive.** The app is a local demo, with no accounts.

## Models used for the final results

From the call log (calls without errors), 2026-10-28 to 2026-11-07:

| Role | Provider / model | Calls |
|---|---|---|
| judge | gemini / gemini-3.5-flash-lite (`score_answer` v3 final, frozen) | 4,291 |
| fact_checker, rechecker, verifier_set_author | gemini / gemini-3.5-flash-lite | 76, 13, 682 |
| generator, reference_answer, amendment_proposer | groq / openai/gpt-oss-120b | 605, 142, 98 |
| perturber, tutor | groq / openai/gpt-oss-120b | 350, 24 |
| verifier | groq / qwen/qwen3.8-27b | 406 |
| feedback_phraser, tutor fallback and earlier tutor runs, early perturber | ollama / qwen3:8b | 204, 42, 308 |
| Phase 2 candidates (not adopted) | groq / qwen/qwen3.8-27b; ollama / qwen3:8b | 604; 298 |

Library versions are pinned in `requirements.lock` (Python 3.13.4).

## Where everything is

- **Decisions and evidence:** `docs/DECISIONS.md`.
- **Validation:** `docs/VALIDATION_REPORT.md`, which ends with the open backlog.
- **Each phase:** `experiments/<phase>/FINDINGS.md`.
- **Setup and commands:** `README.md`.
