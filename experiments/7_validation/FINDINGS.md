# Phase 7: full validation, interim findings

Dates: 2026-11-03 (corpus, judge v2), 2026-11-07 (perturbation, human set, judge v3). Judge:
gemini-3.5-flash-lite.

**Status: decided (`DECISION.md`). The judge is frozen at v3, and the perturbation gate is NOT MET
under either rule once scored by a majority of 3 calls.** The corpus gate passes, and the human set is ready for
graders. Under judge v3, the corpus passes on all 302 answers.

| Gate item | Target | Result |
|---|---|---|
| Borrowed-corpus leniency | absolute value at most 0.1 | **PASS.** v2: −0.020 [−0.065, +0.026]; v3: −0.035 [−0.081, +0.013], both on all 302 |
| Human-set leniency | absolute value at most 0.1 | **PASS: −0.010 [−0.096, +0.070]** (`human/REPORT.md`) |
| Perturbation attribution | at least 70% overall, reported per dimension | **NOT MET.** v3, majority of 3: 19/37 (51%) [36–67%]; 25/37 (68%) if ties count (labelled secondary). See `DECISION.md` |
| `docs/VALIDATION_REPORT.md` | — | Written |

## 1. Borrowed corpus through the full engine (`corpus/`)

These are the Phase 2 held-out SciEntsBank and Beetle answers, with the same rubrics, human labels
and label mapping as Phase 2, so the numbers compare directly.

| Run | n | Leniency [95% CI] | QWK | 2-way acc |
|---|---|---|---|---|
| Phase 2 judge (`path_and_score` v1) | 302 | −0.066 [−0.113, −0.018] | 0.577 | 78.1% |
| Engine, judge v2 | 302 | **−0.020 [−0.065, +0.026]** | 0.614 | 78.5% |
| **Engine, judge v3** | 302 | **−0.035 [−0.081, +0.013]** | 0.616 | 79.1% |

| By dataset | v2 leniency | v3 leniency | v2 QWK | v3 QWK |
|---|---|---|---|---|
| SciEntsBank | −0.086 | −0.102 | 0.754 | 0.729 |
| Beetle | +0.047 | +0.033 | 0.478 | 0.506 |

- **The engine is at least as good as the Phase 2 judge alone.** The v2 interval is inside ±0.1;
  Phase 2's reached past −0.1. The other intervals overlap and the judge flips 12% of labels
  between runs, so "better" isn't established.
- **v3 is slightly harsher than v2** (−0.035 against −0.020), with about the same QWK. On
  SciEntsBank it is −0.102, just past the line, where v2 was −0.086; on Beetle it is closer to
  zero. The differences are inside the intervals. (A first v3 run stopped at 234 answers on
  quota and finished on a new key.)
- **The code checks never fired.** These answers are one or two sentences and the judge quotes
  them exactly. Every rubric is a factual checklist, so amendment can't run here.

## 2. Synthetic perturbation (`perturb/`)

**Bases:** 30 answers that score full marks (10 factual, 10 analytical, 10 explanatory: reference
answers of reviewed questions, plus 2 golden).

**Edits:** each base was edited up to four times, once per dimension, each edit aimed at a
criterion the base met. Local qwen3:8b was tried first and replaced by gpt-oss-120b: it returned
61 of 108 edits unchanged, often while saying it had changed something. gpt-oss is not the judge's
model family.

**Checks:** every edit was checked in code and read by hand. Of the 108, 41 were dropped, each with
its reason in `review.json`, leaving 67 (37 content edits and 30 expression edits). Reasons for
dropping:

- the targeted content or link was still stated elsewhere;
- an "error" that isn't clearly false;
- an invented statistic swapped for another.

The external review of the human set added wording fixes (`review.json` `replace`): a
wrong-physics sentence inherited from a base answer, "imports" for "goods", orphan openers left by
deletions, and a second unplanted error.

**Rule, fixed in code before any run:** an edit is *attributed* when its target dimension has the
unique largest score drop. A tie with another dimension counts as a miss.

| Injected | n | v2 attributed [95% CI] | v3 attributed [95% CI] | v3 ties |
|---|---|---|---|---|
| completeness (content removed everywhere) | 11 | 6 [28–79%] | 6 [28–79%] | 3 |
| correctness (one clearly false fact) | 19 | 9 [27–68%] | 10 [32–73%] | 3 |
| reasoning (causal link or reason broken) | 7 | 3 [16–75%] | 4 [25–84%] | 0 |
| **overall** | 37 | **18 (49%) [33–64%]** | **20 (54%) [38–69%]** | 6 |
| overall if ties counted | 37 | 24 (65%) | 26 (70%) | |

| v3, detected (the target dimension drops at all) | |
|---|---|
| completeness | 9/11 |
| correctness | 14/19 |
| reasoning | 4/7 |

**Expression only:** no content score moved on 30/30, under both v2 and v3. That is expected by
construction, not evidence that the judge handles style. No non-creative rubric has an expression
criterion, because Phase 3 makes dimensions weighted 0.2 or less optional. So this edit can only
be checked for not moving anything, and it is left out of attribution.

### What the test got wrong first, twice

1. **Completeness.** Deleting one sentence left the content stated elsewhere: good answers repeat
   themselves, so 17 of 24 edits owed no drop. Fix: remove the content everywhere.
2. **Reasoning.** 17 of 18 edits broke the link in one sentence while another still stated it. A
   judge crediting them was right. The external review caught it, not my hand check. Regenerated,
   7 of 20 were clean.

Under the flawed versions the engine looked much worse (1/18 on reasoning). The cleaned set is
smaller, and its intervals are wide.

### Judge v3 (`score_answer` v3)

v3 adds three rules:

- a criterion asking how or why X leads to Y is met only if the answer itself says X causes Y; a
  coincidence or timing link doesn't count;
- a reason must bear on the position it supports;
- every factual claim is checked, not only those the criteria ask about.

**Effect:**

| Measure | v2 | v3 |
|---|---|---|
| Attribution | 18/37 | 20/37 |
| False facts detected | 12/19 | 14/19 |
| Reasoning breaks | 3/7 | 4/7 |
| Golden | 40/40 | 39/40 (cell-partial now gets full marks for "after that the cell gets ready to divide") |

The bases still score full marks under v3, except one correctness criterion on one answer. All of
these changes are inside the noise for samples this size.

### What still fails, from the verdicts

- **Ties (6).** A planted error often fails a correctness criterion *and* breaks a criterion in
  another dimension that rests on the same claim. Both drop by the same amount.
- **Missed false facts (5).** These include the Prussian-led German Confederation and the Madame
  Bovary date. The judge still lists errors only some of the time.
- **Reasoning criteria that only test presence** ("Provides a first distinct reason ..."). No judge
  prompt can fail a reason that is present but irrelevant if the criterion only asks for presence.
  This is a rubric issue from Phase 3.

### Majority of 3 judge calls (`perturb/REPORT_maj3.md`)

Every base and edit is scored as the majority of 3 calls, the same way the human set will be.
The single-run figures above are kept for the record.

| Injected | n | v2 strict [95% CI] | v3 strict [95% CI] | v3 ties counted | v3 detected |
|---|---|---|---|---|---|
| completeness | 11 | 7 (64%) [35–85%] | 6 (55%) [28–79%] | 9 (82%) | 9 |
| correctness | 19 | 8 (42%) [23–64%] | 9 (47%) [27–68%] | 12 (63%) | 13 |
| reasoning | 7 | 3 (43%) [16–75%] | 4 (57%) [25–84%] | 4 (57%) | 4 |
| **overall** | 37 | **18 (49%)** [33–64%] | **19 (51%)** [36–67%] | 25 (68%) | 26 |

v3's single-run tie-inclusive 70% does not hold under majority voting. All counts above, and the
bookkeeping (120 possible, 12 skipped, 108 generated, 8 failing checks, 33 dropped on review, 67
kept), are generated by `validation/perturb_votes.py` from the run files.

## 3. Options at this decision point (decided: option 1)

1. **Keep v3 and record the gate as not met.** Report the per-dimension rates and intervals, and
   carry the limits into the validation report. This doesn't change the rule after seeing the
   results.
2. **Rewrite presence-only reasoning criteria** to require the link ("Explains how the reason
   supports the position"). This is a Phase 3 rubric change, needing a new external review of
   those questions and a rerun of everything.
3. **Re-scope the gate:** drop expression (already done), report reasoning separately, decide how
   ties count, and state each change as a change. Ties counted would put v3 at exactly 70%, but
   that rule was not fixed in advance.

## 4. Human-graded set (`human/`), ready for graders

The set has 50 answers on 13 single-path factual and explanatory questions:

- golden answers: good, paraphrased, partial, wrong and off-topic;
- perturbations of every kind, after the review's fixes.

For each answer, two graders mark every requirement Y/N, whether anything is false, and an overall
label. They grade blind to the engine. The sheet now has the review's rules for false statements,
for requirements that refer back to an earlier item, for paraphrased names and for multi-part
requirements. `key.json` must not go to graders.

When the grades return:

1. **Inter-rater agreement first.**
2. **Then engine leniency and correlation.** They are bootstrapped by question, not by answer: the
   answers are uneven across questions, 12 of them on the hot-air balloon.
3. **Then band calibration.** Given the 12% flip rate, the engine side is scored as the majority of
   3 judge runs.

## 5. Human-set results (`human/REPORT.md`)

These come from the pre-registered script, run unchanged.

- **Agreement:** κ is 1.00 on requirements and on the overall label, and 0.95 on the
  false-statement flag. The two graders' files differ in 1 of 332 marks. They graded independently
  (confirmed), but agreement this high is unusual, so it is reported as a limit.
- **Engine, majority of 3 under v3:**
  - leniency −0.010 [−0.096, +0.070], **gate PASS**;
  - Spearman 0.843;
  - QWK 0.821 against each grader.
- **Bands:** 109/121 dimension scores in the same band (90%); the cut-offs are kept.
- **Disagreements:** the engine gave full marks to 5 answers both graders called partially correct.
  Three are planted false facts it missed (the Prussian-led Confederation, three-quarters of the
  rainfall, *Madame Bovary* 1860). The partial cell-cycle answer (A18) is credited with naming a
  third phase that both graders say it doesn't name, though its overall label agrees.
