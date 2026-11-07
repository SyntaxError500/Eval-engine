"""SQLite storage. One file holds rubrics, questions, traces, the call log, cache and usage."""

import sqlite3
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Concatenate, Protocol

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
-- Learner submissions from the app (Phase 8). A submission waits in 'queued' while the judge
-- is unavailable and is retried later; it is never graded by another model.
CREATE TABLE IF NOT EXISTS submissions (
    submission_id TEXT PRIMARY KEY,
    question_id   TEXT NOT NULL,
    answer        TEXT NOT NULL,
    status        TEXT NOT NULL,
    evaluation_id TEXT,
    attempts      INTEGER NOT NULL DEFAULT 0,
    last_error    TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

-- A learner's discussion of a graded submission with the tutor (local model). Kept so disputes
-- of a grade can be read in the admin view; nothing here feeds back into grading.
CREATE TABLE IF NOT EXISTS discussions (
    submission_id TEXT NOT NULL,
    turn          INTEGER NOT NULL,
    role          TEXT NOT NULL,
    text          TEXT NOT NULL,
    call_id       TEXT,
    created_at    TEXT NOT NULL,
    meta          TEXT,
    PRIMARY KEY (submission_id, turn)
);

-- At most one re-check per submission: the judge model takes a second look at the decisions
-- the learner disputes. The original evaluation is never changed; the result sits beside it.
CREATE TABLE IF NOT EXISTS rechecks (
    submission_id TEXT PRIMARY KEY,
    evaluation_id TEXT NOT NULL,
    argument      TEXT NOT NULL,
    result_json   TEXT NOT NULL,
    call_id       TEXT,
    created_at    TEXT NOT NULL
);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    # Generous lock timeout: several judge runs may write to the same file concurrently.
    conn = sqlite3.connect(path, timeout=30.0, check_same_thread=False, factory=LockedConnection)
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
    if "meta" not in {r[1] for r in conn.execute("PRAGMA table_info(discussions)")}:
        conn.execute("ALTER TABLE discussions ADD COLUMN meta TEXT")
        conn.commit()


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class LockedConnection(sqlite3.Connection):
    """A connection that carries its own lock. A sqlite3 connection may be shared across
    threads only if access is serialised; every storage class takes this lock."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.lock = threading.RLock()


def lock_for(conn: sqlite3.Connection) -> threading.RLock:
    if not isinstance(conn, LockedConnection):
        raise TypeError("open connections with storage.db.connect()")
    return conn.lock


class _HasLock(Protocol):
    _lock: threading.RLock


def locked[S: _HasLock, **P, R](
    fn: Callable[Concatenate[S, P], R],
) -> Callable[Concatenate[S, P], R]:
    """Method decorator: run under the instance's connection lock."""

    def wrapper(self: S, /, *args: P.args, **kwargs: P.kwargs) -> R:
        with self._lock:
            return fn(self, *args, **kwargs)

    return wrapper
