"""Append-only, versioned rubric store. A stored rubric is never modified."""

import sqlite3

from eval_engine.schemas.rubric import Rubric
from eval_engine.storage.db import lock_for, locked, utc_now


class RubricStoreError(Exception):
    pass


class RubricStore:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._lock = lock_for(conn)

    @locked
    def save(self, rubric: Rubric) -> None:
        if not rubric.is_frozen:
            raise RubricStoreError("rubric must be frozen (hash set and matching) before saving")
        self._check_lineage(rubric)
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO rubrics (hash, rubric_id, version, parent_hash, source, body,"
                    " created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        rubric.hash,
                        rubric.rubric_id,
                        rubric.version,
                        rubric.parent_hash,
                        rubric.source,
                        rubric.model_dump_json(),
                        utc_now(),
                    ),
                )
        except sqlite3.IntegrityError as e:
            raise RubricStoreError(
                f"rubric {rubric.rubric_id} v{rubric.version} already exists"
            ) from e

    @locked
    def get(self, rubric_hash: str) -> Rubric:
        row = self._conn.execute(
            "SELECT body FROM rubrics WHERE hash = ?", (rubric_hash,)
        ).fetchone()
        if row is None:
            raise KeyError(rubric_hash)
        return self._load(row["body"])

    @locked
    def latest(self, rubric_id: str) -> Rubric:
        row = self._conn.execute(
            "SELECT body FROM rubrics WHERE rubric_id = ? ORDER BY version DESC LIMIT 1",
            (rubric_id,),
        ).fetchone()
        if row is None:
            raise KeyError(rubric_id)
        return self._load(row["body"])

    @locked
    def history(self, rubric_id: str) -> list[Rubric]:
        rows = self._conn.execute(
            "SELECT body FROM rubrics WHERE rubric_id = ? ORDER BY version", (rubric_id,)
        ).fetchall()
        return [self._load(r["body"]) for r in rows]

    @locked
    def _check_lineage(self, rubric: Rubric) -> None:
        if rubric.version == 1:
            if rubric.parent_hash is not None:
                raise RubricStoreError("version 1 must not have a parent_hash")
            return
        if rubric.parent_hash is None:
            raise RubricStoreError(f"version {rubric.version} requires parent_hash")
        try:
            parent = self.get(rubric.parent_hash)
        except KeyError:
            raise RubricStoreError(f"parent {rubric.parent_hash} not found") from None
        if parent.rubric_id != rubric.rubric_id or parent.version != rubric.version - 1:
            raise RubricStoreError(
                f"parent must be {rubric.rubric_id} v{rubric.version - 1}, "
                f"got {parent.rubric_id} v{parent.version}"
            )

    @staticmethod
    def _load(body: str) -> Rubric:
        rubric = Rubric.model_validate_json(body)
        if not rubric.is_frozen:
            raise RubricStoreError(f"stored rubric {rubric.rubric_id} failed its hash check")
        return rubric
