# Phase 6: feedback and output findings

Date: 2026-11-03. Phrasing model: qwen3:8b on local Ollama (`feedback_phrase` v2). Review set:
30 evaluations in `review.md`; raw traces in `cases.json`.

**Status: gate passed on external review 1, 27/30 (90%), exactly the threshold. D5 confirmed:
local qwen3:8b keeps phrasing (3/30 failures, under the 20% rule).** The three failures (E11,
E16, E30) traced to causes in code, which are fixed; see `REVIEW_1_DECISION.md`. The six
edited evaluations have not been reviewed again.

## How feedback is made

1. **Selection is in code** (`feedback/select.py`). Candidates are the failed criteria on the path
   used, plus the factual errors the judge listed, ranked core first, then by weight x dimension
   weight. Two problems, or three when the third is core, then one or two met core criteria as
   what worked. An answer about something else gets one point only.
2. **Phrasing is by the local model** (`feedback/phrase.py`). It gets the chosen points, the
   judge's notes and the answer's own words. It never sees the reference answer, the scores or
   the bands.
3. **Every phrased point is checked in code.** It must:
   - speak to the learner as "you";
   - quote only the answer or the question;
   - not repeat a 6-word run from the reference answer that isn't also in the rubric, the
     question or the answer;
   - not mention grading internals or prompt labels;
   - stay under 60 words.

   A failing point is re-phrased once, then falls back to a plain template. Feedback is never
   missing, and never unchecked.
4. **Route notes:**
   - An accepted amendment gets a fixed neutral sentence.
   - A route that didn't hold up gets a fixed opening sentence, with the model supplying only
     the reason. That keeps the distinct voice (design doc §15).
   - A proposal that only failed code checks, or a provider failure, gets no route note, because
     neither is a reason to give a learner.
5. **What the learner sees:** feedback first, then one coarse band per dimension, with no
   numbers and no aggregate (`feedback/render.py`; the `evaluate` command shows details below
   it).

## Decisions

- **Factual errors are feedback points.** The plan ranks only failed criteria, but a false
  statement costs correctness through the implicit no-errors check, so the learner is told
  which statement was wrong.
- **Merging points that share one mistake.** In the first run, "vitamins are a macronutrient"
  produced three points saying the same thing. Points now merge in three cases:
  - a criterion depends on another ("the phase named in C5");
  - the judge's note on a failed criterion is about a listed error: a shared run of 3 words with
    its quote, or at least 3 content words with its quote and explanation;
  - two criteria are near-identical.
- **Code supplies what models get wrong.**
  - Sentence counts come from code, met or not; the model stated a wrong count in the first run.
  - A verdict a code check overturned keeps none of the judge's reasons for passing.
- **Originality stays feedback only (D3).** A creative piece that reuses an obvious answer gets
  a fixed note that says it wasn't marked down.

## Runs

| Run | Model points | Template fallbacks | Fixed notes | What the pre-check found |
|---|---|---|---|---|
| v1 prompt, first selection | 92 | 0 | 6 | A literal "null" shown to a learner. "The student" / "the answer" instead of "you". Prompt labels copied ("Why it is wrong:"). One mistake told three times (E2, E4, E28, E29). The proposer's verdict copied as the route note. A sentence count the model made up |
| v2 prompt, merges, stricter checks | 79 | 6 | 6 | "It didn't hold up:" doubled in all 4 route notes. The leak check fired on ordinary phrases at 5 words ("because the heated air is"), causing 5 of the 6 fallbacks |
| Final: opener stripped, leak at 6 words with the rubric allowed | 83 | 2 | 6 | See below |

**The v1 run passed every code check with 0 fallbacks, yet had all the problems above.** The
checks were too weak, not the output too good. Each problem found now has a check or a code rule,
and a test.

## My pre-check of the reviewed run (a filter, kept for comparison with the review)

At most 3 problem points everywhere, no reference leakage found, route notes in the right
voice, and no unchecked text. Likely weak spots for the review:

- **E2 (cell-partial):** two points both say "name a third phase". The phase-count criterion
  doesn't reference the others, so nothing merges it.
- **E30 (nonsense answer):** "what worked" says the answer explains how depreciation affects
  competitiveness. That is faithful to the judge, which passed a generic criterion on nonsense,
  but it misleads the learner. It is grading leniency surfacing in feedback.
- **E29 and E6:** points overlap in content (approval; naming the macronutrients), though each
  rests on a different criterion.
- **E13:** the second point mixes "state your position" with a suggested reason.

My Phase 3 pre-reviews were far too lenient, so I put no number on these. The review passed all five and failed three I hadn't flagged (E11, E16, E30). My filter caught overlap, the review caught a misstatement, a generic off-topic note and a generic template.

## D5 (which model phrases)

**Confirmed: local qwen3:8b.** It failed 3 of 30 in review (10%), under the plan's 20% switch-over
rule, and one of those was a code template. It wrote 83 of the 85 non-fixed points in the
reviewed run, at 10.9 s per evaluation on average (20 s at most) on the RTX 3050, with no parse
failures.

## Known limits

- **Feedback inherits grading leniency** (E30). Selection takes verdicts as given, so a criterion
  the judge wrongly passes becomes "what worked".
- **The merge rules were tuned on this review set**, on about 7 cases. They are tested, but other
  rubrics may need different thresholds. Nothing merges two criteria that fail for the same
  reason without referring to each other (E2).
- **The leak check is a guard, not the protection.** The phraser never sees the reference answer,
  so overlap can only be coincidence. The check exists because the plan asks for it, and it
  blocked 1 coincidental phrase in the final run.
- **About 11 s of local phrasing per evaluation** adds to the judge call. That matters for the
  Phase 8 two-minute target, and will need an "evaluating…" state.

## After external review 1

Three code changes:

- **Off-topic notes must name the answer's topic.** They need a word stem from the answer that
  isn't in the question.
- **Back-references merge into one point.** A failed criterion that refers back to "the example"
  joins the point that asks for one.
- **Worked templates quote the credited words.**

The comparison sketch is also labelled as a comparison. Two regressions in evaluations the
reviewer had passed (E14, E15) were caught by diffing against the reviewed text, and fixed before
this was recorded. Final run: 81 model points, 3 templates, 6 fixed notes. Only the six intended
evaluations differ from the reviewed text.

**For later changes:** diff a rerun against the reviewed `cases.json`, not just the fallback
count. Both regressions passed every test.
