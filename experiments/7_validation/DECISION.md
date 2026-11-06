# Phase 7 decision record

```
DECISION 2026-11-07: Judge frozen at score_answer v3 for Phase 7.
Perturbation gate: NOT MET (20/37, 54% [38-69%], strict rule fixed pre-run, single run).
Secondary, labelled: 26/37 (70%) if ties count. Rule not changed.
Reasoning rubric rewrite deferred to Phase 8.
No further judge prompt changes until the human-set results are reported.
```

Made on the senior review's recommendation (Option 1), before any human grade was seen.

**Updates:** the majority-of-3 rerun (step 3) updates the figures below the record, never the
decision. Its numbers are in `perturb/REPORT_maj3.md`.

## Frozen judge configuration

| Setting | Value |
|---|---|
| Role | `judge` in `config/roles.yaml` |
| Provider / model | gemini / `gemini-3.5-flash-lite` |
| Temperature | 0.0 |
| Max output tokens | 4096 |
| Structured output | Gemini `response_json_schema`, `ScoredAnswer` (`src/eval_engine/schemas/judge.py`) |
| Prompt | `prompts/score_answer.yaml` v3, file hash `7d5cd213b57cf1d9ba8c096fb2027373ad2b6bcad3900ad002cfb5e5ef449042` |
| Creative route | `prompts/score_creative.yaml` v1 (unchanged since Phase 4) |
| Code checks | evidence, contradiction and sentence-count checks (`src/eval_engine/evaluation/`), unchanged since Phase 4 |

Reproduce from the tagged commit (`phase7-judge-v3-frozen`) with this config. Cached replies live in
`data/eval_engine.db`, which is not in git.

## The quota restart

Every v3 judge call recorded (695 at the time of writing, 266 of them cache hits) has the prompt
hash and model above. The corpus run stopped at 234 of 302 answers on the old key's daily limit.
The rerun on the new key replayed those 234 from the cache and graded only the remaining 68. The
API key is not part of a request or its cache key, so the settings are identical. Nothing needed
rerunning.
