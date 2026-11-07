# Decisions

Every open decision from the plan (§3), and every change of model for a role, with the evidence
behind it. Figures can be regenerated with `eval-engine reproduce` unless marked as a human
review.

## Open decisions D1–D6

| ID | Question | Outcome | Evidence |
|---|---|---|---|
| D1 | Path identification on every answer, or on demand? | **Every non-creative answer, merged into the scoring call.** Confirmed | Phase 4 golden set: 40 answers, 40 judge calls; every expected path identified, including both second-path answers (P2 at 1.00 and 0.95). `experiments/4_eval/FINDINGS.md` |
| D2 | Show the reference answer to the learner? | **Never.** Tightened in Phase 3 from "hidden, reveal after feedback". The tutor doesn't see it either | Phase 3 review 1 found errors in about a third of reference answers, which play no part in grading. `experiments/3_generation/FINDINGS.md`. The Phase 8 app first showed it; corrected in Phase 9 (`experiments/8_interface/FINDINGS.md`) |
| D3 | Where does originality count for creative tasks? | **Feedback only, never scored.** Revised in Phase 4 | Briefs don't ask for originality (Phase 3), so scoring it would test something not asked. Obvious-answer overlap is in the trace and the feedback; cliché bans a brief asks for are ordinary criteria. `experiments/4_eval/FINDINGS.md` |
| D4 | Single judge or ensemble? | **Single judge.** Ensemble not adopted | Leniency was not borderline on either dataset in Phase 7: corpus -0.035, human set -0.010. `docs/VALIDATION_REPORT.md` |
| D5 | Which model phrases feedback? | **Local qwen3:8b.** Confirmed | Phase 6 external review: 27/30 pass, 3 failures (under the 20% switch rule), one of them a code template. 10.9 s per evaluation on an RTX 3050. `experiments/6_feedback/FINDINGS.md` (human review) |
| D6 | How to keep grades stable, given 12% label flips at temperature 0? | **A resubmission is answered from the cache; one judge vote by default.** Majority of 3 kept for validation runs only | Phase 2 stability run: 12% flips. Phase 4: re-voting the 15 borderline golden items cost 30 extra calls and changed 0 scores (`experiments/4_eval/d6_votes.md`). Phase 7 reports the perturbation and human-set figures on a majority of 3; the corpus run uses the production setting |

## Roles and models

The final configuration is `config/roles.yaml`. Every call made is in the call log; `snapshot/`
carries its metadata.

| Role | Final model | Changes and why |
|---|---|---|
| judge | gemini-3.5-flash-lite (Gemini), `score_answer` v3, frozen (tag `phase7-judge-v3-frozen`) | Chosen in Phase 2 over Qwen 3.8 on Groq (leniency -0.229) and local qwen3:8b (lower QWK), `experiments/2_judge_pilot/REPORT.md`. Full Gemini Flash allows 20 requests a day and the newest models returned 503/504 under load, so the model is pinned. Prompt v2 (Phase 5) changed path confidence to mean intent: ordinary golden answers triggering amendment fell from 10/30 to 1/30. v3 (Phase 7) requires links to be asserted and checks every claim; frozen before human grades were seen (`experiments/7_validation/DECISION.md`) |
| generator, reference_answer, amendment_proposer | gpt-oss-120b (Groq) | No change. A different family from the judge and the verifier, so neither grades its own model's writing |
| fact_checker | gemini-3.5-flash-lite | Added after Phase 3 review 1, which found wrong facts inside rubrics and paths in 6 of 40 questions (cause D, `experiments/3_generation/REVIEW_1_DECISION.md`). A different family from the generator |
| verifier | qwen/qwen3.8-27b (Groq), plain JSON mode | Groq's constrained decoding broke on this model (12 of 22 failed); plain JSON mode fixed 6/6. Phase 5 gate: 0/23 false accepts on nonsense and misconceptions |
| feedback_phraser | qwen3:8b (local) | D5 |
| perturber (Phase 7 only) | gpt-oss-120b (Groq) | Was local qwen3:8b, which returned 61 of 108 edits unchanged, often while saying it had changed them |
| tutor | gpt-oss-120b (Groq), with qwen3:8b as `tutor_fallback` | The user's choice (Phase 8). On the Java objections the local model fell back to the fixed reply 4 times in 7 and said return types are part of the method signature; gpt-oss engaged every objection with no factual error seen. `experiments/8_interface/discussion_check/` |
| rechecker | gemini-3.5-flash-lite | A re-check is grading, so it uses the judge's model, never the local one. Live check: invalid appeals held 6/6, valid ones granted 0/2 |
| (dropped) Mistral | - | Its API is not free; the adapter is kept for a paid upgrade |

## Gate rules and how they were applied

- **Phase 7 perturbation gate: NOT MET**, recorded as such. The tie rule was fixed in code before
  any run and was not changed afterwards (`experiments/7_validation/DECISION.md`).
- **The human-set analysis was pre-registered,** committed before any grade arrived
  (`src/eval_engine/validation/human_analysis.py`).
- **Band cut-offs kept** at 0.40 / 0.65 / 0.85: 90% band agreement with the graders.

## Open: for whoever continues

| Decision | Evidence so far |
|---|---|
| Count one mistake once (a listed error that is also why a correctness criterion failed costs the dimension twice) | Both human graders called 7 of the 10 single-error answers "partially correct"; the engine's label gave all 10 a 0. But overall leniency (-0.010) is two errors cancelling: fixing this alone would make the engine lenient. `docs/VALIDATION_REPORT.md` backlog |
| A generation check for compound criteria | 30 of 45 non-creative bank paths have one correctness requirement, so one failed check decides the band |
| Reasoning criteria that test only presence | Perturbation: an irrelevant reason meets "provides a reason" whatever the judge prompt says |
