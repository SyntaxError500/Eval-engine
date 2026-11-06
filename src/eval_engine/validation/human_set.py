"""Phase 7 task 3: a small human-graded set (design doc §13, plan Phase 7).

Two graders mark the same answers against the same rubric, blind to the engine: each
criterion met or not, whether the answer states something false, and an overall label on the
Phase 2 scale (correct / partially correct / incorrect). Inter-rater agreement is reported
first, then the engine's leniency and correlation against the graders, with bootstrap CIs.

Scope: factual and explanatory questions whose rubric has a single path, so a grader never has
to decide which route an answer took. Answers: the golden answers for those questions, plus
hand-checked perturbations of their reference answers. That spans full, partial, wrong,
off-topic and subtly broken answers.
"""

import csv
import json
import random
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT
from eval_engine.schemas.common import TaskType
from eval_engine.storage import RubricStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import golden, perturb

HUMAN_DIR = REPO_ROOT / "experiments" / "7_validation" / "human"
# Only this folder goes to graders; key.json stays in HUMAN_DIR (senior review step 4).
FOR_GRADERS = "for_graders"
TASK_TYPES = (TaskType.FACTUAL, TaskType.EXPLANATORY)
TARGET_SIZE = 50
SEED = 7
OVERALL = ("correct", "partially_correct", "incorrect")


@dataclass
class Answer:
    answer_id: str  # neutral, so a grader can't infer the intended quality
    source: str  # golden id or perturbation id; never shown to graders
    question_id: str
    text: str


def select(conn: sqlite3.Connection) -> list[Answer]:
    questions, rubrics = QuestionStore(conn), RubricStore(conn)

    def eligible(question_id: str) -> bool:
        q = questions.get(question_id)
        return q.task_type in TASK_TYPES and len(rubrics.get(q.rubric_hash).paths) == 1

    pool = [(g.id, g.question, g.answer) for g in golden.load_items() if eligible(g.question)]
    perturbed = [
        (i.item_id, i.question_id, i.perturbed)
        for i in perturb.load_items()
        if eligible(i.question_id)
    ]
    rng = random.Random(SEED)
    rng.shuffle(perturbed)
    pool += perturbed[: max(0, TARGET_SIZE - len(pool))]
    rng.shuffle(pool)
    return [Answer(f"A{n:02d}", source, qid, text) for n, (source, qid, text) in enumerate(pool, 1)]


def write_sheets(conn: sqlite3.Connection, out_dir: Path = HUMAN_DIR) -> list[Answer]:
    """The grading sheet and one blank CSV per grader, in `for_graders/`; the private key
    (which answer is which perturbation) in `out_dir` itself, never in the graders' folder."""
    questions, rubrics = QuestionStore(conn), RubricStore(conn)
    answers = select(conn)
    share = out_dir / FOR_GRADERS
    share.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Human grading sheet (Phase 7)",
        "",
        f"Thank you for grading. There are {len(answers)} short answers. Judge each one against "
        "its listed requirements only.",
        "",
        "1. For each requirement, mark **Y** if the answer clearly states it (in any words, a "
        "correct paraphrase counts) and **N** if it is missing, only hinted at, or wrong.",
        '   - A paraphrased name counts when it clearly identifies the same thing ("synthesis '
        'stage" for S phase).',
        "   - A requirement that lists several parts needs every part for Y.",
        '   - A requirement that refers to something named earlier ("a function of the third '
        "macronutrient named\") is **N** when that named thing isn't valid (vitamins are not a "
        "macronutrient).",
        "2. Mark **false statement: Y** if the answer states anything factually wrong, even if "
        "every requirement is met.",
        "3. Give an overall label:",
        "   - **correct**: fully answers the question and states nothing false;",
        "   - **partially_correct**: some of it is right and something is missing, or it contains "
        "a false statement on a side detail (a wrong date, name or example);",
        "   - **incorrect**: mostly missing or wrong, or a false statement contradicts a "
        "requirement or the core idea and little else is right.",
        "   Any false statement rules out **correct**.",
        "",
        "Please grade independently, without discussing with the other grader. Enter your marks "
        "in your own copy of the CSV (`grades_grader1.csv` or `grades_grader2.csv`): one row per "
        "requirement, plus one `overall` row and one `false_statement` row per answer.",
        "",
    ]
    rows: list[dict[str, str]] = []
    for a in answers:
        q = questions.get(a.question_id)
        path = rubrics.get(q.rubric_hash).paths[0]
        lines += [
            f"## {a.answer_id}",
            "",
            f"**Question:** {q.text}",
            "",
            f"**Answer:** {a.text}",
            "",
        ]
        lines += ["| Requirement | Y / N |", "|---|---|"]
        for c in path.criteria:
            lines.append(f"| {c.criterion_id}: {c.statement} | |")
            rows.append({"answer_id": a.answer_id, "item": c.criterion_id, "mark": ""})
        lines += [
            "",
            "False statement: Y / N",
            "",
            "Overall: correct / partially_correct / incorrect",
            "",
        ]
        rows.append({"answer_id": a.answer_id, "item": "false_statement", "mark": ""})
        rows.append({"answer_id": a.answer_id, "item": "overall", "mark": ""})
    (share / "grading_sheet.md").write_text("\n".join(lines), encoding="utf-8")
    for grader in ("grader1", "grader2"):
        with (share / f"grades_{grader}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["answer_id", "item", "mark"])
            w.writeheader()
            w.writerows(rows)
    (out_dir / "key.json").write_text(
        json.dumps([asdict(a) for a in answers], indent=1, ensure_ascii=False), encoding="utf-8"
    )
    return answers


def read_grades(path: Path) -> dict[str, dict[str, str]]:
    """{answer_id: {item: mark}} with marks normalised to lower case."""
    out: dict[str, dict[str, str]] = {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.setdefault(r["answer_id"], {})[r["item"]] = r["mark"].strip().lower()
    return out


def overall_graded(label: str) -> float:
    return {"correct": 1.0, "partially_correct": 0.5, "incorrect": 0.0}[label]


def summary(answers: list[Answer]) -> dict[str, Any]:
    kinds: dict[str, int] = {}
    for a in answers:
        kind = a.source.split("/")[-1] if "/" in a.source else a.source.split("-")[-1]
        kinds[kind] = kinds.get(kind, 0) + 1
    return {
        "answers": len(answers),
        "questions": len({a.question_id for a in answers}),
        "by_kind": kinds,
    }
