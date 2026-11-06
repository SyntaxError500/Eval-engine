"""Phase 7 task 2: synthetic perturbation (design doc §13, plan Phase 7).

Good answers are degraded in one controlled way each, and the engine should both notice
(detection: the target dimension's score drops) and say where (attribution: the target
dimension drops the most). The true score is unknown, but the direction of change is known.

- completeness: the part meeting a met completeness criterion is removed;
- reasoning: the because/so link meeting a met reasoning criterion is broken;
- correctness: one fact is made false (the implicit no-errors check scores it).

Each targets a criterion the good answer met on its baseline run, so a correct engine has
something to lose, and the change lands in the dimension being tested.

Expression is different. No non-creative rubric has an expression criterion, because Phase 3
only requires dimensions weighted above 0.2. So damaging only the expression can't move an
expression score. It is still run, as a specificity check: a rewrite that keeps every idea
should move no content score. It is reported separately and left out of attribution.

Bases are the reference answers of the reviewed non-creative questions, plus two golden good
answers. Each perturbation is checked in code, then read by hand; `review.json` drops the ones
that didn't do what they claim.
"""

import json
import re
import sqlite3
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from eval_engine.config import REPO_ROOT
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.base import ProviderError, QuotaExhausted
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.schemas.common import Dimension, TaskType
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore, connect
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import golden

PERTURB_DIR = REPO_ROOT / "experiments" / "7_validation" / "perturb"
ACCEPTED_FILE = REPO_ROOT / "experiments" / "3_generation" / "accepted.json"
GOLDEN_BASES = ("cell-good", "balloon-good")
CONTENT_KINDS = ("completeness", "correctness", "reasoning")
KINDS = (*CONTENT_KINDS, "expression")
ATTEMPTS = 2
ATTRIBUTION_TARGET = 0.70  # plan Phase 7 gate, overall

INSTRUCTIONS = {
    # First run: deleting one sentence often left the same content stated elsewhere (good
    # answers repeat themselves), so 17 of 24 owed no drop. Remove it everywhere.
    "completeness": (
        "Remove the content named below from the answer completely: it may be stated more than "
        "once, so remove every sentence or phrase that states it, until the answer no longer "
        "does this at all. Don't add anything; join the rest so it still reads naturally."
    ),
    # First run: 17 of 18 edits broke the link in one sentence while another still stated it
    # (external review of the human set, then re-audit), so the judge was right to credit them.
    "reasoning": (
        "Break the reasoning named below everywhere it appears. Keep the claims themselves, but "
        "after your edit the answer must not say, in any sentence, that one leads to, causes or "
        "supports the other: replace every such because/so/therefore link (and any summary "
        "sentence that restates it) with an unrelated reason or a coincidence. If the named "
        "part is a reason for a position, replace that reason, and any other sentence giving it, "
        "with one that has no bearing on the position. Keep the facts true."
    ),
    "correctness": (
        "Change exactly one fact so that it becomes clearly false (a wrong cause, name, number, "
        "direction or definition) and keep the rest true. Write the false fact as confidently "
        "as the rest."
    ),
    "expression": (
        "Rewrite the whole answer with poor expression: run-on sentences, clumsy word order, "
        "repeated words, a few misspellings. Keep every idea, fact and reasoning step exactly, "
        "and add or remove none."
    ),
}


class Perturbation(BaseModel):
    perturbed: str
    change: str


@dataclass
class Base:
    base_id: str
    question_id: str
    task_type: str
    answer: str


@dataclass
class Item:
    item_id: str
    base_id: str
    question_id: str
    kind: str
    target: str | None  # the criterion statement the change aims at
    target_dimension: str | None
    perturbed: str
    change: str
    problems: list[str] = field(default_factory=list)  # code checks still failing


def bases(conn: sqlite3.Connection) -> list[Base]:
    questions = QuestionStore(conn)
    out: list[Base] = []
    for entry in json.loads(ACCEPTED_FILE.read_text(encoding="utf-8")):
        q = questions.get(entry["question_id"])
        if q.task_type != TaskType.CREATIVE and q.reference_answer:
            out.append(
                Base(f"ref-{q.question_id}", q.question_id, q.task_type.value, q.reference_answer)
            )
    by_id = {g.id: g for g in golden.load_items()}
    for gid in GOLDEN_BASES:
        g = by_id[gid]
        out.append(Base(gid, g.question, questions.get(g.question).task_type.value, g.answer))
    return out


def _scratch(
    conn: sqlite3.Connection, question_id: str
) -> tuple[RubricStore, QuestionStore, EvaluationStore]:
    """A throwaway store with the v1 rubric, so nothing here touches the real stores."""
    real_q = QuestionStore(conn).get(question_id)
    s = connect(":memory:")
    RubricStore(s).save(RubricStore(conn).get(real_q.rubric_hash))
    QuestionStore(s).save(real_q)
    return RubricStore(s), QuestionStore(s), EvaluationStore(s)


def grade(
    client: LLMClient, conn: sqlite3.Connection, question_id: str, answer: str
) -> EvaluationTrace:
    rubrics, questions, evals = _scratch(conn, question_id)
    return evaluate(client, rubrics, questions, evals, question_id, answer, amend=False)


def baseline(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = PERTURB_DIR
) -> tuple[list[dict[str, Any]], str | None]:
    rows: list[dict[str, Any]] = []
    stopped = None
    for b in bases(conn):
        try:
            t = grade(client, conn, b.question_id, b.answer)
        except QuotaExhausted as e:
            stopped = str(e)
            break
        rows.append({**asdict(b), "trace": json.loads(t.model_dump_json())})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "baseline.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), "utf-8")
    return rows, stopped


def build(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = PERTURB_DIR
) -> dict[str, Any]:
    """Perturb every base in each applicable way, from its baseline. Local model; cached."""
    rubrics, questions = RubricStore(conn), QuestionStore(conn)
    items: list[Item] = []
    skipped: list[str] = []
    for row in json.loads((out_dir / "baseline.json").read_text(encoding="utf-8")):
        t = EvaluationTrace.model_validate(row["trace"])
        q = questions.get(row["question_id"])
        rubric = rubrics.get(q.rubric_hash)
        path = rubric.path(t.identified_path) if t.identified_path else rubric.paths[0]
        met = {v.criterion_id for v in t.verdicts if v.met}
        for kind in KINDS:
            target = None
            if kind in ("completeness", "reasoning"):
                candidates = [
                    c for c in path.criteria if c.dimension.value == kind and c.criterion_id in met
                ]
                if not candidates:
                    skipped.append(f"{row['base_id']}/{kind}: no met {kind} criterion")
                    continue
                target = sorted(candidates, key=lambda c: not c.core)[0].statement
            elif kind == "correctness" and t.errors:
                skipped.append(f"{row['base_id']}/{kind}: the base already has a listed error")
                continue
            item = _perturb(client, q.text, row["answer"], kind, target)
            items.append(
                Item(
                    f"{row['base_id']}/{kind}",
                    row["base_id"],
                    row["question_id"],
                    kind,
                    target,
                    kind if kind in CONTENT_KINDS else None,
                    item.perturbed if item else "",
                    item.change if item else "",
                    _checks(row["answer"], item.perturbed, kind) if item else ["no output"],
                )
            )
    body = {"items": [asdict(i) for i in items], "skipped": skipped}
    (out_dir / "items.json").write_text(json.dumps(body, indent=1, ensure_ascii=False), "utf-8")
    return {
        "items": len(items),
        "failing_checks": sum(bool(i.problems) for i in items),
        "skipped": len(skipped),
    }


def _perturb(
    client: LLMClient, question: str, answer: str, kind: str, target: str | None
) -> Perturbation | None:
    variables: dict[str, Any] = {
        "question": question,
        "answer": answer,
        "instruction": INSTRUCTIONS[kind],
        "target": target,
        "problems": [],
    }
    result = None
    for _ in range(ATTEMPTS):
        try:
            result = client.complete("perturber", "perturb", variables, Perturbation).value
        except (ProviderError, StructuredOutputError):
            return result
        problems = _checks(answer, result.perturbed, kind)
        if not problems:
            return result
        variables["problems"] = problems
    return result


_WORD = re.compile(r"[a-z0-9]+")


def _checks(original: str, perturbed: str, kind: str) -> list[str]:
    """Cheap guards; the hand check decides. A deletion must shorten the answer, an edit must
    keep most of it, and an expression rewrite must keep its content words."""
    a, b = _WORD.findall(original.lower()), _WORD.findall(perturbed.lower())
    if not b or a == b:
        return ["the answer is unchanged"]
    kept = len(set(w for w in a if len(w) > 4) & set(b)) / max(1, len({w for w in a if len(w) > 4}))
    if kind == "completeness" and len(b) >= len(a):
        return ["nothing was deleted; delete the named part"]
    if kind in ("correctness", "reasoning") and not 0.7 <= len(b) / len(a) <= 1.3:
        return ["change only the named part; the rest must stay the same"]
    if kind == "expression" and kept < 0.75:
        return ["keep the same content words; change only how it is expressed"]
    if kind != "completeness" and kept < 0.6:
        return ["too much of the answer was rewritten"]
    return []


def load_items(out_dir: Path = PERTURB_DIR) -> list[Item]:
    raw = json.loads((out_dir / "items.json").read_text(encoding="utf-8"))["items"]
    review_file = out_dir / "review.json"
    review = json.loads(review_file.read_text(encoding="utf-8")) if review_file.exists() else {}
    items = []
    for r in raw:
        decision = review.get(r["item_id"], {})
        if decision.get("drop") or r["problems"]:
            continue
        for before, after in decision.get("replace", []):
            # Wording fixes from review that aren't the injected change (a wrong-physics
            # sentence inherited from the base, an orphan "Another ..." after a deletion).
            if before not in r["perturbed"]:
                raise ValueError(f"{r['item_id']}: review replacement not found: {before!r}")
            r = {**r, "perturbed": r["perturbed"].replace(before, after)}
        items.append(Item(**r))
    return items


def run(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = PERTURB_DIR
) -> tuple[list[dict[str, Any]], str | None]:
    base_scores = {
        r["base_id"]: EvaluationTrace.model_validate(r["trace"]).dimension_scores
        for r in json.loads((out_dir / "baseline.json").read_text(encoding="utf-8"))
    }
    rows: list[dict[str, Any]] = []
    stopped = None
    for item in load_items(out_dir):
        try:
            t = grade(client, conn, item.question_id, item.perturbed)
        except QuotaExhausted as e:
            stopped = str(e)
            break
        before = base_scores[item.base_id]
        drops = {
            d.value: round(before[d] - t.dimension_scores[d], 6)
            for d in before
            if d in t.dimension_scores
        }
        rows.append(
            {"item_id": item.item_id, "kind": item.kind, "drops": drops, "errors": len(t.errors)}
        )
    (out_dir / "results.json").write_text(json.dumps(rows, indent=1), "utf-8")
    return rows, stopped


def attributed(drops: dict[str, float]) -> str:
    """The dimension with the largest drop; 'none' if nothing dropped, 'tie' if not unique."""
    top = max(drops.values(), default=0.0)
    if top <= 0:
        return "none"
    leaders = [d for d, v in drops.items() if v == top]
    return leaders[0] if len(leaders) == 1 else "tie"


def report(rows: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    content = [r for r in rows if r["kind"] in CONTENT_KINDS]
    lines = [
        "| Injected | n | Detected (target drops) | Attributed (target drops most) |",
        "|---|---|---|---|",
    ]
    summary: dict[str, Any] = {}
    for kind in CONTENT_KINDS:
        group = [r for r in content if r["kind"] == kind]
        det = sum(r["drops"].get(kind, 0) > 0 for r in group)
        att = sum(attributed(r["drops"]) == kind for r in group)
        summary[kind] = {"n": len(group), "detected": det, "attributed": att}
        lines.append(
            f"| {kind} | {len(group)} | {_pct(det, len(group))} | {_pct(att, len(group))} |"
        )
    att_all = sum(attributed(r["drops"]) == r["kind"] for r in content)
    summary["overall"] = {"n": len(content), "attributed": att_all}
    passed = bool(content) and att_all / len(content) >= ATTRIBUTION_TARGET
    lines += [
        f"| **overall** | {len(content)} | | **{_pct(att_all, len(content))}** |",
        "",
        f"Gate (attribution >= {ATTRIBUTION_TARGET:.0%} overall): {'PASS' if passed else 'FAIL'}",
        "",
        "Confusion (rows injected, columns attributed):",
        "",
    ]
    cols = [*[d.value for d in Dimension if d != Dimension.EXPRESSION], "tie", "none"]
    lines += ["| injected | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for kind in CONTENT_KINDS:
        group = [r for r in content if r["kind"] == kind]
        cells = [str(sum(attributed(r["drops"]) == c for r in group)) for c in cols]
        lines.append(f"| {kind} | " + " | ".join(cells) + " |")
    expr = [r for r in rows if r["kind"] == "expression"]
    still = sum(all(v <= 0 for v in r["drops"].values()) for r in expr)
    summary["expression_unmoved"] = {"n": len(expr), "unmoved": still}
    lines += [
        "",
        f"Expression only (specificity, not attribution): no content score dropped on "
        f"{_pct(still, len(expr))}.",
    ]
    summary["gate_passed"] = passed
    return "\n".join(lines), summary


def _pct(k: int, n: int) -> str:
    return f"{k}/{n} ({k / n:.0%})" if n else "no items"
