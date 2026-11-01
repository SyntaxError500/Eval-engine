# Phase 3, review 2: handover notes

`review.md` holds 40 questions from generator prompt v4. This batch is the gate: it passes
if at least 85% of the questions pass every applicable checklist item. My pre-filter below
is only a filter, not a verdict (review 1 showed my estimates were far too lenient).

## What changed since review 1

| Review 1 cause | Change |
|---|---|
| A. Criteria demanded things the question never asked for | Every criterion shows `← asked by: "…"`, the question's own words that require it, checked in code. Creative craft tests (a turn, show-don't-tell, a finite banned-phrase list) are marked `craft test (by design)`. Non-core now means "asked for, but secondary". |
| B. Particular arguments required | Reasons and arguments are "a first / a second distinct reason", so any valid one counts. |
| C. Open-ended creative rules | Cliché bans must list exact phrases, normally stated in the brief itself. "Exactly" is allowed only if the question says it. |
| D. Wrong facts in rubrics and paths | Every rubric passes a fact-check by a different model family (Gemini) before freezing. Its doubts, if any, are listed under the question. Explanatory questions may have one path when only one valid explanation exists. |
| E. Wrong reference answers | References are hidden from learners and from this sheet. They are never used in grading. |

Also new: judgement words are banned from question text, "for each" and "at least two"
bundling are rejected, and analytical paths require reasoning.

## Pre-filter actions on this batch

**Rejected and regenerated** (recorded in `rejected.json`):
- the climate question framed human vs natural causes as an open debate (false balance);
- the coastal erosion question offered plate tectonics as the driver of a recent change;
- the clotting question demanded steps beyond "initiates".

5 more were regenerated after the bundling check was broadened.

**Things I'd like the reviewer to look at:**
- #25 (exercise and mental health), path P1: the endorphin explanation is popular, but its evidence is weaker than the BDNF and psychosocial paths.
- #10 (bedtime routines): "factual" is a stretch for an everyday-life routine.
- #29 (Haitian Revolution): path P3, "the 1794 French decree forced abolition", is a contested causal framing.
- Creative briefs with "3–8 sentences" as a core constraint (#31, #38): allowed by design. Decide whether you'd fail them.

The checklist is unchanged from review 1 (8 items).
