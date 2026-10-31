# Phase 3, review 1: outcome and decision

**Gate: NOT PASSED.**
- External strict review: **7 of 39 pass (18%).**
- With my adjustments (below): **13 of 39 (33%).**
- Required: 85%.

The batch reviewed was generator prompt v3, ids in `batch.json` at commit db80cdc. My own pre-review (`PRE_REVIEW.md`) had estimated 87%. It checked structure and a few facts. The external review checked every criterion against its question and verified facts against sources. From now on, quality gates go to a strict review; my pre-review is only a filter.

## Cross-check of the review

I spot-checked its factual findings and all held:
- Ground-level ozone is a secondary pollutant.
- GIP comes from K cells, not L cells.
- Wien's peak at ~1,800 K is ≈1.61 µm (infrared).
- The Gettysburg charge was the 1st Minnesota, on July 2.
- Newspeak keeps "free" in non-political senses.
- *Emma* was published in December 1815.
- Watt's 1769 date is a patent.
- 5% inflation on $1,000 is a $47.62 real loss, not $50.
- NYC rent stabilization dates from 1969.
- A dollar peg does not protect against inflation.

**Two adjustments (they don't change the verdict):**

1. **Creative craft checks** (show-don't-tell, a turn, cliché avoidance) are part of creative grading by design (design doc §9), so item 4 isn't failed for having them. Open-ended "avoids common clichés such as…" still fails item 3: it isn't binary.
2. **Errors only in reference answers** (#3, #12, #16) don't affect grading, because the judge never sees references. They would mislead learners if shown. See cause E.

## Root causes and fixes (generator prompt v4)

| Cause | Questions | Fix |
|---|---|---|
| A. Non-core criteria add requirements the question never asked for (numeric example, named theory, citation, rebuttal, "real-world"). They still cost points on a fully correct answer. | 13, 15, 21, 22, 23, 25, 27, 28 | Every criterion carries `requires`: the exact words of the question that ask for it. Code checks the quote is really in the question. Creative craft criteria are exempt by design. Non-core now means "asked for, but secondary". |
| B. Particular arguments required instead of any valid one | 13, 14, 18 | Prompt rule, plus the `requires` quote. |
| C. Open-ended creative rules ("clichés such as", "exactly one", literal-name checks) | 30–37, 39 | Lint: a cliché check must give a finite list; "exactly" only if the question says it. |
| D. Wrong facts inside rubrics and paths, and paths that miss part of what the question asks | 6, 11, 20, 24, 26, 29 | Fact-check pass by a different model family (Gemini) before freezing. Its errors go back to the generator as check problems. |
| E. Reference answers wrong in about a third of questions | many | References are never shown to learners (D2 tightened). They aren't used in grading. Removed from the review sheet. |
