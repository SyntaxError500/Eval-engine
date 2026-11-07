# Evaluation & Feedback Engine

Grades a human answer against a per-question, frozen rubric and returns prioritised feedback.
Design: [docs/Evaluation_Feedback_Engine_Design.pdf](docs/Evaluation_Feedback_Engine_Design.pdf).
Build plan: [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md).

## Setup (Windows, Git Bash)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
cp .env.example .env        # then fill in the API keys
```

API keys (all free tiers):

| Provider | Role(s) | Get a key |
|---|---|---|
| Gemini | judge (path identification + scoring) | https://aistudio.google.com/apikey |
| Groq | generator, reference answer, amendment proposer (gpt-oss-120b); verifier (Qwen) | https://console.groq.com/keys |
| Ollama (local) | feedback phrasing, perturbations | install from https://ollama.com, then `ollama pull qwen3:8b` |

Free tiers may use what you send for training. **Only send test or borrowed data.**

## Commands

The paths below use Git Bash syntax. In **cmd or PowerShell**, activate the venv first
(`.venv\Scripts\activate`) and drop the prefix: `eval-engine smoke`, `pytest`, `ruff`, `mypy`.

```bash
.venv/Scripts/eval-engine smoke     # one live call per provider; Phase 0 gate
.venv/Scripts/eval-engine usage     # requests/tokens sent per provider/model/day
.venv/Scripts/python -m pytest      # unit tests; never call real models
.venv/Scripts/ruff check src tests && .venv/Scripts/mypy
```

Each phase's experiments have their own commands: `eval-engine pilot --help` (Phase 2),
`eval-engine gen --help` (Phase 3), `eval-engine golden` (Phase 4, rerun after any pipeline change),
`eval-engine verifier --help` (Phase 5) and `eval-engine feedback-review` (Phase 6).
`eval-engine evaluate` shows the learner's feedback (local Ollama, about 11 s) unless
`--no-feedback` is given. All of them resume from the cache.

## The app (Phase 8)

```bash
.venv/Scripts/python -m pip install -e ".[app]"
.venv/Scripts/streamlit run app/streamlit_app.py
```

Learners pick a topic and get a reviewed question, or describe any topic and get a new question
generated on the spot (Groq generator plus the Phase 3 code checks and fact check, about 10-20 s).
A generated question is always marked as unreviewed. Either way they see feedback first and then
one band per dimension. After the feedback they can discuss the answer with a tutor (gpt-oss-120b
on Groq; local qwen3:8b answers when Groq is rate-limited or down). It sees how each band was
reached but can't change it; code rejects replies that repeat earlier ones. A learner who thinks a decision is
wrong can ask for one re-check, done by the judge's model: a decision is reversed only with a
quote from the answer that isn't itself listed as wrong, and the original grade is kept beside
it. Discussions and re-checks are saved for the Admin tab. `eval-engine validate discussion`
replays fixed dispute scenarios live (`experiments/8_interface/discussion_check/`). "See one possible answer" opens only after the feedback. The Admin tab shows each
submission's full trace and the question's rubric versions. If the judge is unavailable, an
answer is queued ("evaluating…") and retried later; it is never graded by another model.

## Swapping a model

Edit the role in [config/roles.yaml](config/roles.yaml). Nothing else changes. Replace the
placeholder rate limits there with the numbers shown in each provider's console.

## Data

Everything lives in `data/eval_engine.db` (SQLite, gitignored): rubric versions, call log,
response cache and usage counters. Re-running an experiment reads from the cache unless the
call is made with `fresh=True`.
