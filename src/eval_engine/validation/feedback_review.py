"""Phase 6 gate set: 30 evaluations with feedback, written up for hand and external review.

Covers every feedback situation: good, partial, wrong and off-topic golden answers on all
four task types, creative answers with an obvious idea, a cliché or a broken constraint, and
amendment cases from the Phase 5 set (accepted routes, a route accepted but still penalised,
declined misconceptions). Each case runs in a throwaway store holding the v1 rubric, so an
accepted amendment can't touch the real rubrics. Judge, proposer and verifier replies come
from the cache; the feedback calls are new.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.feedback.render import learner_view
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.question import Question
from eval_engine.schemas.rubric import Rubric
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore, connect
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import golden, verifier_set

FEEDBACK_DIR = REPO_ROOT / "experiments" / "6_feedback"

GOLDEN_CASES = (
    "cell-good", "cell-partial", "cell-wrong",
    "macro-partial", "macro-wrong", "macro-off",
    "balloon-partial", "balloon-wrong",
    "rain-partial", "rain-wrong", "rain-off",
    "wfh-partial", "wfh-wrong", "wfh-off",
    "wwi-nationalism", "wwi-partial", "wwi-wrong",
    "coffee-obvious", "coffee-partial", "coffee-wrong",
    "fire-cliche", "fire-too-long", "fire-no-character", "fire-off",
)  # fmt: skip
AMENDMENT_CASES = (
    "b850a615f22e-valid_hpa",
    "610c46d48e48-valid_context",
    "91798e725180-holed",
    "23575fb39cfd-misconception_burner_thrust",
    "91798e725180-misconception_mirror_neurons",
    "669bce9c85fb-nonsense",
)

CHECKLIST = (
    "Specific: each point names what in the answer led to it",
    "Actionable: each problem point says what to do next",
    "At most 3 problem points",
    "Says what worked, when anything did",
    "Faithful: nothing contradicts the grading details or misstates the answer",
    "No reference-answer leakage: no wording or content taken from the hidden model answer",
    "Route note, when shown, is in the right voice: neutral when accepted, distinct with a "
    "reason when not",
)


def cases(conn: sqlite3.Connection) -> list[tuple[str, str, str]]:
    """(case id, question id, answer) in review order."""
    by_golden = {g.id: g for g in golden.load_items()}
    by_item = {i.item_id: i for i in verifier_set.load_items()}
    out = [(c, by_golden[c].question, by_golden[c].answer) for c in GOLDEN_CASES]
    out += [(c, by_item[c].question_id, by_item[c].answer) for c in AMENDMENT_CASES]
    return out


def run(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = FEEDBACK_DIR
) -> list[dict[str, Any]]:
    real_rubrics, real_questions = RubricStore(conn), QuestionStore(conn)
    rows: list[dict[str, Any]] = []
    for case_id, question_id, answer in cases(conn):
        q = real_questions.get(question_id)
        scratch = connect(":memory:")
        RubricStore(scratch).save(real_rubrics.get(q.rubric_hash))
        QuestionStore(scratch).save(q)
        t = evaluate(
            client,
            RubricStore(scratch),
            QuestionStore(scratch),
            EvaluationStore(scratch),
            question_id,
            answer,
            feedback=True,
        )
        rubric = RubricStore(scratch).get(t.rubric_hash_used)
        rows.append({"case": case_id, "answer": answer, "trace": json.loads(t.model_dump_json())})
        rows[-1]["path"] = _path_rows(rubric, t)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "cases.json").write_text(
        json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    return rows


def _path_rows(rubric: Rubric, t: EvaluationTrace) -> list[dict[str, Any]]:
    path_id = t.identified_path or rubric.paths[0].path_id
    met = {v.criterion_id: v.met for v in t.verdicts}
    return [
        {
            "id": c.criterion_id,
            "statement": c.statement,
            "core": c.core,
            "met": met.get(c.criterion_id),
        }
        for c in rubric.path(path_id).criteria
    ]


def summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    traces = [EvaluationTrace.model_validate(r["trace"]) for r in rows]
    items = [i for t in traces if t.feedback for i in t.feedback.items]
    return {
        "evaluations": len(traces),
        "items": len(items),
        "by_source": {s: sum(i.source == s for i in items) for s in ("model", "template", "fixed")},
        "with_fallbacks": sum(bool(t.feedback and t.feedback.fallbacks) for t in traces),
        "max_problem_points": max(
            (sum(i.kind == "improve" for i in t.feedback.items) for t in traces if t.feedback),
            default=0,
        ),
    }


def review_sheet(
    rows: list[dict[str, Any]], questions: QuestionStore, out_dir: Path = FEEDBACK_DIR
) -> str:
    lines = [
        "# Feedback review (Phase 6 gate)",
        "",
        "Each evaluation shows what the learner sees, then the grading details it should be "
        "faithful to. Please mark each evaluation pass or fail against the checklist, and for a "
        "fail say which point and why. The gate is a pass rate of at least 90% (27 of 30).",
        "",
        "Checklist:",
        "",
        *[f"{n}. {c}" for n, c in enumerate(CHECKLIST, start=1)],
        "",
        "Wording comes from a small local model, under code checks; a point marked *(template)* "
        "is the plain fallback used when the model's wording failed a check. Grading itself "
        "was validated in Phases 2 and 4; a disagreement with a verdict is worth noting but is "
        "not a feedback failure unless the feedback misstates it.",
        "",
    ]
    for n, row in enumerate(rows, start=1):
        t = EvaluationTrace.model_validate(row["trace"])
        q: Question = questions.get(t.question_id)
        lines += [
            f"## E{n}: {row['case']} ({t.task_type.value})",
            "",
            f"**Question:** {q.text}",
            "",
            f"**Learner answer:** {row['answer']}",
            "",
            "**What the learner sees:**",
            "",
            "```",
            *_marked_view(t),
            "```",
            "",
            "**Grading details:**",
            "",
        ]
        for c in row["path"]:
            mark = "met" if c["met"] else "not met"
            lines.append(f"- {mark}{' (core)' if c['core'] else ''}: {c['statement']}")
        for e in t.errors:
            lines.append(f'- factual error: "{e.quote}" ({e.explanation})')
        if t.addresses_question is False:
            lines.append("- the judge found the answer does not address the question")
        if t.amendment_fired:
            lines.append(f"- different route checked: {_route(t)}")
        if t.obvious_overlap:
            lines.append(f"- reuses an obvious idea (not marked down): {t.obvious_overlap[0]}")
        if q.reference_answer:
            lines += [
                "",
                f"**Hidden model answer (never shown to the learner):** {q.reference_answer}",
            ]
        lines += ["", "**Verdict:** pass / fail, and why:", ""]
    return "\n".join(lines)


def _marked_view(t: EvaluationTrace) -> list[str]:
    templated = {i.text for i in (t.feedback.items if t.feedback else []) if i.source == "template"}
    return [
        line + "  (template)" if any(line.endswith(x) for x in templated) else line
        for line in learner_view(t)
    ]


def _route(t: EvaluationTrace) -> str:
    if t.final_rubric_source == "amendment":
        return "accepted, graded on the new path"
    if t.verifier_verdict is False:
        return f"rejected by the verifier: {t.verifier_reasoning}"
    return f"not taken up: {t.divergence_reason}"
