# Phase 3: findings and decisions

**Status: closed, 2026-11-01. Gate passed: 37 of 40 (92.5%), required 34 (85%).**

The gate was a strict external review of 40 generated questions (4 task types × 10 topics), against an 8-item checklist. A question passes only if it passes every applicable item.

## How we got there

| Round | Generator | Result | Main finding |
|---|---|---|---|
| Review 1 | prompt v3 | 7/39 (18%) | Criteria demanded things the question never asked for; particular arguments required; open-ended creative rules; wrong facts inside paths |
| Review 2 | prompt v4 + traceability + fact-check | 28/40 (70%) | Unstated creative craft tests (phrase bans, turns); criteria narrowing the question's meaning; a false count ("the two conditions"); blurred historical events |
| Review 3 | prompt v5, 9 replacements | 9/9 pass, **37/40** | Clean; minor optional notes only |

My own pre-reviews were useful filters but poor predictors. After review 1 (where I had estimated 87%), the strict review alone decided the gate.

## What the generation stage now enforces

| Rule | Enforced by |
|---|---|
| Every criterion quotes the question words that ask for it (`requires`) | Code check (normalised substring, or all content words present) |
| Creative craft tests (turn, show-don't-tell, phrase bans) only if the brief states them | Code check (no exemption) + prompt + fact-check |
| Criteria don't narrow or change the question's meaning | Prompt + fact-check |
| Any valid reason or argument counts: "a first / a second distinct reason" | Prompt + bundling check |
| One criterion per item; no "for each" / "at least two" bundles | Code check |
| No judgement words in criteria or in the question | Code check |
| Analytical/explanatory questions ask for one answer; paths are alternatives | Code check on question text + prompt |
| Explanatory may have one path when only one valid explanation exists | Code check relaxed (the candle-flame lesson) |
| Facts, premises, settled science, real causes, distinct historical events | Fact-check by a different model family (Gemini) |
| Required dimensions only where weighted above 0.2 | Code check (removes pressure to invent requirements) |

## Decisions

1. **Reference answers are never shown to learners** (D2 tightened). They aren't used in grading, and review 1 found errors in about a third of them.
2. **Reviewer decisions are recorded and binding.** `accepted.json` keeps reviewed passes across prompt versions; `rejected.json` lists failures with reasons.
3. **Generator drafts bypass the response cache.** Otherwise a failed slot replays the same failing draft on every rerun.

## Batch state

- 37 accepted questions.
- 2 newly generated, not yet reviewed: slot 4 factual/ethics and slot 36 creative/geography.
- 1 empty: slot 29 explanatory/history.

The gate stands on the 37. The 2 new ones can join the pool after review.

## Costs and constraints

- **Generation cost.** A v5 question costs about 8–12K Groq tokens (up to 3 generator attempts plus a fact-check), so about 15–20 questions per 200K daily budget. Production generation is one question per user request, so this is fine; batch regeneration is slow.
- **Groq's count runs ahead of ours.** Groq's daily token count consistently ran 20–40% ahead of our own, so its 429 stays authoritative.
