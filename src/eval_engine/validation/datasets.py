"""SemEval-2013 Task 7 corpora (SciEntsBank, Beetle), CC BY 4.0.

Source: https://huggingface.co/datasets/nkazi/SciEntsBank and
https://huggingface.co/datasets/nkazi/Beetle (Dzikovska et al., 2013, ACL S13-2045).
Files are read from data/datasets/<name>/<split>.parquet (gitignored).
"""

import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pyarrow.parquet as pq

from eval_engine.config import REPO_ROOT

DATASET_DIR = REPO_ROOT / "data" / "datasets"

# Label ids as published on the dataset cards.
LABELS_5WAY = (
    "correct",
    "contradictory",
    "partially_correct_incomplete",
    "irrelevant",
    "non_domain",
)


@dataclass(frozen=True)
class GradedAnswer:
    item_id: str
    dataset: str
    split: str
    question: str
    reference_answer: str
    student_answer: str
    label: str  # 5-way

    @property
    def question_key(self) -> str:
        # The reference is part of the key: a few questions carry more than one reference
        # answer, and each needs its own rubric.
        return f"{self.dataset}::{self.question}::{self.reference_answer}"


def load_split(dataset: str, split: str, directory: Path = DATASET_DIR) -> list[GradedAnswer]:
    path = directory / dataset / f"{split}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found; see experiments/2_judge_pilot/README.md")
    rows = pq.read_table(path).to_pylist()
    items: list[GradedAnswer] = []
    for r in rows:
        label = r["label"]
        items.append(
            GradedAnswer(
                item_id=f"{dataset}/{split}/{r['id']}",
                dataset=dataset,
                split=split,
                question=str(r["question"]).strip(),
                reference_answer=str(r["reference_answer"]).strip(),
                student_answer=str(r["student_answer"]).strip(),
                label=LABELS_5WAY[label] if isinstance(label, int) else str(label),
            )
        )
    return items


def sample_by_question(
    items: list[GradedAnswer], n_questions: int, per_question: int, seed: int
) -> list[GradedAnswer]:
    """Pick questions first (bounds the number of rubric-generation calls), then answers.

    Within a question, answers are drawn round-robin across labels so each question
    contributes label diversity instead of mostly its majority label.
    """
    rng = random.Random(seed)
    by_q: dict[str, list[GradedAnswer]] = defaultdict(list)
    for it in items:
        by_q[it.question_key].append(it)
    eligible = sorted(k for k, v in by_q.items() if len(v) >= per_question)
    chosen = rng.sample(eligible, min(n_questions, len(eligible)))

    out: list[GradedAnswer] = []
    for q in sorted(chosen):
        by_label: dict[str, list[GradedAnswer]] = defaultdict(list)
        for it in sorted(by_q[q], key=lambda x: x.item_id):
            by_label[it.label].append(it)
        for bucket in by_label.values():
            rng.shuffle(bucket)
        labels = sorted(by_label)
        picked: list[GradedAnswer] = []
        while len(picked) < per_question:
            progressed = False
            for lab in labels:
                if by_label[lab] and len(picked) < per_question:
                    picked.append(by_label[lab].pop())
                    progressed = True
            if not progressed:
                break
        out.extend(picked)
    return out
