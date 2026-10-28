# Evaluation & Feedback Engine — Implementation Plan

Companion to [`Evaluation_Feedback_Engine_Design.pdf`](Evaluation_Feedback_Engine_Design.pdf). The design doc says *what* and *why*; this document says *how*, *in what order*, and *how we know each phase is done*.

---

## 0. Guiding principles

1. **De-risk the judge first.** Every score passes through the judge. We validate it on a human-graded corpus (Phase 2) before building anything on top of it.
2. **Every phase ends with an exit gate.** A phase is not done until its gate passes. A failed gate is a decision point, not a reason to push on.
3. **No live model calls in tests.** CI runs against a fake provider and cached responses. Live calls happen only in explicit experiment scripts.
4. **Models are configuration, not code.** A role (generator, judge, ...) maps to a provider and model in `config/roles.yaml`. Free tiers change without notice, so swapping a model must take one line.
5. **Everything that produces a score is logged and reproducible.** That covers the rubric hash, prompt version, model ID, and raw response.
6. **Only test or borrowed data goes through free tiers.** The Gemini free tier may train on inputs and allow human review.

---

## 1. Locked decisions

| Area | Decision |
|---|---|
| Comparison target | Per-question frozen rubric, **not** the LLM answer |
| Task types | factual, analytical, explanatory, creative (declared by the generator) |
| Dimensions | correctness, completeness, reasoning, expression (constant; weights vary by task type) |
| Scoring | One call per answer with the whole rubric; per-criterion binary verdicts + justification |
| Aggregation | In code, never in the model |
| User-facing output | Feedback first (2–3 prioritised points + what worked), then coarse per-dimension bands, no single aggregate |

### Model roles (free tier only)

| Role | Provider / model | Family | Notes |
|---|---|---|---|
| Generator (question, task type, rubric, obvious answers) | gpt-oss-120b on Groq | OpenAI open-weight | One call per question; cached in the rubric store, so Groq's small daily token cap is enough |
| Reference answer | gpt-oss-120b on Groq | OpenAI open-weight | Written after the rubric is frozen; not used in scoring |
| Amendment proposer | gpt-oss-120b on Groq | OpenAI open-weight | Sees question + answer only |
| Path identification + scoring judge | **Gemini Flash** | Google | Runs on every answer, so it gets the largest free daily budget |
| Verifier | Qwen on Groq | Qwen | Different family from proposer, judge and generator; runs only when an amendment fires |
| Feedback phrasing, perturbation generation, offline dev | Ollama local (Qwen3 4B–8B, Q4) | Qwen | Never decides a grade |

Mistral was dropped because its API is not free. Every role is now on Gemini, Groq or local Ollama, and families are tracked explicitly in `config/roles.yaml` (`family:`), with a test that enforces the separation rules.

The judge choice is **provisional until the Phase 2 gate**.

**Daily budget is the binding constraint.** Groq's free tier gives about 200K tokens per model per day (about 65 scoring-sized calls), and Gemini Flash gives somewhere between 250 and 1,500 requests per day depending on the account. The rate limiter enforces requests per day *and* tokens per day, so a long experiment stops cleanly with `QuotaExhausted` and resumes from the cache the next day.

### Stack

| Concern | Choice | Reason |
|---|---|---|
| Language | Python 3.12+ | Ecosystem for every provider SDK and metrics |
| Schemas / validation | Pydantic v2 | One source of truth for the JSON schemas sent to models and for validating replies |
| Provider SDKs | `google-genai`, `mistralai`, `groq`, `ollama` behind our own `Provider` protocol | Thin, explicit, no heavy abstraction layer to debug |
| Storage | SQLite (single file) | Rubric store, traces, response cache; zero setup |
| Metrics | `scipy`, `scikit-learn` | Spearman/Pearson, QWK, precision/recall |
| CLI | `typer` | Experiments and batch runs |
| UI | Streamlit | Fastest route to a usable demo; calls the core library directly |
| Tests | `pytest` | Fake provider + recorded responses |
| Lint / format / types | `ruff`, `mypy` | Cheap insurance |

---

## 2. Gaps in the design doc, and how this plan closes them

These came out of reviewing the design text against the pipeline diagram. Each one is resolved in the phase noted.

| # | Gap | Resolution | Phase |
|---|---|---|---|
| G1 | The diagram routes creative answers into the "confidence low?" check, but path ID is skipped for creative | Creative answers go straight to scoring; amendment and verification are disabled. The trace records `creative_route: true` | 4 |
| G2 | The "five most obvious answers" are generated but never consumed | Passed into the creative scoring call as the originality negative test | 4 |
| G3 | Rubric-store write-back is not in the diagram | Accepted amendments are stored as a new rubric version with a new hash. Path ID reads the latest version | 5 |
| G4 | Unclear who writes the feedback | **Code** selects and ranks the failed criteria. An LLM only phrases them, given criteria, judge justifications and answer excerpts, **never the reference answer** | 6 |
| G5 | Creative is "dominated by originality", but originality is not one of the four dimensions | Originality tests (obvious-answer overlap, cliché checks) count under **expression**. Constraint satisfaction counts under **correctness**. See D3 | 3–4 |
| G6 | "Only the aggregate is reported" (creative) vs "no single aggregate" (output) | Individual craft-test results are hidden. They aggregate into per-dimension bands like every other task type. Neither contradicts the other once stated | 6 |
| G7 | Weight values, band cut-offs and confidence threshold are unspecified | Start with defaults in config (§6) and calibrate in Phases 5 and 7 | 4, 5, 7 |
| G8 | Rubric criteria are positive ("states X"), so an answer containing the right idea *plus* a false claim passes every criterion. Phase 7's "insert a factual error" perturbation would go undetected | The judge also returns `errors` (verbatim wrong statements). Any error counts against correctness. In Phase 2 it maps to SemEval's "contradictory" label, so it is validated against human grades | 2, 4 |

---

## 3. Open decisions (default chosen, revisit at the named gate)

| ID | Question | Default | Revisit |
|---|---|---|---|
| D1 | Path ID on every answer or on demand? | **Every non-creative answer, merged into the scoring call.** One call returns the identified path, its confidence and per-criterion verdicts. Only on low confidence do we run amendment → verification → re-score. This halves calls in the common case | Phase 4 gate |
| D2 | Show the LLM reference answer to the user? | **Hidden by default.** Optional reveal *after* feedback, labelled "one possible answer". Feedback never quotes it | Phase 8 |
| D3 | Where does originality count for creative tasks? | Under expression (G5) | Phase 4 gate |
| D4 | Single judge or ensemble? | Single (Gemini Flash). An ensemble (Gemini + Qwen on Groq + local Qwen, majority vote) is tested in Phase 7 only if leniency or correlation is borderline. Its cost is bounded by Groq's daily token cap | Phase 2 and Phase 7 gates |
| D5 | Which model phrases feedback? | Local Qwen. Fall back to Gemini Flash if quality is poor in Phase 6 review | Phase 6 gate |

---

## 4. Repository layout

```
eval_engine/
├── pyproject.toml
├── .env.example               # GEMINI_API_KEY, MISTRAL_API_KEY, GROQ_API_KEY, OLLAMA_HOST
├── config/
│   ├── roles.yaml             # role -> provider, model, temperature, rate limits
│   ├── weights.yaml           # task type -> dimension weights
│   └── bands.yaml             # internal score -> band cut-offs; confidence threshold
├── prompts/                   # versioned YAML templates (name, version, system, user); file hash logged
│   ├── smoke.yaml
│   ├── generate.yaml
│   ├── reference_answer.yaml
│   ├── path_and_score.yaml
│   ├── score_creative.yaml
│   ├── amendment_propose.yaml
│   ├── amendment_verify.yaml
│   └── feedback_phrase.yaml
├── src/eval_engine/
│   ├── config.py, prompts.py, hashing.py, cli.py
│   ├── schemas/               # Pydantic: Question, Rubric, Path, Criterion, Verdict, Evaluation, Trace
│   ├── providers/             # base.py (Provider protocol), client.py (routing, retry, cache,
│   │                          # validation, logging), ratelimit.py, factory.py, jsonutil.py, fake.py,
│   │                          # gemini.py, mistral.py, groq_cloud.py, ollama_local.py
│   ├── generation/            # generate.py, consistency.py, freeze.py, reference.py
│   ├── evaluation/            # path_score.py, creative.py, aggregate.py, pipeline.py
│   ├── amendment/             # propose.py, verify.py
│   ├── feedback/              # select.py, phrase.py, bands.py
│   ├── storage/               # db.py, rubric_store.py, calls.py (call log, response cache, usage)
│   └── validation/            # datasets/, metrics.py, perturb.py, verifier_set.py, report.py
├── app/streamlit_app.py
├── experiments/               # one dated script + results file per experiment
├── data/                      # gitignored: corpora, sqlite db, cached responses
├── tests/
└── docs/
```

---

## 5. Core data contracts

These are defined in Phase 1, and every later phase depends on them, so they are worth getting right once.

### Rubric (frozen)

```jsonc
{
  "rubric_id": "uuid",
  "version": 1,                       // increments on accepted amendment
  "parent_hash": null,                // hash of the version this amends
  "question": "...",
  "topic": "history",
  "task_type": "analytical",          // factual | analytical | explanatory | creative
  "shape": "multi_path_claim_evidence", // checklist | multi_path_claim_evidence | multi_path | craft_tests
  "paths": [
    {
      "path_id": "P1",
      "description": "Argues from economic causes",
      "criteria": [
        {
          "criterion_id": "P1.C1",
          "dimension": "reasoning",   // correctness | completeness | reasoning | expression
          "statement": "Links at least one economic cause to the outcome with a causal mechanism",
          "evidence_hint": "Look for an explicit 'because/led to' chain",
          "core": true,               // core criteria outrank stylistic ones in feedback
          "weight": 1.0
        }
      ]
    }
  ],
  "obvious_answers": [],              // creative only: 5 items
  "source": "generated",              // generated | amendment
  "hash": "sha256 of canonical JSON (sorted keys, no whitespace, excluding hash)"
}
```

Factual rubrics have one path (a checklist). Creative rubrics have one path of binary craft tests plus `obvious_answers`.

### Judge output (structured)

```jsonc
{
  "identified_path": "P2",
  "path_confidences": {"P1": 0.12, "P2": 0.81},
  "verdicts": [
    {"criterion_id": "P2.C1", "met": true,  "evidence": "quote from answer", "justification": "..."}
  ]
}
```

### Trace (one per evaluation; covers design doc §15)

`evaluation_id, timestamp, question_id, rubric_hash_used, rubric_hash_original, task_type, creative_route, path_confidences, amendment_fired, amendment_proposal (verbatim), verifier_verdict, verifier_reasoning, verifier_framing, final_rubric_source, per_criterion_verdicts, dimension_scores, bands, feedback_items, model_ids per role, prompt_versions, latencies, token_counts, cache_hits`

---

## 6. Default configuration (initial values; calibrated later)

**Weights** (`config/weights.yaml`). These are design choices, stated as such in the final report.

| Task type | Correctness | Completeness | Reasoning | Expression |
|---|---|---|---|---|
| factual | 0.50 | 0.30 | 0.10 | 0.10 |
| analytical | 0.20 | 0.20 | 0.45 | 0.15 |
| explanatory | 0.30 | 0.25 | 0.30 | 0.15 |
| creative | 0.25 (constraints) | 0.15 | 0.10 | 0.50 (craft + originality) |

**Dimension score** = sum of the weights of met criteria in that dimension ÷ sum of the weights of all criteria in that dimension, for the path used. The weights above are used only internally (for correlation and leniency against a single human score). They are never shown as an aggregate.

**Bands** (4 levels per dimension): `< 0.40` Not yet · `0.40–0.65` Developing · `0.65–0.85` Proficient · `≥ 0.85` Strong.

**Path confidence threshold for amendment**: start at `0.5` (max over paths); calibrated in Phase 5.

**Temperatures**: judge and verifier 0; generator 0.7; proposer 0.3; feedback phrasing 0.3.

---

## 7. Phases

Rough effort assumes one intern working part-time on other things. Adjust as you go.

### Phase 0 — Setup and accounts (≈2–3 days)

**Tasks**
- Create API keys: Google AI Studio (Gemini) and Groq.
- Record the actual free-tier limits shown in each console in `config/roles.yaml`. Don't trust blog numbers.
- Install Ollama; pull a Qwen3 4B and 8B Q4 model; measure tokens/s and VRAM use with a 4K-token prompt. Close background apps first, since about 16 GB of RAM is normally in use.
- `git init`, `pyproject.toml`, ruff/mypy/pytest, pre-commit, `.env.example`, `.gitignore` (`.env`, `data/`).

**Exit gate**
- [ ] One live "hello, return this JSON" call succeeds against each of the four providers.
- [ ] Real rate limits are written down.
- [ ] `pytest` and `ruff` run clean on the empty project.

---

### Phase 1 — Foundation: schemas, provider layer, storage (≈1–1.5 weeks)

**Tasks**
1. **Schemas**: Pydantic models from §5. Generate JSON Schema from them for structured output.
2. **Provider protocol**: `complete(role, prompt, schema) -> ParsedResponse`, where the role resolves to provider + model via `router.py`.
3. **Per-provider adapters** normalise structured output: Gemini `response_json_schema`, Groq `json_schema`, Ollama `format=<schema>` (a Mistral adapter is kept for a possible paid upgrade).
4. **Validation and repair**: parse with Pydantic; on failure, retry **once** with the validation error appended; then raise a typed error. Never silently accept malformed output.
5. **Rate limiting**: per-provider token bucket on both requests/min **and** tokens/min (Groq's 8K TPM is the binding constraint). Exponential backoff with jitter on 429 and 5xx.
6. **Response cache**: SQLite keyed by `sha256(model_id + prompt_version + rendered_prompt + schema)`. Experiments read the cache by default; a `--fresh` flag bypasses it.
7. **Prompt registry**: load `prompts/*.md`, render with Jinja2, expose `(name, version, hash)`.
8. **Storage**: SQLite tables `questions`, `rubrics` (versioned, append-only), `evaluations`, `traces`, `cache`.
9. **Fake provider**: returns scripted responses for tests.

**Exit gate**
- [ ] Unit tests cover schema round-trips, cache hits and misses, repair-retry, rate-limiter behaviour, and rubric hashing (same content → same hash; key order doesn't matter).
- [ ] Switching the judge from Gemini to Groq is a one-line config change, verified with a live call.
- [ ] Every live call writes a trace row with model ID, prompt version, tokens and latency.

---

### Phase 2 — Judge pilot on a human-graded corpus (≈1 week) ⚠️ critical gate

The goal is to confirm the judge before anything is built on it.

**Tasks**
1. **Dataset**: SemEval-2013 Task 7, SciEntsBank and Beetle. They have reference answers and human labels (5-way: correct / partially correct / contradictory / irrelevant / non-domain; also 3-way and 2-way). Check licence terms before downloading. ASAP-SAS (Kaggle) is a second corpus if time allows.
2. **Rubric adapter**: convert each dataset question's reference answer into a checklist rubric (one pass with the generator, gpt-oss-120b, then **manually spot-check 20**). This tests the judge on rubrics like the ones it will see in production.
3. **Sample**: about 300 answers, stratified by label and question.
4. **Run** the scoring prompt with three judges: Gemini Flash, Qwen on Groq and local Qwen. All responses are cached. gpt-oss-120b is not a judge candidate, because it generated the rubrics. Groq's daily token cap means the Qwen run takes several days; let it resume from the cache.
5. **Map** judge output to the dataset's label scale. Primary metric: 2-way and 3-way, where binary grading is known to be reliable.
6. **Metrics** (`validation/metrics.py`):
   - **Leniency** = mean normalised signed error vs. human score (Pathak et al.), target `|leniency| ≤ 0.1`.
   - **Correlation**: Spearman and quadratic weighted kappa (QWK).
   - Macro-F1 for the categorical labels.
   - **Run-to-run stability**: rerun 50 items 3× fresh and report the verdict flip rate.
   - Report bootstrap 95% confidence intervals for all of these.

**Exit gate (decision)**
- [ ] Gemini `|leniency| ≤ 0.1` **and** QWK not worse than Qwen on Groq by more than its confidence interval → **Gemini stays judge.**
- [ ] Otherwise pick the better judge and swap roles in config (the verifier moves to the other model).
- [ ] If no judge passes: iterate the scoring prompt (evidence-first ordering, explicit "partial = not met") **once**, then consider the D4 ensemble.
- [ ] Results are written to `experiments/2_judge_pilot/REPORT.md`.

---

### Phase 3 — Generation stage (≈1 week)

**Tasks**
1. **Topic list**: about 10 topics (history, technology, ethics, science, ...).
2. **Generator prompt**: one structured call returns `question, task_type, rubric (paths + criteria), obvious_answers (creative only)`. Rubric shape is dictated by task type:
   - factual → checklist (single path)
   - analytical → multi-path claim-and-evidence
   - explanatory → multi-path
   - creative → binary craft tests + constraint checks + 5 obvious answers
3. **Consistency checks** in code, regenerating once on failure:
   - Task type matches rubric shape (the design doc's "free consistency check": analytical with only factual checkboxes → fail).
   - Every criterion is binary and observable (simple lint: no "good", "well", "appropriately" without an observable anchor).
   - Every dimension has at least one criterion. Each path has at least one `core` criterion.
   - Creative has exactly 5 obvious answers.
4. **Freeze**: canonical JSON → SHA-256 → store as version 1.
5. **Reference answer**: separate call, given the frozen rubric. Stored, but not passed to any scoring prompt.

**Exit gate**
- [ ] 40 generated questions (10 per task type) reviewed manually against a checklist: criteria are binary, observable and not answer-leaking; there are at least 2 genuinely distinct paths for analytical and explanatory; task type is correct. Pass rate ≥ 85%. Failures feed prompt revisions.
- [ ] Rubric hash is stable across reloads.

---

### Phase 4 — Evaluation core (≈1–1.5 weeks)

**Tasks**
1. **Merged path ID + scoring call** (D1): the judge sees the question and the full rubric (all paths) plus the answer. It returns the identified path, per-path confidences and per-criterion verdicts with evidence quotes. It is **never** shown the reference answer.
2. **Evidence check** in code: each `met: true` verdict must quote a substring that actually appears in the answer (fuzzy match). If not, the verdict is downgraded and flagged in the trace. This is a cheap guard against hallucinated passes.
3. **Creative route** (G1, G2): skip path ID; separate creative scoring prompt with craft tests plus the obvious-answers list ("does the answer substantially reuse any of these?"). Amendment is disabled.
4. **Aggregation** in code: dimension scores per §6, then bands. Weights are read from config.
5. **Pipeline orchestrator** `evaluate(question_id, answer) -> Evaluation`: loads the latest rubric version, routes by task type, applies the confidence-threshold branch (amendment stub until Phase 5), aggregates and writes the trace.

**Exit gate**
- [ ] End-to-end CLI: `eval-engine evaluate --question <id> --answer-file a.txt` prints verdicts, dimension scores and bands.
- [ ] Golden tests: 10 hand-written answers per task type (good / partial / wrong / off-path) with expected band ranges, run against cached responses.
- [ ] Evidence-check catch rate measured on 20 deliberately unsupported verdicts.
- [ ] D1 and D3 confirmed or revised.

---

### Phase 5 — Amendment and verification (≈1.5 weeks)

**Tasks**
1. **Trigger**: max path confidence `< threshold` (§6) on a non-creative task.
2. **Proposer** (gpt-oss-120b on Groq): sees **only** the question and the answer, not the rubric scores. Narrow question: "Does this answer contain a valid approach not covered by these paths?" Returns `{is_new_valid_approach, proposed_path (criteria in rubric schema), justification}`. It does see the existing path descriptions, so it doesn't re-propose them.
3. **Verifier** (Qwen on Groq), with adversarial framing: "Try to break this proposed path: find the factual error, the invalid inference, the missing step, or show it duplicates an existing path." Returns `{accept, reasons, failure_type}`. The framing is a config flag (`adversarial | neutral`) so the experiment in step 6 can isolate it.
4. **Accept** → create rubric version n+1 (`parent_hash` set, `source: amendment`), re-score against the amended path, and log both hashes.
   **Reject** → score against the original rubric; record `divergence_reason` for feedback.
5. **Rubric store reuse** (G3): later evaluations of the same question load the latest version, so an accepted path is matched by path ID instead of being re-derived.
6. **Verifier test set** (`validation/verifier_set.py`), per design §14:
   - 20 questions × 5 proposals = 100 items, **hand-verified**.
   - Positive class: a valid but unlisted approach (a separate model asked to solve it differently from the listed paths).
   - Negative classes: (a) fluent confident nonsense, (b) correct conclusion with invalid reasoning, (c) restatement of an existing path, (d) real approach with a hole.
   - Run under adversarial **and** neutral framing.
7. **Calibrate the threshold**: sweep 0.3–0.7 on the Phase 4 golden set plus the verifier-set answers. Pick the value that triggers on off-path answers without firing on ordinary partial answers.

**Exit gate**
- [ ] Report precision and recall on the positive class, and the rejection rate per negative class, for both framings. **False-accept rate on class (a) ≤ 10%**, because a false accept is the costly error. Otherwise tighten the verifier prompt or require two-verifier agreement (Qwen on Groq + local Qwen 8B as a weaker second vote, or Gemini if it isn't also judging that item).
- [ ] Amendment fires on < 15% of ordinary golden-set answers at the chosen threshold.
- [ ] Results are written to `experiments/5_verifier/REPORT.md`.

---

### Phase 6 — Feedback and output (≈1 week)

**Tasks**
1. **Selection (code, deterministic)**:
   - Candidates are the failed criteria on the path used. Rank by `core` first, then by weight × dimension weight for the task type.
   - Take the top 2–3. Add 1–2 "what worked" items from met core criteria.
   - Cluster near-duplicates so two points don't say the same thing.
2. **Phrasing (LLM, D5)**: input is the selected criteria, judge justifications and evidence quotes. Output must:
   - name what in the answer caused the judgement,
   - be forward-looking (an action),
   - reference the criterion,
   - never reference or paraphrase the reference answer.

   A post-check in code rejects outputs with high n-gram overlap with the reference answer, then re-phrases or falls back to a template.
3. **Amendment messaging**:
   - Accepted → a neutral statement: "Your approach differs from the standard routes and was evaluated on its own terms." No flattery.
   - Rejected → a distinct voice: the answer diverged, was checked, and didn't hold up because <verifier reason>.
4. **Bands view**: shown after the feedback, per dimension, with no aggregate.
5. **Trace logging** completed for the §5 fields.

**Exit gate**
- [ ] 30 evaluations reviewed by hand against a feedback checklist: specific, actionable, at most 3 problem points, includes what worked, no reference-answer leakage, correct amendment voice. Pass rate ≥ 90%.
- [ ] D5 confirmed: if local Qwen fails more than 20% of the review, switch phrasing to Gemini Flash.

---

### Phase 7 — Full validation (≈1.5 weeks)

**Tasks**
1. **Borrowed corpus, end-to-end**: rerun the Phase 2 sample through the *full* engine (merged path ID, evidence check, aggregation). Report leniency and correlation against Phase 2, so we know whether the pipeline added or lost accuracy.
2. **Synthetic perturbation** (`validation/perturb.py`; generated locally or with Gemini):
   - Start from about 30 good answers across factual, analytical and explanatory.
   - Apply each perturbation: drop a key point (→ completeness), insert a factual error (→ correctness), break a reasoning link (→ reasoning), damage only the expression (→ expression).
   - Metrics: detection rate (the score drops in the target dimension) and **attribution accuracy** (the largest drop is in the *correct* dimension). Report a confusion matrix of injected vs. attributed dimension.
3. **Small human-graded set**: 40–60 answers across 1–2 task types, graded by 2 people against the same rubric. Report inter-rater agreement first, then engine leniency and correlation with bootstrap confidence intervals. If grader time runs short, use pairwise ranking ("which of these two is better?") and report agreement with the engine's ordering.
4. **Ensemble check (D4)**, only if results are borderline: majority vote of Gemini + Qwen on Groq + local Qwen on the same items.
5. **Calibrate band cut-offs** against the human-graded set. Keep 4 bands unless adjacent bands are indistinguishable.

**Exit gate**
- [ ] `|leniency| ≤ 0.1` on both the borrowed corpus and the human set (or a documented reason why not).
- [ ] Perturbation attribution accuracy ≥ 70% overall, reported per dimension.
- [ ] `docs/VALIDATION_REPORT.md` reports correlation **and** leniency together, and states creative evaluation's weakness honestly (design §9).

---

### Phase 8 — Interface and demo (≈1 week)

**Tasks**
1. **Streamlit app**:
   - Learner view: pick a topic → generated question → write an answer → feedback first, then bands. Optional "see one possible answer" toggle (D2).
   - Admin view: browse traces, rubric versions and amendment history, filtered by "amendment fired".
2. **CLI** for batch runs: `generate`, `evaluate`, `validate judge|perturb|verifier`.
3. **Quota display**: remaining calls per provider, from the rate limiter's counters.
4. **Graceful degradation**:
   - If the judge provider is rate-limited, queue the request and show "evaluating…". Never fall back silently to a weaker judge.
   - If an amendment can't be verified (verifier down), grade against the original rubric and mark the trace.

**Exit gate**
- [ ] A new user can go from topic to feedback in under 2 minutes without help.
- [ ] Each of the 3 degradation paths has been triggered deliberately and behaves as specified.

---

### Phase 9 — Hardening and documentation (≈3–5 days)

**Tasks**
- README: setup, keys, running each experiment, swapping models.
- `docs/DECISIONS.md`: the D1–D5 outcomes and any role swaps, each with the evidence behind it.
- Ceiling-frequency analysis from the accumulated traces: how often amendments fire, and how often they're accepted, per task type (design §15).
- Pin dependency versions; record model IDs used for the final results.
- Final report / presentation.

**Exit gate**
- [ ] Fresh clone + `.env` → the demo runs from the README alone.
- [ ] All validation numbers in the final report can be regenerated from cached responses with one command.

---

## 8. Quota budget (estimate; recheck against Phase 0 numbers)

| Activity | Calls | Main provider |
|---|---|---|
| One evaluation, common case (merged path ID + scoring, feedback phrasing) | 1 judge + 1 local | Gemini |
| One evaluation with amendment | + 1 proposer + 1 verifier + 1 re-score | Groq (gpt-oss), Groq (Qwen), Gemini |
| Generate one question | 2 (rubric + reference) | Groq (gpt-oss) |
| Phase 2 pilot | ≈300 × 3 judges + 150 stability reruns | Gemini, Groq (Qwen), local |
| Phase 3 generation review | 40 questions × 2 | Groq (gpt-oss) |
| Phase 5 verifier set | 100 × 2 framings | Groq (Qwen) |
| Phase 7 perturbation | ≈30 × 4 perturbations × 1 judge | Gemini |

At about 200K tokens/day per Groq model, a 300-item Qwen judge run (~3K tokens each) takes about 5 days, and the verifier set takes about 3. Start those runs early and let them resume from the cache. Gemini's daily request cap decides how fast the Gemini runs go; check the real number in AI Studio in Phase 0. The cache makes every rerun free.

---

## 9. Testing strategy

| Layer | How |
|---|---|
| Schemas, hashing, aggregation, bands, feedback selection | Pure unit tests (no models) |
| Pipeline orchestration and routing (creative route, amendment branches) | Fake provider with scripted responses |
| Prompt regressions | Golden set replayed from cached responses; a diff in verdicts fails the test |
| Live behaviour | `experiments/` scripts only, never in CI |

---

## 10. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Free-tier limits or models change mid-project | High | Medium | Role→model config, cache, model IDs in traces; a backup for every role (Gemini ↔ Groq; local Qwen as last resort). Mistral already dropped out because its API isn't free |
| Daily free quota runs out mid-experiment | High | Low | Requests-per-day and tokens-per-day enforced client-side; `QuotaExhausted` stops cleanly; the cache resumes the run next day |
| Judge fails the leniency target | Medium | High | Phase 2 gate; prompt iteration; ensemble (D4) |
| Verifier false-accepts nonsense ("flattery machine") | Medium | High | Phase 5 gate on class (a); two-verifier agreement fallback; the original rubric stays binding |
| Generated rubrics leak the answer or aren't binary | Medium | Medium | Lint checks + Phase 3 manual review |
| Hallucinated evidence for `met` verdicts | Medium | Medium | Evidence-substring check (Phase 4) |
| Self-preference via a shared generator/proposer family | Low–Medium | Medium | Judge and verifier are different families; feedback never quotes the reference |
| Local model too slow or too big for 6 GB VRAM | Medium | Low | Local only does non-grading roles; fall back to Gemini |
| Data used for training by free providers | Certain | Low (test data only) | No real learner data; stated in the README |
| Creative grading unreliable | High | Medium | Acknowledged in the design; reported honestly; machinery that would add noise is disabled |

---

## 11. Phase summary

| Phase | Output | Gate |
|---|---|---|
| 0 Setup | Keys, real limits, tooling | Live call to all 4 providers |
| 1 Foundation | Schemas, provider layer, cache, storage | Config-only model swap works |
| 2 Judge pilot | Judge confirmed on SciEntsBank/Beetle | \|leniency\| ≤ 0.1 |
| 3 Generation | Frozen, hashed, linted rubrics | ≥ 85% manual-review pass |
| 4 Evaluation core | End-to-end scoring + bands | Golden tests pass |
| 5 Amendment | Proposer + verifier + rubric versioning | False-accept on nonsense ≤ 10% |
| 6 Feedback | Prioritised, criterion-referenced feedback | ≥ 90% review pass |
| 7 Validation | Validation report | Leniency + attribution targets |
| 8 Interface | Streamlit + CLI | Degradation paths verified |
| 9 Hardening | Docs, decisions, reproducible results | Fresh-clone demo |
