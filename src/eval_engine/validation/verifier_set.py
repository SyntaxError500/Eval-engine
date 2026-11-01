"""Phase 5 verifier test set (design doc §14): proposals whose validity is known in advance.

Positive: a valid approach the rubric doesn't list. Negative: (a) fluent nonsense, (b) right
conclusion by invalid reasoning, (c) restatement of an existing path, (d) a real approach with a
hole, and a class the design doesn't list: confident misconceptions, because the invented
mechanisms in (a) turned out too absurd to test the costly error on their own. Every item must
pass the same code checks a real proposal has to pass, so the verifier sees what it would see in
production.

The negatives are written by a model and every valid item is hand-curated (`curated.yaml`): on
hand check, 10 of the 17 "valid" items the model wrote were sub-cases of a listed path or refused
the question's forced choice. Those stay in the set under their true class.

Labels start as the author's intent. `review.json` holds the decisions of the hand and external
reviews, which override them: {"<item_id>": {"drop": true} | {"kind": "..."}, ...}.
"""

import json
import re
import sqlite3
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field

from eval_engine.amendment.propose import as_solution_path
from eval_engine.amendment.verify import verify
from eval_engine.config import REPO_ROOT, load_weights
from eval_engine.evaluation.aggregate import load_bands
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.generation.consistency import check_path, required_dimensions
from eval_engine.providers.base import QuotaExhausted
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.schemas.amendment import Framing, ProposedPath
from eval_engine.schemas.common import SINGLE_PATH_SHAPES
from eval_engine.schemas.rubric import Rubric
from eval_engine.storage import RubricStore, connect
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import golden

VERIFIER_DIR = REPO_ROOT / "experiments" / "5_verifier"
ACCEPTED_FILE = REPO_ROOT / "experiments" / "3_generation" / "accepted.json"
CURATED_FILE = VERIFIER_DIR / "curated.yaml"
AUTHOR_ATTEMPTS = 3
FRAMINGS: tuple[Framing, Framing] = ("adversarial", "neutral")
THRESHOLDS = (0.3, 0.4, 0.5, 0.6, 0.7)

POSITIVE = "valid_unlisted"
KINDS: dict[str, str] = {
    "nonsense": (
        "Write a path that is confident, fluent and wrong: its criteria state false facts or "
        "a mechanism that does not exist, though a non-expert might believe them. Give it a "
        "plausible name; it must read as seriously as a valid path, with no joke or absurdity."
    ),
    "invalid_reasoning": (
        "Write a path that reaches a defensible conclusion by reasoning that does not "
        "establish it: for example one event following another taken as cause and effect, a "
        "conclusion resting on itself, or a true premise that has no bearing on the "
        "conclusion. Its criteria state that bad step plainly as the argument, as if it were "
        "sound. Its individual facts must be true."
    ),
    "restatement": (
        "Take one listed path and write it again as if it were a new approach: same central "
        "argument or explanation, different words, with a new name of its own. Name the "
        "listed path in note."
    ),
    "holed": (
        "Write a real approach, different from the listed paths, whose statements are all "
        "true, but where the path's own criteria leave a hole: an answer could meet every "
        "criterion and still lack a step the approach needs, or skip part of what the "
        "question asks. The criteria must not ask for the missing thing. If you cannot "
        "write this honestly, set possible to false."
    ),
}

MISCONCEPTION = "misconception"  # hand-written; gated with nonsense, as the costliest error
NEGATIVE_KINDS = (*KINDS, MISCONCEPTION)
FALSE_ACCEPT_GATE = 0.10  # plan Phase 5: at most this rate on confident wrong proposals
GATE_KINDS = ("nonsense", MISCONCEPTION)

# A real proposer believes in its path. Text that names its own flaw makes the verifier's job
# trivial, and the first author run did so in most negatives ("employs circular reasoning").
_LEAK = re.compile(
    r"\b(circular\w*|fallac\w*|post hoc|pseudo\S*|paraphras\w*|restat\w*|rephras\w*|"
    r"invalid\w*|nonsense|fabricat\w*|fictitious|made-up|fake|flaw\w*|correlat\w*|"
    r"non-causal|omit\w*|incomplete|unrelated|irrelevant|fails? to|leaves? out|without|"
    r"synonym\w*|vocabulary|terminology|phrasing)\b",
    re.IGNORECASE,
)


class AuthoredItem(ProposedPath):
    possible: bool
    justification: str
    answer: str
    note: str = Field(description="For the human checker; why this item is of the stated kind")


@dataclass
class Item:
    item_id: str
    question_id: str
    kind: str
    path: dict[str, Any]
    justification: str
    answer: str
    note: str

    @property
    def valid(self) -> bool:
        return self.kind == POSITIVE


REVIEW_INTRO = (
    "Each item is a proposed new rubric path. The verifier is scored against the class given here,",
    "so a wrong label makes a wrong result. For every item, please say whether its class is right",
    "and give a corrected class or a reason to drop it if not. Results are left out on purpose.",
    "",
    "- **valid_unlisted**: factually sound, does what the question asks, and is not a listed path",
    "  or a narrower case of one.",
    "- **nonsense**: rests on an invented mechanism or false facts.",
    "- **misconception**: a common false belief, stated confidently.",
    "- **invalid_reasoning**: the reasoning does not establish the conclusion.",
    "- **restatement**: a listed path in other words, or a narrower case of it.",
    "- **holed**: real, but the path could be fully met while something needed is missing.",
    "",
    "Only the path and the justification reach the verifier. The learner answer is used to test",
    "the trigger, and the last field of each item is for you.",
)


def multi_path_questions(conn: sqlite3.Connection) -> list[tuple[str, Rubric]]:
    """Reviewed questions whose rubric can take another path. The frozen v1 rubric, so that
    an accepted amendment elsewhere can't change this experiment."""
    rubrics, questions = RubricStore(conn), QuestionStore(conn)
    accepted = json.loads(ACCEPTED_FILE.read_text(encoding="utf-8"))
    out = []
    for entry in accepted:
        q = questions.get(entry["question_id"])
        rubric = rubrics.get(q.rubric_hash)
        if rubric.shape not in SINGLE_PATH_SHAPES:
            out.append((q.question_id, rubric))
    return out


def _author(
    client: LLMClient, rubric: Rubric, kind: str, weights: dict[str, dict[str, float]]
) -> tuple[AuthoredItem | None, list[str]]:
    variables: dict[str, Any] = {
        "question": rubric.question,
        "task_type": rubric.task_type.value,
        "required_dimensions": sorted(required_dimensions(rubric.task_type, weights)),
        "paths": [p.model_dump(mode="json") for p in rubric.paths],
        "kind": kind,
        "instruction": KINDS[kind],
        "problems": [],
    }
    problems: list[str] = []
    for _ in range(AUTHOR_ATTEMPTS):
        res = client.complete("verifier_set_author", "verifier_set_author", variables, AuthoredItem)
        item = res.value
        if not item.possible:
            return None, ["author says this kind is not possible for this question"]
        problems = check_path(rubric, as_solution_path(rubric, item), weights) + _leaks(item)
        if not problems:
            return item, []
        variables["problems"] = problems
    return None, problems


def _leaks(item: AuthoredItem) -> list[str]:
    fields = [item.description, item.justification]
    fields += [t for c in item.criteria for t in (c.statement, c.evidence_hint)]
    found = sorted({m.lower() for text in fields for m in _LEAK.findall(text)})
    if not found:
        return []
    return [
        f"the path mentions its own flaw ({', '.join(found)}); a proposer believes its path is "
        "valid, so state the content as sound and name the flaw only in note"
    ]


def load_curated(rubrics: dict[str, Rubric], path: Path = CURATED_FILE) -> list[Item]:
    """Hand-checked items, held to the same code checks as a real proposal."""
    weights = load_weights()
    items = []
    for raw in yaml.safe_load(path.read_text(encoding="utf-8"))["items"]:
        rubric = rubrics[raw["question_id"]]
        proposed = ProposedPath(description=raw["description"], criteria=raw["criteria"])
        solution = as_solution_path(rubric, proposed)
        problems = check_path(rubric, solution, weights)
        if problems:
            raise ValueError(f"curated item {raw['item_id']}: {problems}")
        items.append(
            Item(
                raw["item_id"],
                raw["question_id"],
                raw["kind"],
                solution.model_dump(mode="json"),
                raw["justification"],
                raw["answer"],
                raw["note"],
            )
        )
    return items


def build(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = VERIFIER_DIR
) -> dict[str, Any]:
    """Author the negatives and add the curated items. Resumable: replies come from the cache."""
    weights = load_weights()
    questions = multi_path_questions(conn)
    items = load_curated(dict(questions))
    gaps: list[dict[str, Any]] = []
    stopped = None
    for qid, rubric in questions:
        for kind in KINDS:
            try:
                authored, problems = _author(client, rubric, kind, weights)
            except QuotaExhausted as e:
                stopped = str(e)
                break
            except StructuredOutputError as e:
                authored, problems = None, [str(e)[:300]]
            if authored is None:
                gaps.append({"question_id": qid, "kind": kind, "problems": problems})
                continue
            items.append(
                Item(
                    f"{qid}-{kind}",
                    qid,
                    kind,
                    as_solution_path(rubric, authored).model_dump(mode="json"),
                    authored.justification,
                    authored.answer,
                    authored.note,
                )
            )
        if stopped:
            break
    out_dir.mkdir(parents=True, exist_ok=True)
    body = {"items": [asdict(i) for i in items], "gaps": gaps}
    (out_dir / "items.json").write_text(
        json.dumps(body, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    return {"items": len(items), "gaps": len(gaps), "stopped": stopped}


def load_items(out_dir: Path = VERIFIER_DIR) -> list[Item]:
    """The set after review: dropped items removed, relabelled items moved."""
    raw = json.loads((out_dir / "items.json").read_text(encoding="utf-8"))["items"]
    review_file = out_dir / "review.json"
    review = json.loads(review_file.read_text(encoding="utf-8")) if review_file.exists() else {}
    items = []
    for entry in raw:
        decision = review.get(entry["item_id"], {})
        if decision.get("drop"):
            continue
        items.append(Item(**{**entry, "kind": decision.get("kind", entry["kind"])}))
    return items


def run(
    client: LLMClient,
    conn: sqlite3.Connection,
    framing: Framing,
    out_dir: Path = VERIFIER_DIR,
) -> tuple[list[dict[str, Any]], str | None]:
    """Verify every item under one framing, single-threaded because of Groq's output-token cap.
    Resumable from the cache."""
    rubrics = dict(multi_path_questions(conn))
    rows: list[dict[str, Any]] = []
    stopped = None
    for item in load_items(out_dir):
        rubric = rubrics[item.question_id]
        path = as_solution_path(rubric, ProposedPath.model_validate(_proposed(item)))
        try:
            res = verify(client, rubric, path, item.justification, framing)
        except QuotaExhausted as e:
            stopped = str(e)
            break
        except StructuredOutputError as e:
            rows.append({"item_id": item.item_id, "kind": item.kind, "error": str(e)[:300]})
            continue
        rows.append(
            {
                "item_id": item.item_id,
                "kind": item.kind,
                "accepted": res.value.accepted,
                "failure_type": res.value.failure_type,
                "reasons": res.value.reasons,
            }
        )
    results = out_dir / "results"
    results.mkdir(parents=True, exist_ok=True)
    (results / f"{framing}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )
    return rows, stopped


def _proposed(item: Item) -> dict[str, Any]:
    return {"description": item.path["description"], "criteria": item.path["criteria"]}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% interval for a proportion. Holds up at 0/n and n/n, where a bootstrap collapses."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / d
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, mid - half), min(1.0, mid + half))


def _rate(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({k / n:.0%}, CI {lo:.0%}-{hi:.0%})" if n else "no items"


def report(out_dir: Path = VERIFIER_DIR) -> tuple[str, dict[str, dict[str, Any]]]:
    lines = ["# Verifier test set results", ""]
    summary: dict[str, dict[str, Any]] = {}
    for framing in FRAMINGS:
        path = out_dir / "results" / f"{framing}.jsonl"
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        decided = [r for r in rows if "error" not in r]
        positives = [r for r in decided if r["kind"] == POSITIVE]
        negatives = [r for r in decided if r["kind"] != POSITIVE]
        tp = sum(r["accepted"] for r in positives)
        fp = sum(r["accepted"] for r in negatives)
        lines += [
            f"## {framing}",
            "",
            f"{len(decided)} items decided, {len(rows) - len(decided)} with errors.",
            "",
            f"- Recall on valid approaches: {_rate(tp, len(positives))}",
            f"- Precision of acceptances: {_rate(tp, tp + fp)}",
            "",
            "| class | rejected | accepted (false accept) | failure types given |",
            "|---|---|---|---|",
        ]
        summary[framing] = {"tp": tp, "fp": fp, "positives": len(positives)}
        for kind in NEGATIVE_KINDS:
            group = [r for r in decided if r["kind"] == kind]
            accepted = sum(r["accepted"] for r in group)
            types = Counter(r["failure_type"] or "none" for r in group if not r["accepted"])
            type_text = ", ".join(f"{t} {n}" for t, n in types.most_common())
            lines.append(
                f"| {kind} | {_rate(len(group) - accepted, len(group))} "
                f"| {_rate(accepted, len(group))} | {type_text} |"
            )
            summary[framing][kind] = {"accepted": accepted, "n": len(group)}
        gated = [r for r in decided if r["kind"] in GATE_KINDS]
        wrong = sum(r["accepted"] for r in gated)
        passed = bool(gated) and wrong / len(gated) <= FALSE_ACCEPT_GATE
        summary[framing]["gate_passed"] = passed
        lines += [
            "",
            f"False accepts on confident wrong proposals: {_rate(wrong, len(gated))}, gate "
            f"<= {FALSE_ACCEPT_GATE:.0%}: {'PASS' if passed else 'FAIL'}",
            "",
        ]
    return "\n".join(lines), summary


def calibrate(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = VERIFIER_DIR
) -> tuple[str, list[dict[str, Any]]]:
    """Judge the set's answers (no amendment) and sweep the confidence threshold over them and
    the golden set. Ordinary answers should stay below the trigger; answers taking an
    unlisted line should fire. Cached, so a rerun is free."""
    rubrics, questions, evals = RubricStore(conn), QuestionStore(conn), EvaluationStore(conn)
    rows: list[dict[str, Any]] = []
    try:
        for item in load_items(out_dir):
            t = evaluate(
                client, rubrics, questions, evals, item.question_id, item.answer, amend=False
            )
            rows.append(
                _conf_row(item.kind, item.item_id, t.path_confidences, t.addresses_question)
            )
    except QuotaExhausted as e:
        return f"Stopped after {len(rows)} items: {e}. Rerun later to resume.", rows
    for g in golden.load_items():
        t = evaluate(client, rubrics, questions, evals, g.question, g.answer, amend=False)
        if t.task_type.value in ("explanatory", "analytical"):  # amendment can't fire elsewhere
            rows.append(
                _conf_row(f"golden_{g.kind}", g.id, t.path_confidences, t.addresses_question)
            )
    (out_dir / "calibration.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return _sweep(rows), rows


def _conf_row(kind: str, item_id: str, confidences: Any, addresses: bool | None) -> dict[str, Any]:
    conf = max((p.confidence for p in confidences), default=0.0)
    return {"kind": kind, "item_id": item_id, "confidence": conf, "addresses": addresses}


def _sweep(rows: list[dict[str, Any]]) -> str:
    groups = sorted({r["kind"] for r in rows})
    head = " | ".join(f"< {t}" for t in THRESHOLDS)
    lines = [f"| group | n | {head} |", "|---|---|" + "---|" * len(THRESHOLDS)]
    for g in groups:
        members = [r for r in rows if r["kind"] == g]
        cells = [
            str(sum(r["confidence"] < t and r["addresses"] is True for r in members))
            for t in THRESHOLDS
        ]
        lines.append(f"| {g} | {len(members)} | {' | '.join(cells)} |")
    return "\n".join(lines)


def end_to_end(
    client: LLMClient, conn: sqlite3.Connection, out_dir: Path = VERIFIER_DIR
) -> tuple[str, str | None]:
    """The whole chain on answers that trigger amendment: can a wrong answer earn its own path?
    The verifier test above is handed its paths; here the proposer writes them from the answer.
    Each item gets a throwaway store holding the v1 rubric, so an accepted path can't touch the
    real rubrics or change the next item. Replies still go through the shared cache."""
    real_rubrics, real_questions = RubricStore(conn), QuestionStore(conn)
    threshold = load_bands().amendment_confidence_threshold
    calibration = json.loads((out_dir / "calibration.json").read_text(encoding="utf-8"))
    due = {
        r["item_id"] for r in calibration if r["addresses"] is True and r["confidence"] < threshold
    }
    cases = [(i.item_id, i.kind, i.question_id, i.answer) for i in load_items(out_dir)]
    cases = [c for c in cases if c[0] in due]
    cases += [
        (g.id, f"golden_{g.kind}", g.question, g.answer)
        for g in golden.load_items()
        if g.id in due and real_questions.get(g.question).task_type.value != "factual"
    ]
    rows: list[dict[str, Any]] = []
    stopped = None
    for item_id, kind, question_id, answer in cases:
        scratch = connect(":memory:")
        rubrics, questions = RubricStore(scratch), QuestionStore(scratch)
        q = real_questions.get(question_id)
        rubrics.save(real_rubrics.get(q.rubric_hash))
        questions.save(q)
        try:
            t = evaluate(client, rubrics, questions, EvaluationStore(scratch), question_id, answer)
        except QuotaExhausted as e:
            stopped = str(e)
            break
        if t.amendment_error and "QuotaExhausted" in t.amendment_error:
            stopped = t.amendment_error
            break
        proposed = json.loads(t.amendment_proposal) if t.amendment_proposal else None
        outcome = (
            "accepted"
            if t.final_rubric_source == "amendment"
            else "verifier rejected"
            if t.verifier_verdict is False
            else "proposer declined"
            if proposed and not proposed["is_new_valid_approach"]
            else "failed checks"
            if t.divergence_reason
            else "error"
        )
        rows.append(
            {
                "item_id": item_id,
                "kind": kind,
                "outcome": outcome,
                "failure_type": t.verifier_failure_type,
                "overall": t.overall_score,
                "reason": t.divergence_reason or t.verifier_reasoning or t.amendment_error,
            }
        )
    (out_dir / "e2e.json").write_text(
        json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    return _e2e_table(rows), stopped


def _e2e_table(rows: list[dict[str, Any]]) -> str:
    outcomes = ("accepted", "verifier rejected", "proposer declined", "failed checks", "error")
    lines = ["| class | n | " + " | ".join(outcomes) + " |", "|---|---|" + "---|" * len(outcomes)]
    for kind in sorted({r["kind"] for r in rows}):
        group = [r for r in rows if r["kind"] == kind]
        counts = Counter(r["outcome"] for r in group)
        cells = " | ".join(str(counts[o]) for o in outcomes)
        lines.append(f"| {kind} | {len(group)} | {cells} |")
    return "\n".join(lines)


def review_sheet(conn: sqlite3.Connection, out_dir: Path = VERIFIER_DIR) -> str:
    """Markdown for the hand and external reviews, the one place the labels are shown."""
    rubrics = dict(multi_path_questions(conn))
    by_question: dict[str, list[Item]] = {}
    for item in load_items(out_dir):
        by_question.setdefault(item.question_id, []).append(item)
    review_file = out_dir / "review.json"
    review = json.loads(review_file.read_text(encoding="utf-8")) if review_file.exists() else {}
    lines = ["# Verifier test set review", "", *REVIEW_INTRO, ""]
    for n, (qid, items) in enumerate(by_question.items(), start=1):
        r = rubrics[qid]
        lines += [f"## Q{n} ({r.task_type.value}, {qid})", "", r.question, "", "Listed paths:"]
        for p in r.paths:
            lines.append(f"- **{p.path_id}**: {p.description}")
        lines.append("")
        for item in items:
            lines += [f"### {item.item_id}", "", f"**Intended class:** {item.kind}", ""]
            why = review.get(item.item_id, {}).get("why")
            if why:
                lines += [f"**Changed on hand check:** {why}", ""]
            lines.append(f"**Path:** {item.path['description']}")
            lines += [f"- {c['statement']}" for c in item.path["criteria"]]
            lines += [
                "",
                f"**Proposer's justification:** {item.justification}",
                "",
                f"**Learner answer:** {item.answer}",
                "",
                f"**Why it is this class:** {item.note}",
                "",
            ]
    dropped = [(i, d) for i, d in review.items() if d.get("drop")]
    if dropped:
        lines += ["## Dropped on hand check", ""]
        lines += [f"- {i}: {d.get('why', '')}" for i, d in dropped]
    return "\n".join(lines)
