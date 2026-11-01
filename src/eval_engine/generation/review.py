"""Phase 3 exit gate: generate a batch (task types x topics), then write a review sheet for
manual checking. Resumable: slots that already have a question are skipped."""

import json
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT, load_topics, load_weights
from eval_engine.generation.consistency import check_rubric
from eval_engine.generation.generate import GenerationError, generate_question, write_reference
from eval_engine.providers.base import QuotaExhausted
from eval_engine.providers.client import LLMClient, StructuredOutputError
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
    "Each path is a complete alternative answer, not a part the question requires "
    "together with the other paths (analytical / explanatory only)",
    "The question's premise and the rubric's facts are correct",
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
    # Only questions made by the current generator prompt count; a prompt fix means the
    # batch is regenerated rather than mixing versions in one review.
    prompt_hash = client.prompts.get("generate").file_hash
    # Questions a reviewer rejected for reasons no automatic check can see (false balance,
    # an invalid path): listed by id in rejected.json, never reused, so their slot regenerates.
    rejected = _id_list(out_dir / "rejected.json")
    # A human reviewer's pass is final: accepted questions are kept as reviewed, even when a
    # newer prompt version or a stricter check would regenerate them.
    accepted = _id_list(out_dir / "accepted.json")
    # Any other reused question must come from the current prompt and pass the CURRENT checks:
    # checks added after it was made would otherwise let it through unexamined.
    existing = {
        (q.task_type, q.topic): q
        for q in questions.all()
        if q.question_id not in rejected
        and (
            q.question_id in accepted
            or (
                q.generator_prompt_hash == prompt_hash
                and not check_rubric(rubrics.get(q.rubric_hash), weights, q.task_type)
            )
        )
    }
    # An accepted question wins its slot over any other candidate.
    for q in questions.all():
        if q.question_id in accepted:
            existing[(q.task_type, q.topic)] = q
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
            except StructuredOutputError as e:
                # One malformed reply must not end the batch; the slot is retried next run.
                failed.append(
                    {"task_type": task_type.value, "topic": topic, "problems": [str(e)[:300]]}
                )
                continue
            built += 1
            existing[(task_type, topic)] = g.question
            if g.attempts > 1:
                retried.append(g.question.question_id)
    except QuotaExhausted as e:
        stopped = str(e)

    # Fixed slot numbers (1..N in slot order): numbering by position among filled slots
    # shifted whenever a slot was empty, so a question's number changed between reviews.
    slot_list = slots(per_type, load_topics())
    numbered = [(n, existing.get(sl), sl) for n, sl in enumerate(slot_list, 1)]
    batch = [q for _, q, _ in numbered if q is not None]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "batch.json").write_text(
        json.dumps(
            {
                "question_ids": [q.question_id for q in batch],
                "slots": [
                    {
                        "slot": n,
                        "task_type": sl[0].value,
                        "topic": sl[1],
                        "question_id": q.question_id if q else None,
                    }
                    for n, q, sl in numbered
                ],
                "retried_after_checks": retried,
                "failed_checks_twice": failed,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    write_review(rubrics, numbered, out_dir / "review.md")
    return {
        "in_batch": len(batch),
        "built": built,
        "skipped": skipped,
        "failed": len(failed),
        "retried": len(retried),
        "stopped": stopped,
    }


def _id_list(path: Path) -> set[str]:
    """Question ids from a reviewer list (accepted.json / rejected.json)."""
    if not path.exists():
        return set()
    return {r["question_id"] for r in json.loads(path.read_text(encoding="utf-8"))}


def write_review(
    rubrics: RubricStore,
    numbered: list[tuple[int, Question | None, tuple[TaskType, str]]],
    path: Path,
) -> None:
    filled = sum(q is not None for _, q, _ in numbered)
    lines = [
        "# Phase 3: generated question review",
        "",
        f"{filled} questions in {len(numbered)} fixed slots (empty slots count as failures). "
        "For each one, tick every item that holds. The gate passes "
        "when at least 85% of questions pass every item that applies to them.",
        "",
        "Checklist per question:",
        "",
        *[f"{i}. {c}" for i, c in enumerate(CHECKLIST, 1)],
        "",
    ]
    for n, q, (task_type, topic) in numbered:
        if q is None:
            lines += [f"## {n}. {task_type.value} · {topic} · (empty slot)", ""]
            continue
        lines += _question_block(n, q, rubrics.get(q.rubric_hash))
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
            asked = f' ← asked by: "{c.requires}"' if c.requires else " ← (no quote)"
            out.append(
                f"- `{c.criterion_id}` {c.dimension.value}, {tag}, w={c.weight:g}: "
                f"{c.statement}{asked}"
            )
        out.append("")
    if r.obvious_answers:
        out += ["**Obvious answers (originality check):**", ""]
        out += [f"- {a}" for a in r.obvious_answers]
        out.append("")
    if q.rubric_doubts:
        out += ["**Fact-check doubts (not counted as errors; please judge):**", ""]
        out += [f"- {d}" for d in q.rubric_doubts]
        out.append("")
    # Reference answers are not shown: they are display-only, never used in grading, and
    # review 1 found factual errors in about a third of them (decision D2).
    out += ["Review: " + " ".join(f"[ ] {i}" for i in range(1, len(CHECKLIST) + 1)), ""]
    return out
