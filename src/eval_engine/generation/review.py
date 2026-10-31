"""Phase 3 exit gate: generate a batch (task types x topics), then write a review sheet for
manual checking. Resumable: slots that already have a question are skipped."""

import json
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT, load_topics, load_weights
from eval_engine.generation.generate import GenerationError, generate_question, write_reference
from eval_engine.providers.base import QuotaExhausted
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.common import TaskType
from eval_engine.schemas.question import Question
from eval_engine.schemas.rubric import Rubric
from eval_engine.storage.question_store import QuestionStore
from eval_engine.storage.rubric_store import RubricStore

REVIEW_DIR = REPO_ROOT / "experiments" / "3_generation"

CHECKLIST = (
    "Task type is right for the question",
    "Question is self-contained and answerable in a short paragraph",
    "Every criterion is binary and observable",
    "Criteria ask for nothing the question doesn't need",
    "Criteria don't leak a model sentence to copy",
    "Granular enough that a partial answer can meet some criteria",
    "Paths are genuinely different approaches (analytical / explanatory only)",
)


def slots(per_type: int, topics: list[str]) -> list[tuple[TaskType, str]]:
    """Each task type gets `per_type` topics, rotated so types don't share a topic order."""
    out: list[tuple[TaskType, str]] = []
    for ti, task_type in enumerate(TaskType):
        for i in range(per_type):
            out.append((task_type, topics[(i + ti) % len(topics)]))
    return out


def build_batch(
    client: LLMClient,
    rubrics: RubricStore,
    questions: QuestionStore,
    *,
    per_type: int = 10,
    out_dir: Path = REVIEW_DIR,
) -> dict[str, Any]:
    weights = load_weights()
    existing = {(q.task_type, q.topic): q for q in questions.all()}
    built = skipped = 0
    failed: list[dict[str, Any]] = []
    retried: list[str] = []
    stopped: str | None = None
    try:
        for task_type, topic in slots(per_type, load_topics()):
            if (task_type, topic) in existing:
                skipped += 1
                q = existing[(task_type, topic)]
                if q.reference_answer is None:  # stopped before its reference last time
                    write_reference(client, questions, q, rubrics.latest(q.rubric_id))
                continue
            try:
                g = generate_question(client, rubrics, questions, topic, task_type, weights=weights)
            except GenerationError as e:
                failed.append(
                    {"task_type": task_type.value, "topic": topic, "problems": e.problems}
                )
                continue
            built += 1
            existing[(task_type, topic)] = g.question
            if g.attempts > 1:
                retried.append(g.question.question_id)
    except QuotaExhausted as e:
        stopped = str(e)

    batch = [existing[s] for s in slots(per_type, load_topics()) if s in existing]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "batch.json").write_text(
        json.dumps(
            {
                "question_ids": [q.question_id for q in batch],
                "retried_after_checks": retried,
                "failed_checks_twice": failed,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    write_review(rubrics, batch, out_dir / "review.md")
    return {
        "in_batch": len(batch),
        "built": built,
        "skipped": skipped,
        "failed": len(failed),
        "retried": len(retried),
        "stopped": stopped,
    }


def write_review(rubrics: RubricStore, batch: list[Question], path: Path) -> None:
    lines = [
        "# Phase 3: generated question review",
        "",
        f"{len(batch)} questions. For each one, tick every item that holds. The gate passes "
        "when at least 85% of questions pass every item that applies to them.",
        "",
        "Checklist per question:",
        "",
        *[f"{i}. {c}" for i, c in enumerate(CHECKLIST, 1)],
        "",
    ]
    for n, q in enumerate(batch, 1):
        r = rubrics.get(q.rubric_hash)
        lines += _question_block(n, q, r)
    path.write_text("\n".join(lines), encoding="utf-8")


def _question_block(n: int, q: Question, r: Rubric) -> list[str]:
    out = [
        f"## {n}. {q.task_type.value} · {q.topic} · `{q.question_id}`",
        "",
        f"**Q:** {q.text}",
        "",
    ]
    for p in r.paths:
        out.append(f"**Path {p.path_id}:** {p.description}")
        out.append("")
        for c in p.criteria:
            tag = "core" if c.core else "non-core"
            out.append(
                f"- `{c.criterion_id}` {c.dimension.value}, {tag}, w={c.weight:g}: {c.statement}"
            )
        out.append("")
    if r.obvious_answers:
        out += ["**Obvious answers (originality check):**", ""]
        out += [f"- {a}" for a in r.obvious_answers]
        out.append("")
    if q.reference_answer:
        ref_path = q.reference_path_id or "?"
        out += [f"**Reference answer** (path {ref_path}):", "", f"> {q.reference_answer}", ""]
    out += ["Review: " + " ".join(f"[ ] {i}" for i in range(1, len(CHECKLIST) + 1)), ""]
    return out
