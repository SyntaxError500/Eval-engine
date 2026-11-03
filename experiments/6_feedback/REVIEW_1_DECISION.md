# Feedback review set: external review 1 and decision

Review date: 2026-11-03 (`external_review_1.md`). The review covered all 30 evaluations against
the 7-point checklist.

**Result: 27/30 pass (90%). The gate (at least 27/30) is passed, with no margin.**

**D5 is confirmed: the local model keeps phrasing.** It failed 3 of 30 evaluations (10%),
under the plan's 20% switch-over rule. One of the 3 (E30) was a code template, not the model.

## Cross-check

I agree with all three failures. Each pointed at a cause in code, not just a bad sentence:

| Evaluation | Failure | Cause | Fix |
|---|---|---|---|
| E11 | Off-topic note could fit any answer; never names the monsoon explanation | Nothing required the note to say what the answer is about | A code check: the note must share a word stem with the answer that isn't in the question. Failing twice gives a template that quotes the answer's opening |
| E16 | Says the learner doesn't explain how alliances caused the war (they gave a general account); calls the July Crisis an alliance | "Give an example" and "explain how *the example* shows it" became two points, so the second was phrased as a missing explanation | Among failed criteria, one that refers back to "the example", "the evidence" or similar joins the point that asks for it |
| E30 | "What worked" restated the criterion, naming nothing in the answer | The template restated the criterion | The worked template quotes the words the judge credited |

The reviewer's optional suggestions applied: the "predictable take" sketch is now labelled as a
comparison (E18, E21, E22), so its details aren't mistaken for the learner's own scene.

Not applied: merging E2's two points and E6's overlap, E13's wording, a second error point for
E17, and E20's setting wording. None affects pass or fail. They would need selection or prompt
changes that rewrite reviewed evaluations.

## After the fixes

The two regressions this caught before release were both in evaluations the reviewer had passed:

- **E14:** the new check rejected "company productivity" because the answer says "productive";
  it now matches word stems.
- **E15:** the back-reference merge also merged met criteria; it now applies to failures only.

After that, only E11, E16, E30 and the three relabelled sketches differ from the reviewed text.
The other 24 are byte-identical. Following the reviewer's caution, I don't claim 30/30: the
edited six have not been reviewed.

| Evaluation | Now |
|---|---|
| E11 | Template: `Your answer is about something else ("Monsoons happen because land heats up faster than the ocean in summer"). Reread the question and answer what it asks: ...`. The model failed the new check twice |
| E16 | "You don't mention specific alliances like the Triple Alliance or events like the July Crisis. Add an example of an alliance and explain how it led to the war." It no longer says the learner gave no explanation, though unlike the reviewer's version it doesn't credit the general account |
| E30 | `You wrote "directly increases the country's export volumes and overall global competitiveness", which explains how a depreciation ...`. Specific now, but it still repeats a lenient verdict on a nonsense answer, which the reviewer classed as a grading issue |
