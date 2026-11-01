"""Stored evaluations: one full trace per graded answer (design doc §15)."""

import sqlite3

from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage.db import lock_for, locked, utc_now


class EvaluationStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._lock = lock_for(conn)

    @locked
    def save(self, trace: EvaluationTrace) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO evaluations (evaluation_id, question_id, trace, created_at)"
                " VALUES (?, ?, ?, ?)",
                (trace.evaluation_id, trace.question_id, trace.model_dump_json(), utc_now()),
            )

    @locked
    def get(self, evaluation_id: str) -> EvaluationTrace:
        row = self._conn.execute(
            "SELECT trace FROM evaluations WHERE evaluation_id = ?", (evaluation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(evaluation_id)
        return EvaluationTrace.model_validate_json(row["trace"])

    @locked
    def for_question(self, question_id: str) -> list[EvaluationTrace]:
        rows = self._conn.execute(
            "SELECT trace FROM evaluations WHERE question_id = ? ORDER BY created_at",
            (question_id,),
        ).fetchall()
        return [EvaluationTrace.model_validate_json(r["trace"]) for r in rows]
