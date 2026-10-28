# Phase 2: judge pilot

Tests the judge against human grades before anything is built on top of it.

**Data:** SciEntsBank and Beetle, SemEval-2013 Task 7 (Dzikovska et al., 2013), CC BY 4.0,
from huggingface.co/datasets/nkazi/SciEntsBank and huggingface.co/datasets/nkazi/Beetle.
The unseen-answers test splits (`test_ua`) are used. The files are not committed.

## Get the data (Git Bash)

```bash
mkdir -p data/datasets/SciEntsBank data/datasets/Beetle
curl -L -o data/datasets/SciEntsBank/test_ua.parquet https://huggingface.co/datasets/nkazi/SciEntsBank/resolve/main/data/test-ua-00001.parquet
curl -L -o data/datasets/Beetle/test_ua.parquet https://huggingface.co/datasets/nkazi/Beetle/resolve/main/data/test-ua-00001.parquet
```

## Run

```bash
eval-engine pilot prepare                              # 30 questions x 5 answers per dataset; 1 rubric per question
# review experiments/2_judge_pilot/rubrics_review.md (spot-check at least 20)
eval-engine pilot run --role judge                     # Gemini
eval-engine pilot run --role judge_candidate_qwen      # Qwen on Groq (several days on the free tier)
eval-engine pilot run --role judge_candidate_local     # qwen3:8b via Ollama
eval-engine pilot stability --role judge               # 50 items x 3 fresh reruns
eval-engine pilot report                               # writes REPORT.md
```

Every command can be rerun. Finished calls come from the cache, so a run that stops on a
daily quota (exit code 2) picks up where it left off.

## Mapping (fixed before any judge ran)

See `src/eval_engine/validation/labels.py`:
- **Human graded scale:** correct = 1.0, partially correct = 0.5, everything else = 0.0.
- **Engine:**
  - any wrong statement listed by the judge → contradictory, 0.0
  - all core criteria met → correct, 1.0
  - some criterion met → 0.5
  - nothing met → 0.0
- **Gate:** |leniency| ≤ 0.1 for `judge`, and no candidate has a QWK interval entirely above
  the judge's.
