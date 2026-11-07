"""A portable copy of what a fresh clone needs (plan Phase 9): `snapshot/` in the repository.

`data/` is gitignored (the live database also holds usage counters, the call log and app
submissions), so a fresh clone would have no questions to show and no cached responses to
regenerate the reports from. The snapshot carries:

- rubrics, questions and evaluations (every version; the reviewed bank and the experiments);
- the call log's metadata (which model and prompt version answered each call);
- the response cache, so `eval-engine reproduce` works with no API calls;
- the two borrowed corpora (SemEval-2013 Task 7, CC BY 4.0), which the Phase 2 and Phase 7
  corpus runs read.

Rows are written in primary-key order to gzip files with a fixed timestamp, so an export of
unchanged data is byte-identical and makes no git diff. Import only adds missing rows.
"""

import gzip
import json
import shutil
import sqlite3
from pathlib import Path

from eval_engine.config import REPO_ROOT
from eval_engine.storage.db import connect
from eval_engine.validation.datasets import DATASET_DIR

SNAPSHOT_DIR = REPO_ROOT / "snapshot"
TABLES = {  # table -> primary key, for a stable order
    "rubrics": "hash",
    "questions": "question_id",
    "evaluations": "evaluation_id",
    "response_cache": "request_key",
    # Metadata only (role, model, prompt version, tokens, errors): no prompts and no keys. The
    # amendment-frequency report needs it to tell judge prompt versions and reruns apart.
    "llm_calls": "call_id",
}


def export(db: Path, out: Path = SNAPSHOT_DIR, datasets: Path = DATASET_DIR) -> dict[str, int]:
    out.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    counts = {}
    try:
        for table, key in TABLES.items():
            where = ""
            if table == "evaluations":
                # App submissions stay out: they are not experiments, and the submissions
                # table isn't exported, so a fresh clone couldn't tell them apart (the
                # amendment-frequency report counted 3 extra rows in the first fresh-clone run).
                where = (
                    " WHERE evaluation_id NOT IN (SELECT evaluation_id FROM submissions"
                    " WHERE evaluation_id IS NOT NULL)"
                )
            rows = conn.execute(f"SELECT * FROM {table}{where} ORDER BY {key}").fetchall()
            lines = "".join(json.dumps(dict(r), ensure_ascii=False) + "\n" for r in rows)
            with (
                open(out / f"{table}.jsonl.gz", "wb") as raw,
                gzip.GzipFile(fileobj=raw, mode="wb", mtime=0, filename="") as gz,
            ):
                gz.write(lines.encode("utf-8"))
            counts[table] = len(rows)
    finally:
        conn.close()
    for parquet in sorted(datasets.glob("*/*.parquet")):
        dest = out / "datasets" / parquet.relative_to(datasets)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(parquet, dest)
        counts[f"datasets/{parquet.relative_to(datasets).as_posix()}"] = 1
    return counts


def load(db: Path, src: Path = SNAPSHOT_DIR, datasets: Path = DATASET_DIR) -> dict[str, int]:
    """Add the snapshot's rows to the database (creating it if needed) and copy the corpora
    into place. Rows already present are left alone."""
    conn = connect(db)
    added = {}
    try:
        for table in TABLES:
            with gzip.open(src / f"{table}.jsonl.gz", "rt", encoding="utf-8") as f:
                rows = [json.loads(line) for line in f if line.strip()]
            before = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if rows:
                cols = list(rows[0])
                marks = ", ".join("?" for _ in cols)
                with conn:
                    conn.executemany(
                        f"INSERT OR IGNORE INTO {table} ({', '.join(cols)}) VALUES ({marks})",
                        [tuple(r[c] for c in cols) for r in rows],
                    )
            after = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            added[table] = after - before
    finally:
        conn.close()
    for parquet in sorted((src / "datasets").glob("*/*.parquet")):
        dest = datasets / parquet.relative_to(src / "datasets")
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(parquet, dest)
            added[f"datasets/{dest.relative_to(datasets).as_posix()}"] = 1
    return added
