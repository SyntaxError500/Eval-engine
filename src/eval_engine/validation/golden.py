"""Phase 4 golden set: hand-written answers with expected score ranges per dimension.

`run` grades every item live and writes a fixture holding each item's raw judge reply plus the
question and rubric it was graded against. `replay` feeds those recorded replies back through
the real pipeline with a scripted provider, so CI checks the post-judge code (evidence check,
path repair, aggregation) against the same inputs without a network call.
"""

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from eval_engine.config import REPO_ROOT
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.question import Question
from eval_engine.schemas.rubric import Rubric
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore

GOLDEN_DIR = REPO_ROOT / "experiments" / "4_eval"
GOLDEN_FILE = GOLDEN_DIR / "golden.yaml"
FIXTURE_FILE = GOLDEN_DIR / "golden_fixture.json"


@dataclass
class GoldenItem:
    id: str
    question: str
    kind: str
    answer: str
    expect: dict[str, tuple[float, float]]
    path: str | None = None
    overlap: bool | None = None


@dataclass
class Outcome:
    item: GoldenItem
    scores: dict[str, float]
    path: str | None
    overlap: list[str]
    downgrades: list[str]
    contradictions: list[str]
    count_overrides: list[str]
    n_errors: int
    misses: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.misses


def load_items(path: Path = GOLDEN_FILE) -> list[GoldenItem]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    items = []
    for raw in data["items"]:
        expect = {d: (float(lo), float(hi)) for d, (lo, hi) in raw["expect"].items()}
        items.append(
            GoldenItem(
                id=raw["id"],
                question=raw["question"],
                kind=raw["kind"],
                answer=raw["answer"],
                expect=expect,
                path=raw.get("path"),
                overlap=raw.get("overlap"),
            )
        )
    return items


def check(item: GoldenItem, trace: EvaluationTrace) -> Outcome:
    scores = {d.value: s for d, s in trace.dimension_scores.items()}
    out = Outcome(
        item,
        scores,
        trace.identified_path,
        trace.obvious_overlap,
        trace.evidence_downgrades,
        trace.contradiction_downgrades,
        trace.count_overrides,
        len(trace.errors),
    )
    for dim, (lo, hi) in item.expect.items():
        got = scores.get(dim)
        if got is None:
            # "not assessed" only satisfies a range that allows zero
            if lo > 0:
                out.misses.append(f"{dim} not assessed, expected [{lo}, {hi}]")
        elif not lo - 1e-9 <= got <= hi + 1e-9:
            out.misses.append(f"{dim} {got:.2f} outside [{lo}, {hi}]")
    if item.path and trace.identified_path != item.path:
        out.misses.append(f"path {trace.identified_path}, expected {item.path}")
    if item.overlap is not None and bool(trace.obvious_overlap) != item.overlap:
        out.misses.append(f"obvious overlap {trace.obvious_overlap}, expected {item.overlap}")
    return out


def _judge_text(conn: sqlite3.Connection, call_id: str) -> str:
    row = conn.execute(
        "SELECT rc.text FROM llm_calls c JOIN response_cache rc ON rc.request_key = c.request_key"
        " WHERE c.call_id = ?",
        (call_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"no cached judge reply for call {call_id}")
    return str(row[0])


def run(
    client: LLMClient,
    conn: sqlite3.Connection,
    items: list[GoldenItem],
    fixture: Path = FIXTURE_FILE,
) -> list[Outcome]:
    """Grade every item live (single vote) and record the fixture. Cached replies are reused,
    so a rerun after a quota stop only pays for the missing items."""
    rubrics, questions, evals = RubricStore(conn), QuestionStore(conn), EvaluationStore(conn)
    outcomes: list[Outcome] = []
    recorded: dict[str, Any] = {"questions": {}, "items": {}}
    for item in items:
        trace = evaluate(client, rubrics, questions, evals, item.question, item.answer)
        q = questions.get(item.question)
        recorded["questions"][q.question_id] = {
            "question": json.loads(q.model_dump_json()),
            "rubric": json.loads(rubrics.latest(q.rubric_id).model_dump_json()),
        }
        o = check(item, trace)
        recorded["items"][item.id] = {
            "judge_reply": _judge_text(conn, trace.call_ids[0]),
            "scores": o.scores,
            "path": o.path,
            "passed": o.passed,
        }
        outcomes.append(o)
    fixture.write_text(json.dumps(recorded, indent=1, ensure_ascii=False), encoding="utf-8")
    return outcomes


def load_fixture(conn: sqlite3.Connection, fixture: Path = FIXTURE_FILE) -> dict[str, Any]:
    """Store the fixture's questions and rubrics in `conn`; return the recorded items."""
    data: dict[str, Any] = json.loads(fixture.read_text(encoding="utf-8"))
    rubrics, questions = RubricStore(conn), QuestionStore(conn)
    for entry in data["questions"].values():
        r = Rubric.model_validate(entry["rubric"])
        rubrics.save(r)
        q = Question.model_validate(entry["question"])
        # A fixture rubric may be an amended version; point the question at the stored one.
        questions.save(q.model_copy(update={"rubric_hash": r.hash}))
    items: dict[str, Any] = data["items"]
    return items


def report(outcomes: list[Outcome]) -> str:
    lines = ["| item | kind | result | scores | notes |", "|---|---|---|---|---|"]
    for o in outcomes:
        scores = ", ".join(f"{d} {s:.2f}" for d, s in o.scores.items())
        notes = "; ".join(o.misses)
        if o.downgrades:
            notes += f" (evidence downgrades: {', '.join(o.downgrades)})"
        if o.contradictions:
            notes += f" (met on a flagged error: {', '.join(o.contradictions)})"
        if o.count_overrides:
            notes += f" (count decided in code: {', '.join(o.count_overrides)})"
        if o.n_errors:
            notes += f" ({o.n_errors} error(s) listed)"
        lines.append(
            f"| {o.item.id} | {o.item.kind} | {'pass' if o.passed else 'MISS'} | {scores} "
            f"| {notes.strip()} |"
        )
    n = sum(o.passed for o in outcomes)
    lines.append(f"\n{n}/{len(outcomes)} items within their expected ranges.")
    return "\n".join(lines)


def vote_study(
    client: LLMClient, conn: sqlite3.Connection, items: list[GoldenItem], votes: int = 3
) -> str:
    """D6: grade every item with the majority vote and compare with the recorded single vote.
    Only borderline items get extra (fresh, uncached) calls; the first vote is the cached one.
    Does not touch the fixture."""
    recorded = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))["items"]
    rubrics, questions, evals = RubricStore(conn), QuestionStore(conn), EvaluationStore(conn)
    lines = ["| item | single | majority | scores single -> majority |", "|---|---|---|---|"]
    revoted = changed = fixed = broke = 0
    for item in items:
        trace = evaluate(client, rubrics, questions, evals, item.question, item.answer, votes=votes)
        if trace.judge_votes == 1:
            continue
        revoted += 1
        o, rec = check(item, trace), recorded[item.id]
        moved = any(abs(o.scores.get(d, -1) - s) > 1e-9 for d, s in rec["scores"].items())
        changed += moved
        fixed += o.passed and not rec["passed"]
        broke += rec["passed"] and not o.passed
        fmt = ", ".join(f"{d} {s:.2f}" for d, s in rec["scores"].items())
        new = ", ".join(f"{d} {s:.2f}" for d, s in o.scores.items())
        lines.append(
            f"| {item.id} | {'pass' if rec['passed'] else 'MISS'} | "
            f"{'pass' if o.passed else 'MISS'} | {fmt} -> {new}{' (changed)' if moved else ''} |"
        )
    lines.append(
        f"\n{revoted}/{len(items)} items re-voted ({2 * revoted} extra calls at votes=3); "
        f"scores changed on {changed}; misses fixed {fixed}, passes broken {broke}."
    )
    return "\n".join(lines)
