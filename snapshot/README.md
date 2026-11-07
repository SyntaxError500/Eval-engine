# Snapshot

What a fresh clone needs, since `data/` is gitignored. Load it once after cloning:

```bash
.venv/Scripts/eval-engine snapshot import
```

| File | Contents |
|---|---|
| `rubrics.jsonl.gz` | every rubric version (reviewed bank, experiments, amendments) |
| `questions.jsonl.gz` | every question, including the 37 reviewed ones the app serves |
| `evaluations.jsonl.gz` | evaluation traces from the experiments (app submissions are left out) |
| `response_cache.jsonl.gz` | cached model responses, keyed by a hash of the request; lets `eval-engine reproduce` regenerate every report with no API calls |
| `datasets/` | SciEntsBank and Beetle, SemEval-2013 Task 7 (Dzikovska et al., 2013, ACL S13-2045), CC BY 4.0, from huggingface.co/datasets/nkazi |

It contains only test, borrowed or synthetic answers, never real learners' data, and no API
keys. Refresh it with `eval-engine snapshot export` after new results; unchanged data exports
byte-identical.
