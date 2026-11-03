# Verifier test set: external review 1 and decision

Review date: 2026-11-01, applied 2026-11-03. The review covered all 95 items. It kept 84 labels,
relabelled 2 and marked 9 to revise or drop. It was a classification review, made blind to the
verifier's results.

## Cross-check

I agree with every decision. The 9 flagged items match weak spots the hand check had already
seen or should have seen:

- **2 "valid" items were not secure novelty tests** (valid_mixed, valid_class). The judge had
  already scored both 1.00 on a listed path, which is the reviewer's point in other words.
- **3 mandatory criteria stated something false or backwards.** They were the synaptic-baseline
  monoamine claim, "reduced costs undermine revenue" and "fortification prevents supplementation".
  A path that requires a false claim can't be a clean example of anything.
- **2 nonsense items used metaphor or real research, not invented physics** (market
  "temperature", canopy thermography). 2 more were relabelled invalid_reasoning, because
  resonance and phonetic analysis are real and only the inference was at fault.
- **2 labels depended on the learner answer**, which the verifier never sees (Q14 no_choice, Q15
  invalid_reasoning). A label must rest on what the verifier is shown.

## What was applied

| Decision | Items | Where |
|---|---|---|
| Dropped | valid_mixed, valid_class, two nonsense, Q14 no_choice, Q15 invalid_reasoning | `review.json` |
| Revised | monoamine path (now `b850a615f22e-valid_monoamine`), two restatement criteria | `curated.yaml` |
| Relabelled to invalid_reasoning | Q13 and Q14 nonsense | `review.json` |
| Stale explanations replaced | 7 of the 8 listed (the 8th item was revised instead) | `review.json` `note` |
| Trigger answers replaced | all 8 holed answers that supplied the step their path omits | `review.json` `answer` |

Of these, only the revised paths change what the verifier sees. Replaced answers change only the
trigger test. Relabels and notes change no model call.

## Conventions adopted

1. **The verifier's context.** It already gets the question and every listed path with its
   criteria. The old sheet said "only the path and the justification reach the verifier", which
   was wrong, and is now corrected.
2. **Class precedence**, from the review: misconception, nonsense, invalid_reasoning, holed, then
   restatement versus valid_unlisted. When two defects are equally plausible, the item is
   rewritten or dropped.
3. **Misconception** now means a plausible domain misunderstanding stated confidently, rather than
   a belief of documented prevalence. This settles the taxonomy concern without sourcing how
   common each claim is.
4. **Nonsense** needs a demonstrably false literal mechanism. A fancy name or a metaphor is not
   enough.
5. **No IDs reach the model.** This was already true: `verify()` sends question, paths, the
   proposed path and the justification only.

## Not applied

- **Factual cleanups in learner answers of non-holed items** (the WWI "automatic domino", the
  Iowa farm, the FAO figures). These answers are never a reference, and they only test whether
  amendment fires, which a wrong detail in a restatement answer doesn't change. Recorded here so
  nobody reuses them as model answers.
- **Rewrites in place of drops.** The review allowed either. Each dropped class still has 11-27
  items, and a rewrite would need its own review.
