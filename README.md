# Evaluation & Feedback Engine

Grades a human's answer against a per-question, frozen rubric (never against an LLM's own
answer) and returns prioritised feedback. Free-tier models only.

- Design: [docs/Evaluation_Feedback_Engine_Design.pdf](docs/Evaluation_Feedback_Engine_Design.pdf)
- Build plan and gates: [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)
- Results: [docs/FINAL_REPORT.md](docs/FINAL_REPORT.md), validation detail in
  [docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md), decisions in
  [docs/DECISIONS.md](docs/DECISIONS.md)

## Setup from a fresh clone

Windows, Git Bash, Python 3.12 or later (results were produced on 3.13.4). In cmd or
PowerShell, activate the venv (`.venv\Scripts\activate`) and drop the `.venv/Scripts/` prefix.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.lock      # the exact versions used
.venv/Scripts/python -m pip install -e . --no-deps
cp .env.example .env                                           # then add the API keys
.venv/Scripts/eval-engine snapshot import                      # questions, rubrics, cache, corpora
```

`snapshot import` fills `data/` (gitignored) from [snapshot/](snapshot/): the 37 reviewed
questions the app serves, every rubric version, the evaluation traces, the cached model
responses and the two borrowed corpora. Run it once; it only adds missing rows.

API keys, all free tiers:

| Provider | Roles | Key |
|---|---|---|
| Gemini | judge, fact checker, re-check | https://aistudio.google.com/apikey |
| Groq | generator, reference answer, amendment proposer, tutor (gpt-oss-120b); verifier (Qwen) | https://console.groq.com/keys |
| Ollama (local) | feedback phrasing, tutor backup | install from https://ollama.com, then `ollama pull qwen3:8b` |

Free tiers may use what you send for training. **Send only test or borrowed data**, never real
learners' answers.

## Check that it works

```bash
.venv/Scripts/eval-engine smoke                 # one live call per provider
.venv/Scripts/python -m pytest                  # 300+ tests; never call a real model
.venv/Scripts/eval-engine reproduce             # every validation report, from the cache
```

`reproduce` regenerates each validation report from cached responses only (a cache miss is an
error, never a live call), on a temporary copy of the database, and checks each is identical to
the committed one. It needs no API key and takes a few minutes.

## The app

```bash
.venv/Scripts/streamlit run app/streamlit_app.py      # http://localhost:8501
```

- **Answer a question:** pick a topic for a reviewed question, or describe any topic for a
  new one, generated and checked on the spot and marked as unreviewed. Feedback comes first,
  then one band per dimension. No reference answer is shown (decision D2).
- **Discuss your answer:** a tutor that knows how each band was reached. It can't change the
  grade, and code rejects replies that repeat earlier ones.
- **Ask for a re-check:** once per answer, by the judge's model. A decision is reversed only
  with a quote from the answer that isn't itself listed as wrong. The original grade is kept.
- **Admin:** each submission's full trace, discussion, re-check and rubric versions.
- **When a model is down:** if the judge is unavailable, the answer waits ("evaluating…") and
  is never graded by another model. If the verifier is down, the original rubric is used. If
  the feedback model is down, template feedback is used. If Groq is down, the local model
  takes the tutor's place.

## Experiments, by phase

Each command resumes from the cache, so a rerun after a quota stop only pays for what's missing.
Results and findings are in `experiments/<phase>/`.

| Phase | What | Commands |
|---|---|---|
| 2 | Judge pilot on SciEntsBank and Beetle | `eval-engine pilot prepare`, `pilot run --role judge`, `pilot report` |
| 3 | Question and rubric generation | `eval-engine gen question --topic T --task-type explanatory`, `gen batch` |
| 4 | Golden set (rerun after any pipeline change; re-records the replay fixture) | `eval-engine golden` |
| 5 | Amendment verifier test set | `eval-engine verifier build`, `run --framing adversarial`, `calibrate`, `e2e`, `report` |
| 6 | Feedback review sheet | `eval-engine feedback-review` |
| 7 | Full validation | `eval-engine validate corpus`, `validate perturb baseline\|build\|run\|report`, `validate human` |
| 8 | Degradation and dispute checks (live) | `eval-engine validate degrade`, `validate discussion` |
| 9 | Amendment frequency | `eval-engine amendment-frequency` |

Grade a single answer from the command line:
`eval-engine evaluate --question QUESTION_ID --answer "..."` (or `--answer-file F`; add
`--no-feedback` to skip the local model). `eval-engine usage` shows requests sent per
provider and day.

## Swapping a model

Edit the role in [config/roles.yaml](config/roles.yaml); nothing else changes. Set the rate
limits there to the numbers in the provider's console. Responses are cached per request, model
included, so a swapped role starts with an empty cache. Change the judge only with a new
validation run (Phase 7).

## Data

Everything lives in `data/eval_engine.db` (SQLite, gitignored): rubric versions, questions,
evaluation traces, the call log, the response cache, usage counters and app submissions. After
new results, run `eval-engine snapshot export` to refresh `snapshot/`. Unchanged data exports
byte-identical, so it makes no git diff.

## Development

```bash
.venv/Scripts/python -m pip install -e ".[dev,app]"
.venv/Scripts/ruff check src app tests && .venv/Scripts/mypy src app
```
