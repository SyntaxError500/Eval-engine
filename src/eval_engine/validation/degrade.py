"""Phase 8 exit gate: trigger each degradation path on the real system, one at a time.

Each check breaks one thing through configuration only, and runs the real service on a
throwaway database holding one reviewed question, so nothing reaches the real stores:

1. judge rate-limited: the judge's daily limit is set to 1, and today's use already exceeds it,
   so our own rate limiter refuses the call (the path a spent quota takes). Then the limit is
   restored and the queued answer is retried;
2. verifier down: the verifier points at a model the provider doesn't have, on an answer known
   to trigger amendment (the Phase 5 HPA-axis answer);
3. feedback model down: Ollama points at a closed port.
"""

import json
import os
import random
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT, AppConfig
from eval_engine.providers.factory import build_client
from eval_engine.service import EngineService
from eval_engine.storage import RubricStore, connect
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import verifier_set

DEGRADE_DIR = REPO_ROOT / "experiments" / "8_interface"
AMENDMENT_ITEM = "b850a615f22e-valid_hpa"  # triggers amendment (Phase 5 end to end)
PLAIN_ANSWER = (
    "When the air inside the balloon is heated it expands and becomes less dense than the "
    "cooler air outside. The denser outside air then pushes the balloon up with a buoyant "
    "force, so it rises."
)
BALLOON_QUESTION = "23575fb39cfd"


def _scratch(
    conn: sqlite3.Connection, question_id: str, tmp: Path
) -> tuple[sqlite3.Connection, Path]:
    """In-memory stores with one question and its v1 rubric, plus a one-question bank."""
    q = QuestionStore(conn).get(question_id)
    s = connect(":memory:")
    RubricStore(s).save(RubricStore(conn).get(q.rubric_hash))
    QuestionStore(s).save(q)
    bank = tmp / f"bank_{question_id}.json"
    bank.write_text(json.dumps([{"question_id": question_id}]), encoding="utf-8")
    return s, bank


@contextmanager
def _env(name: str, value: str) -> Iterator[None]:
    old = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old


def run(conn: sqlite3.Connection, config: AppConfig, tmp: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    # 1. Judge rate-limited -> queued, then retried once the limit is back.
    s, bank = _scratch(conn, BALLOON_QUESTION, tmp)
    broken = config.model_copy(deep=True)
    judge = broken.roles["judge"]
    broken.providers[judge.provider].model_limits[judge.model] = (
        broken.providers[judge.provider].limits_for(judge.model).model_copy(update={"rpd": 1})
    )
    # Today's real usage is counted on the shared database, so it exceeds 1.
    usage_conn = conn
    svc = EngineService(s, build_client(broken, usage_conn), broken, bank_file=bank)
    before = _other_calls(conn)
    sub = svc.submit(BALLOON_QUESTION, PLAIN_ANSWER)
    stand_ins = _other_calls(conn) - before
    queued = (sub.status, sub.last_error)
    restored = EngineService(s, build_client(config, conn), config, bank_file=bank)
    (after,) = restored.retry_queued()
    trace = restored.trace(after)
    results.append(
        {
            "path": "judge rate-limited",
            "expected": "queued with 'evaluating…', no other model grades it; graded on retry",
            "first_attempt": queued[0],
            "error": queued[1],
            "other_models_called": stand_ins,
            "after_retry": after.status,
            "graded_by": trace and _judge_model(conn, trace.call_ids[0]),
            "ok": queued[0] == "queued" and stand_ins == 0 and after.status == "done",
        }
    )

    # 2. Verifier down -> original rubric, trace marked.
    item = next(i for i in verifier_set.load_items() if i.item_id == AMENDMENT_ITEM)
    s, bank = _scratch(conn, item.question_id, tmp)
    broken = config.model_copy(deep=True)
    broken.roles["verifier"] = broken.roles["verifier"].model_copy(
        update={"model": "qwen/model-that-does-not-exist"}
    )
    svc = EngineService(s, build_client(broken, conn), broken, bank_file=bank)
    sub = svc.submit(item.question_id, item.answer)
    t = svc.trace(sub)
    results.append(
        {
            "path": "verifier down",
            "expected": "graded on the original rubric, amendment error in the trace",
            "status": sub.status,
            "amendment_fired": t and t.amendment_fired,
            "amendment_error": t and t.amendment_error,
            "rubric_used": t and t.final_rubric_source,
            "ok": bool(t and t.amendment_error and t.final_rubric_source == "generated"),
        }
    )

    # 3. Feedback model down -> templates, marked.
    s, bank = _scratch(conn, BALLOON_QUESTION, tmp)
    with _env("OLLAMA_HOST", "http://127.0.0.1:9"):
        svc = EngineService(
            s, build_client(config, conn), config, bank_file=bank, rng=random.Random(0)
        )
        # A different answer, so neither the judge's nor the phraser's reply is cached.
        sub = svc.submit(BALLOON_QUESTION, PLAIN_ANSWER + " When the air cools it comes down.")
    t = svc.trace(sub)
    sources = sorted({i.source for i in t.feedback.items}) if t and t.feedback else []
    results.append(
        {
            "path": "feedback model down",
            "expected": "graded, with template feedback marked as such",
            "status": sub.status,
            "feedback_sources": sources,
            "fallbacks": t.feedback.fallbacks if t and t.feedback else None,
            "ok": sub.status == "done" and sources == ["template"],
        }
    )
    return results


def _other_calls(conn: sqlite3.Connection) -> int:
    """Calls logged for any role but the judge, cached or not."""
    row = conn.execute("SELECT COUNT(*) FROM llm_calls WHERE role != 'judge'").fetchone()
    return int(row[0])


def _judge_model(conn: sqlite3.Connection, call_id: str) -> str:
    row = conn.execute(
        "SELECT provider, model FROM llm_calls WHERE call_id = ?", (call_id,)
    ).fetchone()
    return f"{row[0]}/{row[1]}" if row else "unknown"


def report(results: list[dict[str, Any]]) -> str:
    lines = ["# Phase 8 degradation checks", ""]
    for r in results:
        lines += [
            f"## {r['path']}: {'PASS' if r['ok'] else 'FAIL'}",
            "",
            f"Expected: {r['expected']}",
            "",
        ]
        lines += [f"- {k}: {v}" for k, v in r.items() if k not in ("path", "expected", "ok")]
        lines.append("")
    return "\n".join(lines)
