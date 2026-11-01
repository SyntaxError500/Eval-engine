# Phase 5: amendment and verification findings

Date: 2026-11-01. Proposer: gpt-oss-120b on Groq (`amendment_propose` v1). Verifier: Qwen 3.8 on
Groq (`amendment_verify` v1). Judge: gemini-3.5-flash-lite (`score_answer` v2). Test set: 95 items
on 19 questions, written up in `review.md`; verifier numbers in `REPORT.md`; end-to-end outcomes
in `e2e.json`.

**Status: the gate passes on hand-checked labels. External review of those labels is pending**,
and it decides the gate (my own reviews were far too lenient in Phase 3).

## Exit gate

| Gate item | Result |
|---|---|
| Precision, recall and per-class rejection, both framings | Reported below and in `REPORT.md` |
| False accepts on class (a) at most 10% | **0/27** in both framings (19 nonsense + 8 misconceptions). 95% CI 0-12%, so the data can't yet rule out a rate just above 10% |
| Amendment fires on under 15% of ordinary golden answers | **1/30 (3%)** at threshold 0.5 (was 10/30 under `score_answer` v1) |

## Verifier test set

| Measure | Adversarial | Neutral |
|---|---|---|
| Recall on valid approaches | 15/16 (94%, CI 72-99%) | 16/16 (100%, CI 81-100%) |
| Precision of acceptances | 15/17 (88%, CI 66-97%) | 16/18 (89%, CI 67-97%) |
| Rejected: nonsense | 19/19 | 19/19 |
| Rejected: misconception | 8/8 | 8/8 |
| Rejected: invalid reasoning | 13/13 | 13/13 |
| Rejected: holed | 12/12 | 12/12 |
| Rejected: restatement | 25/27 | 25/27 |

**Decision: Qwen stays as verifier.** Phase 2 rejected it as a judge and required it to prove
this role on its own merits; it did.

**Decision: adversarial framing stays, on design grounds rather than data.** The framing made no
measured difference: the same 2 false accepts, and one extra false reject that is defensible
(it called habit-based key loss a narrower case of the attention path). The interesting result
the design hoped for did not appear on this set.

Both false accepts are the same two items under both framings: the molecular account of a
hot-air balloon and a shorter 5G transmission interval. Each is a correct sub-case of a listed
path, so the cost is a redundant path, not credit for a wrong answer.

## End to end: can a wrong answer earn its own path?

The test above hands the verifier its paths. This runs the whole chain on the 24 answers that
trigger amendment, each in a throwaway store so the real rubrics are untouched.

| Class of answer | n | Accepted | Verifier rejected | Proposer declined | Failed checks |
|---|---|---:|---:|---:|---:|
| Valid | 8 | 5 | 1 | 0 | 2 |
| Nonsense | 5 | 0 | 0 | 5 | 0 |
| Misconception | 3 | 0 | 0 | 3 | 0 |
| Invalid reasoning | 3 | 0 | 0 | 3 | 0 |
| Holed | 4 | 1 | 0 | 3 | 0 |
| Golden wrong | 1 | 0 | 0 | 1 | 0 |

**No wrong answer earned a path.** The one accepted "holed" case was read by hand: the hole was
in the authored path, while the learner's answer is a sound account of incentives and sanctions,
and the proposer wrote a complete path for it. That label doesn't carry over to the answer.

The 5 accepted valid answers rose from 0.18-0.47 to 1.00 after a re-score on the new version.

## Calibration

| Group | n | fire at < 0.3 | < 0.4 | < 0.5 | < 0.6 | < 0.7 |
|---|---|---|---|---|---|---|
| Golden good and paraphrase | 8 | 0 | 0 | 0 | 0 | 0 |
| Golden partial | 4 | 0 | 0 | 0 | 1 | 1 |
| Golden wrong | 4 | 0 | 1 | 1 | 3 | 3 |
| Valid unlisted | 16 | 4 | 7 | 8 | 9 | 9 |

**Decision: the threshold stays at 0.5.** Moving to 0.6 gains one valid answer and adds three
wrong or partial ones. That would still pass the gate (4/30, 13%), but it is a poor trade: each
false firing spends a proposer call, and 4 of the 16 ordinary multi-path answers would fire.

## What the hand check found (why the first test set was thrown away)

The first author run produced 88 items that would have given a meaningless result:

1. **Flaws leaked into the text.** Descriptions said "employs circular reasoning", "paraphrases
   Path P1", "pseudoeconomic". Rejecting those proves nothing. The author prompt is now v2 and
   `_leaks` rejects any such text in code.
2. **Most "valid" items weren't.** 10 of 17 were a new argument for a listed position, a sub-case
   of a mechanism-agnostic path, or a refusal of the question's forced choice. Valid items are
   now hand-curated (`curated.yaml`), and those 10 stay in the set under their true class as the
   hardest negatives.
3. **Many "holed" paths had no hole.** The gap was in the sample answer, not in the path the
   verifier sees.
4. **Nonsense was too easy.** Invented mechanisms ("lunar tidal pull on masonry") barely test the
   costly error, so 8 hand-written misconceptions were added as their own class ("5G waves travel
   faster than 4G waves"), held to the same gate. A confidently wrong learner answer looks like
   these.

The regenerated set needed 10 more decisions, recorded with reasons in `review.json`.

## Other changes

- **`score_answer` v2.** Path confidence now asks which path the answer is *attempting*, not how
  well it fits. New `addresses_question` separates an answer about something else from a real new
  approach: both have low confidence on every path, so the signal proposed in Phase 4 (low
  confidence, no core criterion met) couldn't tell them apart. It flagged 5 of the 6 non-creative
  off-topic golden answers; the sixth, macro-off, is factual, where amendment can't run anyway.
  Golden is now **40/40** (macro-partial now passes), but that is one run and the judge flips 12%
  of labels between runs, so treat the extra pass as noise until shown otherwise.
- **Amendment applies to multi-path rubrics only.** A factual checklist has one right answer, and
  the schema allows it one path.
- **The verifier never sees the learner's answer.** An accepted path joins the rubric for every
  later answer, so it has to stand on its own, however well this answer was written.
- **A proposal must pass the same per-path checks as a generated rubric** before it reaches the
  verifier, with one retry. A provider failure leaves the grade on the original rubric and marks
  the trace.

## Known limits

- **The ceiling is only partly solved.** Of 16 valid answers, 5 already score full marks on a
  listed path and 11 are under-scored. Of those 11, the trigger catches 8, and 5 of the 8 end up
  accepted. So 5 of 11 under-scored valid answers are rescued.
- **3 of those 11 never trigger.** The judge is confident (0.8-1.0) they are on a listed path
  (profit-margin route on the price-effect path, plant-input route, memory interference). No
  threshold catches these without firing on wrong answers. The cost is a learner being marked down
  for a valid route, which the design accepts as the cheap error.
- **2 of the 8 fell to the code checks**, safely but needlessly. The proposer omitted a correctness
  criterion, and added a length criterion copied from the question. Fix: two lines in the proposer
  prompt. Not applied yet, because rerunning needs about 50K Groq tokens and today's key is spent.
- **The verifier was barely tested end to end.** The proposer declined all 15 wrong answers, so no
  proposer-written wrong path reached the verifier. Its evidence comes from the test set alone.
- **Small and related samples.** 8 misconceptions give a CI up to 32%. Several valid items share a
  question, because few questions have room for another route: forced-choice questions and
  single-mechanism science have none, which is itself a finding about how often the ceiling
  matters.
- **I wrote 10 of the 16 valid items and all 8 misconceptions**, so they may be easier for a model
  to judge than what real learners write. This is the main reason external review matters.

## Cost

Verifier runs: 190 Qwen calls, about 160K tokens. Test set authoring: about 250 Gemini calls
across both author runs. Calibration: 95 Gemini calls. End to end: 30 gpt-oss calls, 7 Qwen
calls, 6 Gemini calls.
