# Phase 5: amendment and verification findings

Dates: built 2026-11-01; external review applied and rerun 2026-11-03.

| Part | Model | Prompt |
|---|---|---|
| Proposer | gpt-oss-120b on Groq | `amendment_propose` v2 |
| Verifier | Qwen 3.8 on Groq | `amendment_verify` v1 |
| Judge | gemini-3.5-flash-lite | `score_answer` v2 |

The test set has 89 items on 19 questions, after external review 1 (`REVIEW_1_DECISION.md`). The
items are in `review.md`, verifier numbers in `REPORT.md` and end-to-end outcomes in `e2e.json`.

**Status: gate passed on externally reviewed labels.** Three paths revised after the review follow
the reviewer's own wording, and were not reviewed a second time.

## Exit gate

| Gate item | Result |
|---|---|
| Precision, recall and per-class rejection, both framings | Reported below and in `REPORT.md` |
| False accepts on class (a) at most 10% | **0/23** in both framings (15 nonsense + 8 misconceptions). 95% CI 0-14%, so a rate just above 10% can't be ruled out on this sample |
| Amendment fires on under 15% of ordinary golden answers | **1/30 (3%)** at threshold 0.5 (was 10/30 under `score_answer` v1) |

## Verifier test set

| Measure | Adversarial | Neutral |
|---|---|---|
| Recall on valid approaches | 13/14 (93%, CI 69-99%) | 14/14 (100%, CI 78-100%) |
| Precision of acceptances | 13/15 (87%, CI 62-96%) | 14/16 (88%, CI 64-97%) |
| Rejected: nonsense | 15/15 | 15/15 |
| Rejected: misconception | 8/8 | 8/8 |
| Rejected: invalid reasoning | 14/14 | 14/14 |
| Rejected: holed | 11/11 | 11/11 |
| Rejected: restatement | 25/27 | 25/27 |

**Decision: Qwen stays as verifier.** Phase 2 rejected it as a judge and required it to prove this
role on its own merits; it did.

**Decision: adversarial framing stays, on design grounds rather than data.** The framing made no
measured difference: the same 2 false accepts, and one extra false reject that is defensible. It
called habit-based key loss a narrower case of the attention path. The interesting result the
design hoped for did not appear on this set.

Both false accepts are the same two items under both framings: the molecular account of a hot-air
balloon and a shorter 5G transmission interval. Each is a correct sub-case of a listed path, so
the cost is a redundant path, not credit for a wrong answer.

## End to end: can a wrong answer earn its own path?

The test above hands the verifier its paths. This runs the whole chain on the 23 answers that
trigger amendment, each in a throwaway store so the real rubrics are untouched.

| Class of answer | n | Accepted | Proposer declined |
|---|---|---:|---:|
| Valid | 8 | **8** | 0 |
| Nonsense | 5 | 0 | 5 |
| Misconception | 3 | 0 | 3 |
| Invalid reasoning | 3 | 0 | 3 |
| Holed | 3 | 1 | 2 |
| Golden wrong | 1 | 0 | 1 |

No case was rejected by the verifier or failed the code checks, so those columns are left out.

**No wrong answer earned credit for what it lacks.** The one accepted holed answer was read by
hand. Its route, enforcement by authority, is a valid explanation, and the proposer wrote a sound
path for it. That path's own completeness criterion then caught the missing step: why enforcement
beats a moral objection. The answer scored 0.71, not 1.00. A valid route was added and the gap
was still penalised, which is the design working.

All 8 accepted valid answers rose from 0.18-0.47 to 1.00 after a re-score on the new version.

**`amendment_propose` v2** fixed the two valid answers that v1 lost to the code checks. One had no
correctness criterion; the other copied the question's sentence count into a criterion. The fix
also moved the authority answer to acceptance: v1 had written it a path the verifier rejected.

## Calibration

| Group | n | fire at < 0.3 | < 0.4 | < 0.5 | < 0.6 | < 0.7 |
|---|---|---|---|---|---|---|
| Golden good and paraphrase | 8 | 0 | 0 | 0 | 0 | 0 |
| Golden partial | 4 | 0 | 0 | 0 | 1 | 1 |
| Golden wrong | 4 | 0 | 1 | 1 | 3 | 3 |
| Valid unlisted | 14 | 4 | 7 | 8 | 8 | 8 |

**Decision: the threshold stays at 0.5.** Raising it catches no more valid answers on this set
and fires on three more wrong or partial ones.

## What the reviews found

**My hand check** threw away the first author run. Its paths named their own flaws ("employs
circular reasoning"), and 10 of 17 "valid" items weren't valid. Three changes followed: author
prompt v2, a code check (`_leaks`), and hand-curated valid items. The misconception class was
added because the invented mechanisms were too absurd to test the costly error.

**External review 1** kept 84 of 95 labels, relabelled 2 and flagged 9:

- **Two "valid" items were not secure novelty tests.** The judge had already scored both 1.00 on
  a listed path.
- **Three mandatory criteria stated something false or backwards.**
- **Two "nonsense" items were metaphor or real research.**
- **Two labels depended on the learner answer**, which the verifier never sees.

It also showed that 8 holed trigger answers supplied the very step their path omits. All of it was
applied; see `REVIEW_1_DECISION.md`. The verifier's results didn't move, which is some evidence
that they don't rest on the mislabelled items.

## Other changes

- **`score_answer` v2.** Path confidence now asks which path the answer is *attempting*, not how
  well it fits. New `addresses_question` separates an answer about something else from a real new
  approach: both have low confidence on every path, so the signal proposed in Phase 4 couldn't
  tell them apart. It flagged 5 of the 6 non-creative off-topic golden answers; the sixth,
  macro-off, is factual, where amendment can't run anyway. Golden is now **40/40**, but that is
  one run and the judge flips 12% of labels between runs, so treat the extra pass as noise until
  shown otherwise.
- **Amendment applies to multi-path rubrics only.** A factual checklist has one right answer, and
  the schema allows it one path.
- **The verifier never sees the learner's answer.** An accepted path joins the rubric for every
  later answer, so it has to stand on its own, however well this answer was written.
- **A proposal must pass the same per-path checks as a generated rubric** before it reaches the
  verifier, with one retry. A provider failure leaves the grade on the original rubric and marks
  the trace.

## Known limits

- **The ceiling is mostly, not fully, solved.** Of 14 valid answers, 3 already score full marks on
  a listed path and 11 are under-scored. The trigger catches 8 of the 11, and all 8 are rescued.
- **3 under-scored valid answers never trigger.** The judge is confident (0.8-1.0) they are on a
  listed path: the profit-margin route, the plant-input route and memory interference. No
  threshold catches these without firing on wrong answers. A learner taking such a route is
  marked down, which the design accepts as the cheap error.
- **The verifier was barely tested end to end.** The proposer declined every wrong answer, so no
  proposer-written wrong path reached the verifier. Its evidence comes from the test set alone.
- **Small and related samples.** 8 misconceptions give a CI up to 32%. Several valid items share a
  question, because few questions have room for another route. Forced-choice questions and
  single-mechanism science have none, which is itself a finding about how often the ceiling
  matters.
- **I wrote 10 of the 14 valid items and all 8 misconceptions**, so they may be easier for a model
  to judge than what real learners write. The external review checked their labels, not their
  difficulty.
- **Learner answers outside the holed class keep some factual slips** (`REVIEW_1_DECISION.md`).
  They never serve as a reference.

## Cost

| Run | Calls |
|---|---|
| First run, 2026-11-01 | 190 Qwen (verifier); about 250 Gemini (authoring, both author runs); 95 Gemini (calibration); 30 gpt-oss, 7 Qwen and 6 Gemini (end to end) |
| Rerun after review, 2026-11-03 | 15 Qwen, 23 gpt-oss and 17 Gemini. Everything unchanged came from the cache |
