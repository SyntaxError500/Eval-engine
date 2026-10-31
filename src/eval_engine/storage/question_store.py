"""Generated questions. The rubric is immutable (RubricStore); a question row is updated
once, when its reference answer is written after the rubric was frozen."""

import sqlite3

from eval_engine.schemas.question import Question
from eval_engine.storage.db import lock_for, locked, utc_now


class QuestionStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._lock = lock_for(conn)

    @locked
    def save(self, q: Question) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO questions (question_id, rubric_id, body, created_at)"
                " VALUES (?, ?, ?, ?)"
                " ON CONFLICT (question_id) DO UPDATE SET body = excluded.body",
                (q.question_id, q.rubric_id, q.model_dump_json(), utc_now()),
            )

    @locked
    def get(self, question_id: str) -> Question:
        row = self._conn.execute(
            "SELECT body FROM questions WHERE question_id = ?", (question_id,)
        ).fetchone()
        if row is None:
            raise KeyError(question_id)
        return Question.model_validate_json(row["body"])

    @locked
    def all(self) -> list[Question]:
        rows = self._conn.execute("SELECT body FROM questions ORDER BY created_at").fetchall()
        return [Question.model_validate_json(r["body"]) for r in rows]

    def by_topic(self, topic: str) -> list[Question]:
        return [q for q in self.all() if q.topic == topic]
