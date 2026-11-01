# Phase 4: evaluation core findings

Date: 2026-11-01. Judge: gemini-3.5-flash-lite (`score_answer` v1, `score_creative` v1).
Golden set: `golden.yaml` (40 hand-written answers: 8 questions from the accepted Phase 3
batch, 2 per task type, 5 answers each). Expected score ranges were written before any judge
run. Full table: `golden_report.md`; D6 study: `d6_votes.md`.

## Exit gate

| Gate item | Result |
|---|---|
| End-to-end CLI | `eval-engine evaluate --question <id> --answer-file a.txt` prints path + confidences, verdicts, errors, code-check downgrades, dimension scores and bands. Done |
| Golden tests, 10 per task type, run against cached responses | 40 items (10 per task type: good / paraphrase / partial / wrong / off-topic; creative uses obvious, cliché and constraint-breaking variants). **39/40 within range.** `tests/test_golden_replay.py` replays the recorded judge replies with no network and fails if any score, path or pass/fail changes |
| Evidence-check catch rate on 20 unsupported verdicts | **20/20** downgraded (`test_evidence_check_catch_rate_on_20_unsupported_verdicts`). False downgrades on the 40 genuine golden answers: **0** (after the fragment fix below) |
| D1 and D3 confirmed or revised | D1 confirmed, D3 revised (below) |

## What the golden set found, and what changed

1. **The evidence check rejected relational quotes.** The first live run downgraded "the three
   phases named are all different" because the judge quoted `G1, S phase, M phase` from three
   places. On fire-too-long it also rejected two quoted sentences from different places.
   **Fix:** evidence is split into fragments on `, ; … /` and sentence ends, and every
   fragment must be in the answer. An invented fragment still fails (tested).

2. **The judge contradicts itself.** On macro-wrong it marked "states a function of the first
   macronutrient" as met on *"Carbohydrates are mainly used to build bones"* while listing
   that same sentence as a factual error. Correctness came out 0.75 for an answer whose three
   functions are all wrong. wwi-wrong did the same: it passed only because its range was wide.
   **Fix (code, no prompt change):** a met verdict whose evidence is the same statement as one
   of the judge's own error quotes is downgraded (`contradiction_downgrades` in the trace).
   "Same statement" means containment with at least 3 words on the shorter side, or 0.85 fuzzy
   similarity, so a shared noun ("carbohydrates") isn't enough. It fired on 5 verdicts, all in
   the two wrong answers, and on nothing else.

3. **The judge can't count sentences.** On a 10-sentence piece its justification counts to ten
   and then marks "between three and eight sentences" as met. **Fix:** criteria stating a
   sentence range are decided in code (`evaluation/counts.py`, `count_overrides` in the trace)
   in both directions.

4. **Remaining miss: macro-partial.** The answer calls vitamins the third macronutrient. The
   judge passed "names three distinct macronutrients" while its justification says vitamins are
   micronutrients. This is plain leniency on one criterion. The contradiction rule doesn't catch
   it: the evidence `Carbohydrates, Proteins, Vitamins` isn't the flagged sentence, and
   loosening the rule to match single words would downgrade correct verdicts (see 2). The
   implicit no-errors check still costs the answer correctness (0.50). Left as a recorded miss.

5. **Paraphrases are not penalised.** Phase 2 flagged the judge as literal-minded. All 8
   paraphrased-but-correct answers (no rubric wording: "growth gap / synthesis stage /
   division stage", "warm air weighs less", "Death Valley, east of the Sierra Nevada") scored
   full marks with `score_answer` v1's guidance on everyday words and synonyms.

## Decisions

- **D1 confirmed.** One merged call per answer did path identification and scoring: 40
  answers, 40 judge calls. Every expected path was identified, including both answers on the
  second path (wfh-paraphrase P2 at 1.00; wwi-nationalism P2 at 0.95).
- **D3 revised: originality is a feedback signal, never scored.** Phase 3 established that
  briefs don't state originality as a requirement, so scoring it would test something the
  learner wasn't asked for. The creative judge still reports obvious-answer overlap
  (`obvious_overlap` in the trace). coffee-obvious was flagged as reusing obvious answer 2
  and was not marked down. Cliché checks that the brief asks for (fire-cliche: "phoenix
  rising") are ordinary criteria and do count under expression (0.50).
- **D6: majority of 3 is not adopted; single vote stays the default.** 15/40 items count as
  borderline (low path confidence, or exactly one unmet core criterion). Re-voting them cost
  30 extra calls (75% more judge calls on this set) and changed **0** scores. `--votes 3`
  stays available. Revisit on the human-graded set in Phase 7, where disagreement with the
  judge can be measured directly. An identical resubmission is still answered from the cache.

## Carried into Phase 5

Both points below were resolved by `score_answer` v2: see `experiments/5_verifier/FINDINGS.md`. The golden report and fixture now record v2 (40/40).

- **Path confidence measures fit, not intent.** The judge gives low confidence to answers
  that *attempt* the only path but do it badly: balloon-wrong 0.10, rain-wrong 0.10,
  balloon-partial 0.30, and every off-topic answer 0.00–0.20. At the 0.5 threshold, 10 of 30
  non-creative golden answers would trigger amendment, and none of them is a new valid
  approach. Phase 5 must either reword the confidence instruction ("which path is the answer
  attempting", not "how well does it satisfy it") or measure that the proposer reliably
  rejects these. Otherwise amendment cost scales with the number of weak answers.
- An off-topic answer should probably skip amendment altogether. Candidate signal: every
  path's confidence ≤ 0.2 *and* no core criterion met.

## Cost

Golden run: 40 Gemini Flash Lite calls (~1.8K tokens each). Re-recording after code changes is
free (judge replies are cached). D6 study: 30 calls.
