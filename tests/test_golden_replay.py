"""Replay the recorded golden-set judge replies through the real pipeline (no network).

Fails when a code change alters any recorded score or path, which would also move the
golden pass count reported in experiments/4_eval/FINDINGS.md."""

import sqlite3
from typing import Any

import pytest

from eval_engine.evaluation.pipeline import evaluate
from eval_engine.providers.fake import FakeProvider
from eval_engine.storage import RubricStore
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import golden
from tests.conftest import make_config

pytestmark = pytest.mark.skipif(
    not golden.FIXTURE_FILE.exists(), reason="golden fixture not recorded yet"
)


def test_golden_replay_reproduces_recorded_results(
    make_client: Any, conn: sqlite3.Connection, providers: dict[str, FakeProvider]
) -> None:
    role = {"temperature": 0.0, "max_output_tokens": 2048}
    client = make_client(
        make_config(roles={"judge": {"provider": "alpha", "model": "j", "family": "a", **role}})
    )
    recorded = golden.load_fixture(conn)
    rubrics, questions, evals = RubricStore(conn), QuestionStore(conn), EvaluationStore(conn)
    items = golden.load_items()
    assert {i.id for i in items} == set(recorded), "golden.yaml changed: rerun `eval-engine golden`"
    for item in items:
        rec = recorded[item.id]
        providers["alpha"].push(rec["judge_reply"])
        trace = evaluate(client, rubrics, questions, evals, item.question, item.answer)
        o = golden.check(item, trace)
        assert o.scores == pytest.approx(rec["scores"]), item.id
        assert o.path == rec["path"], item.id
        assert o.passed == rec["passed"], item.id
