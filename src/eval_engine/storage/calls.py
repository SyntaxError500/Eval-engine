"""Call log, response cache and daily usage counters."""

import json
import sqlite3
from dataclasses import dataclass

from eval_engine.schemas.trace import LLMCall
from eval_engine.storage.db import utc_now


class CallLog:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def record(self, call: LLMCall) -> None:
        d = call.model_dump(mode="json")
        d["retry_errors"] = json.dumps(d["retry_errors"])
        cols = ", ".join(d)
        marks = ", ".join("?" for _ in d)
        with self._conn:
            self._conn.execute(
                f"INSERT INTO llm_calls ({cols}) VALUES ({marks})", tuple(d.values())
            )

    def for_evaluation(self, evaluation_id: str) -> list[LLMCall]:
        rows = self._conn.execute(
            "SELECT * FROM llm_calls WHERE evaluation_id = ? ORDER BY timestamp", (evaluation_id,)
        ).fetchall()
        return [
            LLMCall.model_validate({**dict(r), "retry_errors": json.loads(r["retry_errors"])})
            for r in rows
        ]

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM llm_calls").fetchone()[0])


@dataclass(frozen=True)
class CachedResponse:
    text: str
    input_tokens: int | None
    output_tokens: int | None


class ResponseCache:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get(self, key: str) -> CachedResponse | None:
        row = self._conn.execute(
            "SELECT text, input_tokens, output_tokens FROM response_cache WHERE request_key = ?",
            (key,),
        ).fetchone()
        return CachedResponse(row[0], row[1], row[2]) if row else None

    def put(
        self,
        key: str,
        provider: str,
        model: str,
        text: str,
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT OR REPLACE INTO response_cache (request_key, provider, model, text,"
                " input_tokens, output_tokens, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (key, provider, model, text, input_tokens, output_tokens, utc_now()),
            )


class UsageCounter:
    """Requests actually sent per provider/model/day; backs the requests-per-day limit."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def increment(self, provider: str, model: str, day: str, tokens: int = 0) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO usage (provider, model, day, requests, tokens) VALUES (?, ?, ?, 1, ?)"
                " ON CONFLICT (provider, model, day)"
                " DO UPDATE SET requests = requests + 1, tokens = tokens + excluded.tokens",
                (provider, model, day, tokens),
            )

    def add_tokens(self, provider: str, model: str, day: str, tokens: int) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE usage SET tokens = tokens + ? WHERE provider = ? AND model = ? AND day = ?",
                (tokens, provider, model, day),
            )

    def requests_on(self, provider: str, model: str, day: str) -> int:
        row = self._conn.execute(
            "SELECT requests FROM usage WHERE provider = ? AND model = ? AND day = ?",
            (provider, model, day),
        ).fetchone()
        return int(row[0]) if row else 0

    def tokens_on(self, provider: str, model: str, day: str) -> int:
        row = self._conn.execute(
            "SELECT tokens FROM usage WHERE provider = ? AND model = ? AND day = ?",
            (provider, model, day),
        ).fetchone()
        return int(row[0]) if row else 0

    def summary(self, day: str | None = None) -> list[sqlite3.Row]:
        if day is None:
            return self._conn.execute(
                "SELECT * FROM usage ORDER BY day DESC, provider, model"
            ).fetchall()
        return self._conn.execute(
            "SELECT * FROM usage WHERE day = ? ORDER BY provider, model", (day,)
        ).fetchall()
