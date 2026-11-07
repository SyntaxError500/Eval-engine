"""Phase 9: the offline client, the report comparison and the snapshot round trip. No network."""

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from eval_engine.prompts import PromptRegistry
from eval_engine.providers.client import CacheMiss, LLMClient
from eval_engine.providers.fake import FakeProvider
from eval_engine.storage import RubricStore, connect, snapshot
from eval_engine.storage.calls import CallLog, ResponseCache, UsageCounter
from eval_engine.validation.reproduce import compare
from tests.conftest import make_config, make_rubric


class Reply(BaseModel):
    ok: bool


def client(
    conn: sqlite3.Connection, providers: dict[str, FakeProvider], offline: bool
) -> LLMClient:
    return LLMClient(
        make_config(),
        PromptRegistry(),
        lambda name: providers[name],
        cache=ResponseCache(conn),
        call_log=CallLog(conn),
        usage=UsageCounter(conn),
        offline=offline,
    )


def test_offline_client_answers_from_the_cache_and_never_calls_a_provider(
    conn: sqlite3.Connection, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push(json.dumps({"ok": True}))
    client(conn, providers, offline=False).complete("judge", "smoke", {"token": "t"}, Reply)
    offline = client(conn, providers, offline=True)
    assert offline.complete("judge", "smoke", {"token": "t"}, Reply).value.ok
    with pytest.raises(CacheMiss):
        offline.complete("judge", "smoke", {"token": "t"}, Reply, fresh=True)
    assert len(providers["alpha"].requests) == 1


def test_a_cache_miss_is_not_a_provider_error() -> None:
    """Degradation paths catch ProviderError; a reproduction must fail instead."""
    from eval_engine.providers.base import ProviderError

    assert not issubclass(CacheMiss, ProviderError)


def test_compare_ignores_line_end_whitespace_and_reports_a_change() -> None:
    assert compare("| a | 0.10 |\n", "| a | 0.10 |  \n\n")[0]
    ok, diff = compare("| leniency | -0.010 |\n", "| leniency | -0.012 |\n")
    assert not ok and "-| leniency | -0.010 |" in diff and "+| leniency | -0.012 |" in diff


def test_snapshot_round_trip(tmp_path: Path, conn: sqlite3.Connection) -> None:
    rubric = make_rubric()
    RubricStore(conn).save(rubric)
    db = tmp_path / "live.db"
    src = sqlite3.connect(db)
    conn.backup(src)
    src.close()
    data = tmp_path / "datasets" / "X"
    data.mkdir(parents=True)
    (data / "test_ua.parquet").write_bytes(b"PAR1")

    out = tmp_path / "snap"
    counts: dict[str, Any] = snapshot.export(db, out, tmp_path / "datasets")
    assert counts["rubrics"] == 1
    first = (out / "rubrics.jsonl.gz").read_bytes()
    snapshot.export(db, out, tmp_path / "datasets")
    assert (out / "rubrics.jsonl.gz").read_bytes() == first  # deterministic

    fresh, fresh_data = tmp_path / "fresh.db", tmp_path / "fresh_data"
    added = snapshot.load(fresh, out, fresh_data)
    assert added["rubrics"] == 1 and (fresh_data / "X" / "test_ua.parquet").exists()
    assert snapshot.load(fresh, out, fresh_data)["rubrics"] == 0  # idempotent
    loaded = connect(fresh)
    assert RubricStore(loaded).get(rubric.hash or "") == rubric
    loaded.close()
