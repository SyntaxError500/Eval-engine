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

## Swapping a model

Edit the role in [config/roles.yaml](config/roles.yaml). Nothing else changes. Replace the
placeholder rate limits there with the numbers shown in each provider's console.

## Data

Everything lives in `data/eval_engine.db` (SQLite, gitignored): rubric versions, call log,
response cache and usage counters. Re-running an experiment reads from the cache unless the
call is made with `fresh=True`.
