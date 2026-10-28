"""SQLite storage. One file holds rubrics, questions, traces, the call log, cache and usage."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS rubrics (
    hash        TEXT PRIMARY KEY,
    rubric_id   TEXT NOT NULL,
    version     INTEGER NOT NULL,
    parent_hash TEXT REFERENCES rubrics(hash),
    source      TEXT NOT NULL,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    UNIQUE (rubric_id, version)
);
CREATE TABLE IF NOT EXISTS questions (
    question_id TEXT PRIMARY KEY,
    rubric_id   TEXT NOT NULL,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS evaluations (
    evaluation_id TEXT PRIMARY KEY,
    question_id   TEXT NOT NULL,
    trace         TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS llm_calls (
    call_id        TEXT PRIMARY KEY,
    timestamp      TEXT NOT NULL,
    role           TEXT NOT NULL,
    provider       TEXT NOT NULL,
    model          TEXT NOT NULL,
    prompt_name    TEXT NOT NULL,
    prompt_version INTEGER NOT NULL,
    prompt_hash    TEXT NOT NULL,
    request_key    TEXT NOT NULL,
    cache_hit      INTEGER NOT NULL,
    repaired       INTEGER NOT NULL,
    attempts       INTEGER NOT NULL,
    input_tokens   INTEGER,
    output_tokens  INTEGER,
    latency_ms     INTEGER,
    error          TEXT,
    retry_errors   TEXT NOT NULL DEFAULT '[]',
    evaluation_id  TEXT
);
CREATE INDEX IF NOT EXISTS llm_calls_eval ON llm_calls (evaluation_id);
CREATE TABLE IF NOT EXISTS response_cache (
    request_key   TEXT PRIMARY KEY,
    provider      TEXT NOT NULL,
    model         TEXT NOT NULL,
    text          TEXT NOT NULL,
    input_tokens  INTEGER,
    output_tokens INTEGER,
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usage (
    provider TEXT NOT NULL,
    model    TEXT NOT NULL,
    day      TEXT NOT NULL,
    requests INTEGER NOT NULL DEFAULT 0,
    tokens   INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (provider, model, day)
);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.executescript(SCHEMA)
    _migrate(conn)
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """Additive column migrations for databases created by earlier versions."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(llm_calls)")}
    if "retry_errors" not in cols:
        conn.execute("ALTER TABLE llm_calls ADD COLUMN retry_errors TEXT NOT NULL DEFAULT '[]'")
        conn.commit()


def utc_now() -> str:
    return datetime.now(UTC).isoformat()
