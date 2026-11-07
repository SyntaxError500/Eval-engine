# Phase 9: hardening and documentation

Date: 2026-11-07. **Status: both exit gates passed.**

| Gate item | Result |
|---|---|
| Fresh clone + `.env` runs the demo from the README alone | **Passed** (below) |
| Every validation number regenerates from cached responses with one command | **Passed:** `eval-engine reproduce`, 9/9 reports identical |

## What was added

- **`snapshot/`** (2.7 MB, committed). `data/` is gitignored, so a fresh clone had no questions
  for the app and no cache to regenerate from. The snapshot holds rubrics, questions, experiment
  evaluations, the response cache, call-log metadata (no prompts, no keys) and the two CC BY 4.0
  corpora. It is loaded with `eval-engine snapshot import`. Exports are deterministic: fixed row
  order and gzip timestamp, so unchanged data makes no git diff.
- **`eval-engine reproduce`.** Regenerates every validation report with an offline client: a
  cache miss raises `CacheMiss`, which is deliberately not a `ProviderError`, so no degradation
  path can absorb it and change a number. It runs on a copy of the database and of each
  experiment folder, then compares each report with the committed one.
- **`eval-engine amendment-frequency`**: `AMENDMENT_FREQUENCY.md`.
- **`requirements.lock`**: the exact versions used (Python 3.13.4). Model IDs per role, with call
  counts, are in `docs/FINAL_REPORT.md`.
- **Documents:** `docs/DECISIONS.md` (D1–D6 and role changes, with evidence),
  `docs/FINAL_REPORT.md`, and a README rewritten around the fresh-clone path.

## Fresh-clone test

A scratch folder held exactly what git would clone (tracked plus new non-ignored files; no
`data/`, no `.env`). The README's steps were followed as written, with `.env` copied from
`.env.example`, so no API keys:

- install from `requirements.lock`, then `pip install -e . --no-deps`;
- `snapshot import`;
- pytest: 320 passed;
- `reproduce`: 9/9 identical;
- Streamlit AppTest: 10 topics, a reviewed question shown;
- `streamlit run`: health check 200.

**The first run failed, usefully.** The amendment-frequency report differed: the snapshot carried
the app's evaluations but not the submissions table that marks them as app activity, so a fresh
clone counted 3 more answers. The snapshot now leaves app evaluations out, and the rerun passed.

## Correction made in this phase

Reference answers are no longer shown to learners or given to the tutor. Phase 3 had tightened
D2 to "never shown" (binding), because review found errors in about a third of them, and the
Phase 8 app had missed this (`experiments/8_interface/FINDINGS.md`).

## Not done here

- Phase 8's usability gate still needs a first-time user.
- The open grading decisions are listed at the end of `docs/DECISIONS.md`.
