"""Phase 7 step 3 (senior review): the perturbation set scored by a majority of 3 judge calls.

The judge flips 12% of labels between identical runs (Phase 2), so one run can't tell 18 from 20
attributed edits apart. Each base and each kept edit is graded with three calls, and each
criterion takes the majority verdict; extra calls never overwrite the cached first reply. The
human set is scored the same way. Every figure in the report is computed from the run files by
`report`, including the bookkeeping counts.

The rule is the one fixed before any run: an edit is attributed when its target dimension has
the unique largest drop. Counting ties is reported as a labelled secondary figure only.
"""

import json
import shutil
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.prompts import PromptRegistry
from eval_engine.providers.base import QuotaExhausted
from eval_engine.providers.client import LLMClient
from eval_engine.validation import perturb
from eval_engine.validation.verifier_set import wilson

VOTES = 3
V2_COMMIT = "score-answer-v2"  # tag on the last commit with score_answer v2


def v2_prompts(scratch: Path) -> PromptRegistry:
    """A prompt folder identical to the current one except `score_answer` at v2, from git."""
    folder = scratch / "prompts_v2"
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(REPO_ROOT / "prompts", folder)
    text = subprocess.run(
        ["git", "show", f"{V2_COMMIT}:prompts/score_answer.yaml"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    ).stdout
    (folder / "score_answer.yaml").write_text(text, encoding="utf-8")
    return PromptRegistry(folder)


def run(
    client: LLMClient, conn: sqlite3.Connection, label: str, out_dir: Path = perturb.PERTURB_DIR
) -> tuple[dict[str, Any], str | None]:
    """Majority-of-3 scores for every base and kept edit. Resumable: the file is rewritten as it
    goes and finished entries are skipped."""
    path = out_dir / f"maj3_{label}.json"
    done: dict[str, Any] = (
        json.loads(path.read_text(encoding="utf-8"))
        if path.exists()
        else {"bases": {}, "items": {}}
    )
    jobs = [("bases", b.base_id, b.question_id, b.answer) for b in perturb.bases(conn)]
    jobs += [("items", i.item_id, i.question_id, i.perturbed) for i in perturb.load_items(out_dir)]
    stopped = None
    for group, key, question_id, text in jobs:
        if key in done[group]:
            continue
        rubrics, questions, evals = perturb._scratch(conn, question_id)
        try:
            t = evaluate(
                client, rubrics, questions, evals, question_id, text,
                votes=VOTES, vote_all=True, amend=False,
            )  # fmt: skip
        except QuotaExhausted as e:
            stopped = str(e)
            break
        done[group][key] = {
            "scores": {d.value: s for d, s in t.dimension_scores.items()},
            "votes": t.judge_votes,
            "errors": len(t.errors),
        }
        path.write_text(json.dumps(done, indent=1), encoding="utf-8")
    return done, stopped


def drops(run_file: dict[str, Any], out_dir: Path = perturb.PERTURB_DIR) -> list[dict[str, Any]]:
    rows = []
    for item in perturb.load_items(out_dir):
        base = run_file["bases"].get(item.base_id)
        got = run_file["items"].get(item.item_id)
        if base is None or got is None:
            continue
        d = {
            k: round(v - got["scores"][k], 6)
            for k, v in base["scores"].items()
            if k in got["scores"]
        }
        rows.append({"item_id": item.item_id, "kind": item.kind, "drops": d})
    return rows


def bookkeeping(out_dir: Path = perturb.PERTURB_DIR) -> list[str]:
    body = json.loads((out_dir / "items.json").read_text(encoding="utf-8"))
    review = json.loads((out_dir / "review.json").read_text(encoding="utf-8"))
    items = body["items"]
    failing = [i for i in items if i["problems"]]
    dropped = [i for i in items if review.get(i["item_id"], {}).get("drop") and not i["problems"]]
    kept = perturb.load_items(out_dir)
    possible = len(perturb.KINDS) * len(
        {i["base_id"] for i in items} | {s.split("/")[0] for s in body["skipped"]}
    )
    by_kind = Counter(i.kind for i in kept)
    return [
        f"- Possible edits: {possible} ({len(perturb.KINDS)} per base).",
        f"- Skipped, the base met no criterion in that dimension: {len(body['skipped'])}.",
        f"- Generated: {len(items)} (each slot holds its latest version; a regenerated edit "
        "replaced the earlier one in place).",
        f"- Failing the code checks: {len(failing)}. Dropped on review: {len(dropped)}.",
        f"- Kept: {len(kept)} ({', '.join(f'{k} {n}' for k, n in sorted(by_kind.items()))}).",
        f"- Text fixes from review: {sum(bool(v.get('replace')) for v in review.values())}.",
    ]


def table(rows: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    lines = [
        "| Injected | n | Detected | Attributed, strict [95% CI] | Ties | Ties counted |",
        "|---|---|---|---|---|---|",
    ]
    out: dict[str, Any] = {}
    content = [r for r in rows if r["kind"] in perturb.CONTENT_KINDS]
    for kind in (*perturb.CONTENT_KINDS, "overall"):
        group = content if kind == "overall" else [r for r in content if r["kind"] == kind]
        n = len(group)
        hit = sum(perturb.attributed(r["drops"]) == r["kind"] for r in group)
        ties = sum(perturb.attributed(r["drops"]) == "tie" for r in group)
        det = sum(r["drops"].get(r["kind"], 0) > 0 for r in group)
        lo, hi = wilson(hit, n)
        out[kind] = {"n": n, "attributed": hit, "ties": ties, "detected": det}
        lines.append(
            f"| {kind} | {n} | {det} | {hit} ({hit / n:.0%}) [{lo:.0%}-{hi:.0%}] | {ties} | "
            f"{hit + ties} ({(hit + ties) / n:.0%}) |"
        )
    expr = [r for r in rows if r["kind"] == "expression"]
    unmoved = sum(all(v <= 0 for v in r["drops"].values()) for r in expr)
    out["expression_unmoved"] = {"n": len(expr), "unmoved": unmoved}
    lines.append(f"\nExpression only, no content score dropped: {unmoved}/{len(expr)}.")
    return lines, out


def report(out_dir: Path = perturb.PERTURB_DIR) -> tuple[str, dict[str, Any]]:
    lines = [
        "# Perturbation, majority of 3 judge calls",
        "",
        "## Bookkeeping",
        "",
        *bookkeeping(out_dir),
    ]
    summary: dict[str, Any] = {}
    for label in ("v3", "v2"):
        path = out_dir / f"maj3_{label}.json"
        if not path.exists():
            continue
        run_file = json.loads(path.read_text(encoding="utf-8"))
        rows = drops(run_file, out_dir)
        body, summary[label] = table(rows)
        not_full = {
            k: v["scores"] for k, v in run_file["bases"].items() if min(v["scores"].values()) < 1
        }
        lines += [
            "",
            f"## Judge {label} ({len(rows)} edits scored)",
            "",
            "Strict rule (fixed before any run): the target dimension has the unique largest drop.",
            "",
            *body,
            "",
            f"Bases below full marks: {not_full or 'none'}.",
        ]
    return "\n".join(lines), summary
