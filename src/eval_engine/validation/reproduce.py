"""Phase 9 exit gate: regenerate every validation report from cached responses, with one command,
and check each matches the committed version (`eval-engine reproduce`).

Rules:
- The client is offline: any response not in the cache raises `CacheMiss`, so a step that
  would need a live call fails instead of quietly taking a degradation path.
- Everything runs on a temporary copy of the database and of each experiment folder, so the
  real store and the committed reports are never written.
- A step passes when its regenerated report is identical to the committed one (whitespace at
  line ends aside).

Not regenerated, by nature: Phase 3 and 6 gates (human review sheets), and the Phase 8
degradation and discussion checks, which break providers or call models live on purpose.
Majority-of-3 votes are not in the response cache (extra votes are fresh calls); their traces
are committed (`engine_maj3.json`, `maj3_v*.json`) and the reports are recomputed from them.
"""

import difflib
import json
import shutil
import sqlite3
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from eval_engine.config import REPO_ROOT, AppConfig
from eval_engine.providers.client import LLMClient
from eval_engine.providers.factory import build_client
from eval_engine.storage import connect
from eval_engine.validation import (
    amendment_freq,
    corpus,
    golden,
    human_analysis,
    human_set,
    perturb,
    perturb_votes,
    pilot,
    verifier_set,
)

PHASE2_JUDGES = ["judge", "judge_candidate_qwen", "judge_candidate_local"]


@dataclass
class StepResult:
    name: str
    committed: Path
    ok: bool
    detail: str  # a diff excerpt, or the error


@dataclass
class _Ctx:
    client: LLMClient
    conn: sqlite3.Connection
    tmp: Path

    def copy(self, folder: Path) -> Path:
        dest = self.tmp / folder.relative_to(REPO_ROOT)
        if not dest.exists():
            shutil.copytree(folder, dest)
        return dest


def _phase2(ctx: _Ctx) -> str:
    text, _ = pilot.report(PHASE2_JUDGES, out_dir=ctx.copy(pilot.PILOT_DIR))
    return text


def _phase2_final(ctx: _Ctx) -> str:
    """The final judge run (rubric prompt v3) the Phase 2 decision rests on."""
    text, _ = pilot.report(["judge"], out_dir=ctx.copy(pilot.PILOT_DIR / "test_v3"))
    return text


def _golden(ctx: _Ctx) -> str:
    outcomes = golden.run(
        ctx.client, ctx.conn, golden.load_items(), fixture=ctx.tmp / "golden_fixture.json"
    )
    return golden.report(outcomes) + "\n"


def _verifier(ctx: _Ctx) -> str:
    text, _ = verifier_set.report(ctx.copy(verifier_set.VERIFIER_DIR))
    return text + "\n"


def _corpus(ctx: _Ctx) -> str:
    runs, stopped = corpus.run(ctx.client, ctx.conn, out_dir=ctx.tmp / "corpus")
    if stopped:
        raise RuntimeError(f"corpus run stopped: {stopped}")
    return corpus.report(runs) + "\n"


def _perturb_single(ctx: _Ctx) -> str:
    rows = json.loads((perturb.PERTURB_DIR / "results.json").read_text(encoding="utf-8"))
    text, _ = perturb.report(rows)
    return text + "\n"


def _perturb_maj3(ctx: _Ctx) -> str:
    text, _ = perturb_votes.report(ctx.copy(perturb.PERTURB_DIR))
    return text + "\n"


def _human(ctx: _Ctx) -> str:
    expected = human_analysis.expected_items(ctx.conn)
    grades = human_analysis.GRADES_DIR
    g1 = human_analysis.load_grades(grades / "grader1.csv", expected)
    g2 = human_analysis.load_grades(grades / "grader2.csv", expected)
    key = json.loads((human_set.HUMAN_DIR / "key.json").read_text(encoding="utf-8"))
    engine = human_analysis.engine_scores(
        ctx.client, ctx.conn, out_dir=ctx.copy(human_set.HUMAN_DIR)
    )
    criteria = human_analysis.criteria_by_hash(ctx.conn, engine)
    text, _ = human_analysis.analyse(key, g1, g2, expected, engine, criteria)
    return text + "\n"


def _amendment(ctx: _Ctx) -> str:
    return amendment_freq.report(ctx.conn)


STEPS: list[tuple[str, Path, Callable[[_Ctx], str]]] = [
    ("Phase 2 judge pilot, three judges", pilot.PILOT_DIR / "REPORT.md", _phase2),
    ("Phase 2 judge pilot, final run", pilot.PILOT_DIR / "test_v3" / "REPORT.md", _phase2_final),
    ("Phase 4 golden set", golden.GOLDEN_DIR / "golden_report.md", _golden),
    ("Phase 5 verifier", verifier_set.VERIFIER_DIR / "REPORT.md", _verifier),
    ("Phase 7 corpus", corpus.CORPUS_DIR / "REPORT.md", _corpus),
    ("Phase 7 perturbation (single)", perturb.PERTURB_DIR / "REPORT.md", _perturb_single),
    ("Phase 7 perturbation (majority of 3)", perturb.PERTURB_DIR / "REPORT_maj3.md", _perturb_maj3),
    ("Phase 7 human set", human_set.HUMAN_DIR / "REPORT.md", _human),
    (
        "Phase 9 amendment frequency",
        amendment_freq.OUT_DIR / "AMENDMENT_FREQUENCY.md",
        _amendment,
    ),
]


def _norm(text: str) -> list[str]:
    return [line.rstrip() for line in text.strip().splitlines()]


def compare(committed: str, regenerated: str) -> tuple[bool, str]:
    a, b = _norm(committed), _norm(regenerated)
    if a == b:
        return True, ""
    diff = difflib.unified_diff(a, b, "committed", "regenerated", n=1, lineterm="")
    return False, "\n".join(list(diff)[:40])


def run(db: Path, config: AppConfig, only: set[str] | None = None) -> list[StepResult]:
    results = []
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_name:
        tmp = Path(tmp_name)
        copy = tmp / "eval_engine.db"
        # A `with` block on a sqlite3 connection commits but doesn't close; on Windows an open
        # handle would keep the copy locked.
        src, dst = sqlite3.connect(db), sqlite3.connect(copy)
        try:
            src.backup(dst)  # a consistent copy, WAL included
        finally:
            src.close()
            dst.close()
        conn = connect(copy)
        ctx = _Ctx(build_client(config, conn, offline=True), conn, tmp)
        for name, committed, step in STEPS:
            if only and not any(o.lower() in name.lower() for o in only):
                continue
            try:
                ok, detail = compare(committed.read_text(encoding="utf-8"), step(ctx))
            except Exception as e:  # report every step, then fail overall
                ok, detail = False, f"{type(e).__name__}: {str(e)[:500]}"
            results.append(StepResult(name, committed, ok, detail))
        conn.close()
    return results


def report(results: list[StepResult]) -> str:
    lines = ["| Report | Regenerated from cache |", "|---|---|"]
    for r in results:
        lines.append(f"| {r.name} (`{r.committed.relative_to(REPO_ROOT).as_posix()}`) | "
                     f"{'identical' if r.ok else 'DIFFERENT'} |")  # fmt: skip
    for r in results:
        if not r.ok:
            lines += ["", f"## {r.name}", "", "```", r.detail, "```"]
    return "\n".join(lines)
