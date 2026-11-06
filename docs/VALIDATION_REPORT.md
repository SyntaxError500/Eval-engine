# Validation report

Evaluation & Feedback Engine, Phase 7, 2026-11-07.

| Item | Setting |
|---|---|
| Judge | `gemini-3.5-flash-lite`, `score_answer` v3, frozen (`experiments/7_validation/DECISION.md`, tag `phase7-judge-v3-frozen`) |
| Engine | merged path identification and scoring, code checks (evidence, contradiction, sentence counts) and aggregation; amendment off for validation |
| Scoring | Phase 2 label mapping (`labels.py`): correct 1.0, partial 0.5, otherwise 0.0 |

Every figure below is generated from the run files by committed scripts:

- corpus: `validation/corpus.py`;
- perturbation: `validation/perturb_votes.py`;
- human set: `validation/human_analysis.py`, committed before any grade arrived.

## 1. Gates

| Gate | Target | Result |
|---|---|---|
| Borrowed corpus (SciEntsBank + Beetle, 302 held-out answers) | absolute leniency at most 0.1 | **PASS: −0.035 [−0.081, +0.013]** |
| Human-graded set (50 answers, 2 graders) | absolute leniency at most 0.1 | **PASS: −0.010 [−0.096, +0.070]** |
| Synthetic perturbation (37 content edits) | attribution at least 70% overall | **NOT MET: 19/37 (51%) [36–67%].** Labelled secondary figure if ties count: 25/37 (68%) |

Correlation is reported with leniency throughout, because each misses what the other sees:

| Data | Leniency | QWK | Spearman | 2-way accuracy |
|---|---|---|---|---|
| Borrowed corpus | −0.035 | 0.616 | 0.621 | 79.1% |
| Human set | −0.010 | 0.821 (vs each grader) | 0.843 | — |

For comparison, the Phase 2 judge alone had corpus leniency −0.066 [−0.113, −0.018] and QWK 0.577.
The engine is at least as good; with overlapping intervals and a 12% run-to-run label flip rate,
"better" isn't established.

## 2. What the engine does well

- **It is not systematically harsh or lenient.** Leniency is inside ±0.1 on both a borrowed corpus
  graded by others and a set graded for this project, and each interval is inside the target.
- **It orders answers like humans do.** On the human set Spearman is 0.84 and QWK 0.82, with a
  cluster bootstrap over 13 questions, so the intervals aren't flattered by the 12 balloon
  answers.
- **Bands are well placed.** 109 of 121 dimension scores (90%) fall in the same band as the
  graders' adjudicated requirement marks, with a mean gap of 0.057. **The four bands and their
  cut-offs are kept (plan task 5).**
- **Completeness:** once content is truly gone, it is detected in 9 of 11 edits.
- **Expression rewrites move no content score** (30/30). This is by construction, not skill: no
  non-creative rubric has an expression criterion.

## 3. Known limits

- **False facts outside the criteria are missed.** In the perturbation set, 6 of 19 planted false
  facts produced no correctness drop under v3, majority of 3. On the human set, three planted errors
  got full marks from the engine where both graders said partially correct: the Prussian-led German
  Confederation, three-quarters of the rainfall, and *Madame Bovary* in 1860. The judge's errors
  list catches false statements unreliably.
- **One error rightly hits two dimensions.** A false fact often fails a correctness criterion and a
  criterion in another dimension that rests on it. Under the strict attribution rule these 6 ties
  count as misses.
- **Reasoning criteria often test only presence** ("Provides a first distinct reason ..."). No
  judge prompt can fail a reason that is present but irrelevant. Only 7 clean reasoning edits could
  be made, so that dimension's interval is wide (4/7, 25–84%).
- **SciEntsBank leniency is −0.102 under v3,** just past the line for that dataset alone (v2:
  −0.086). Beetle is +0.033. This is one dataset in one run.
- **The judge flips about 12% of labels between identical runs** (Phase 2). Validation uses a
  majority of 3 calls; production by default uses one (decision D6), with a cached answer for an
  identical resubmission.
- **v3 is in-sample on the perturbation set.** It was written after reading those verdicts. The
  human set is its first held-out test, and it passed.
- **The lenient "names a phase" verdict.** On the partial cell-cycle answer (A18), the engine
  credits "after that the cell gets ready to divide" as naming a third phase; both graders say it
  doesn't. The overall label agrees (partially correct).
- **Creative evaluation is the weakest part** (design doc §9). Its rubrics are craft tests the brief
  states; originality is reported as feedback and never scored (decision D3). None of the gates
  above covers creative answers. The golden set has 10, of which 10 were within range; no borrowed
  or human-graded creative data exists.
- **Inter-rater agreement is unusually high.** κ is 1.00 on requirements and on the overall label,
  and 0.95 on the false-statement flag: the two graders' files differ in 1 of 332 marks. The graders
  graded independently (confirmed with the project owner). This is reported as measured, but it is
  far above what independent grading usually gives, so the human-set results effectively rest on one
  shared judgement. A further independent grader would strengthen them.

## 4. How the tests were built, and what went wrong first

The perturbation test had to be rebuilt twice. Each flaw made the engine look worse than it was:

1. **Completeness.** Deleting one sentence often left the same content stated elsewhere: good
   answers repeat themselves. 17 of 24 edits owed no drop. The edits now remove the content
   everywhere.
2. **Reasoning.** 17 of 18 edits broke the link in one sentence while another still stated it, so a
   judge crediting them was right. **The external review caught this, not the hand check.**
   Regenerated, 7 of 20 were clean.

Every edit was checked in code and read by hand. 41 of 108 were dropped, each with its reason in
`perturb/review.json`. Wording fixes from the external review are recorded there too: a
wrong-physics sentence inherited from a reference answer, "imports" for "goods", orphan openers,
and a second unplanted error. The local model first used to write edits returned 61 of 108
unchanged and was replaced by gpt-oss-120b, which is not the judge's model family.

External review is a strength of the process: it found the flaw that would have most misled the
gate decision.

## 5. Decisions

- **Judge frozen at v3** before the human grades were seen. The perturbation gate is recorded as
  not met; the tie rule fixed before any run was not changed (`DECISION.md`).
- **Band cut-offs kept** at 0.40 / 0.65 / 0.85 (90% band agreement with the graders).
- **D4 (ensemble) not adopted.** Leniency is not borderline on either dataset.

## 6. Phase 8 backlog

| Item | Why |
|---|---|
| Rewrite presence-only reasoning criteria to require the link | No judge prompt can fail an irrelevant reason when the criterion only asks for presence |
| A dedicated false-fact pass (a separate call or a code check) | Planted false facts are missed: 6/19 in perturbation, 3 on the human set |
| Revisit the tie rule, with the change declared before the next run | Ties often reflect correct behaviour |
| Grow clean reasoning perturbations to about 20 or more | n = 7 can't support a per-dimension gate |
| An expression criterion where style matters | It can't be measured today by construction |
| Watch SciEntsBank harshness | −0.102 is one dataset in one run |
| A third, independent grader for the human set | The two graders' near-identical marks limit what agreement can show |
