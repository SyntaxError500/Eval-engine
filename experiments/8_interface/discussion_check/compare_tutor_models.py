"""T1 (the Java objections) under other tutor configurations, to decide whether the remaining
T1 failure is the local model. Same scenario, same code checks; only the tutor role changes.

Run: .venv/Scripts/python experiments/8_interface/discussion_check/compare_tutor_models.py
"""

import json
import sys
import tempfile
from pathlib import Path

from eval_engine.config import db_path, load_config, load_env
from eval_engine.storage import connect
from eval_engine.validation import discussion_check as dc

VARIANTS = {
    # Same local model with Qwen3 "thinking" on (slower on a 6 GB GPU).
    "qwen3_8b_thinking": {"reasoning_effort": None, "max_output_tokens": 4000},
    # The generator's model on Groq (free tier, 1,000 requests/day).
    "gpt_oss_120b": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "family": "openai-oss",
        "reasoning_effort": "low",
        "json_mode": "strict",
        "max_output_tokens": 3000,
    },
}


def main(names: list[str]) -> None:
    load_env()
    real = connect(db_path())
    base = load_config()
    out = {}
    for name in names:
        config = base.model_copy(deep=True)
        config.roles["tutor"] = config.roles["tutor"].model_copy(update=VARIANTS[name])
        with tempfile.TemporaryDirectory() as tmp:
            out[name] = dc.run(real, config, Path(tmp), {"T1"})["T1"]
        r = out[name]
        print(f"{name}: max overlap {r['max_overlap']}, fallbacks {r['fallbacks']}, "
              f"rejected drafts {r['rejected_drafts']}")  # fmt: skip
    path = dc.OUT_DIR / f"results_T1_{'_'.join(names)}.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    report = dc.report({f"T1 {n}": r for n, r in out.items()})
    (dc.OUT_DIR / f"REPORT_T1_{'_'.join(names)}.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:] or list(VARIANTS))
