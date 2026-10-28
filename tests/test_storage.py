import sqlite3

import pytest

from eval_engine.schemas import Rubric
from eval_engine.storage import RubricStore, RubricStoreError
from tests.conftest import make_rubric, rubric_data


def amended(parent: Rubric, version: int = 2) -> Rubric:
    return Rubric.model_validate(
        rubric_data(version=version, parent_hash=parent.hash, source="amendment")
    ).freeze()


def test_save_and_load(conn: sqlite3.Connection) -> None:
    store = RubricStore(conn)
    r = make_rubric()
    store.save(r)
    assert r.hash is not None
    assert store.get(r.hash) == r
    assert store.latest("r1") == r


def test_unfrozen_rubric_rejected(conn: sqlite3.Connection) -> None:
    with pytest.raises(RubricStoreError, match="frozen"):
        RubricStore(conn).save(Rubric.model_validate(rubric_data()))


def test_versions_are_append_only(conn: sqlite3.Connection) -> None:
    store = RubricStore(conn)
    v1 = make_rubric()
    store.save(v1)
    with pytest.raises(RubricStoreError, match="already exists"):
        store.save(make_rubric(topic="other"))


def test_amendment_lineage(conn: sqlite3.Connection) -> None:
    store = RubricStore(conn)
    v1 = make_rubric()
    store.save(v1)
    v2 = amended(v1)
    store.save(v2)
    assert store.latest("r1").version == 2
    assert [r.version for r in store.history("r1")] == [1, 2]


@pytest.mark.parametrize("bad", ["missing_parent", "skips_version", "v1_with_parent"])
def test_bad_lineage_rejected(conn: sqlite3.Connection, bad: str) -> None:
    store = RubricStore(conn)
    v1 = make_rubric()
    store.save(v1)
    if bad == "missing_parent":
        r = Rubric.model_validate(rubric_data(version=2, source="amendment")).freeze()
    elif bad == "skips_version":
        r = amended(v1, version=3)
    else:
        r = Rubric.model_validate(rubric_data(rubric_id="r2", parent_hash=v1.hash)).freeze()
    with pytest.raises(RubricStoreError):
        store.save(r)


def test_tampered_row_detected_on_load(conn: sqlite3.Connection) -> None:
    store = RubricStore(conn)
    r = make_rubric()
    store.save(r)
    conn.execute("UPDATE rubrics SET body = replace(body, 'history', 'ethics')")
    with pytest.raises(RubricStoreError, match="hash check"):
        store.latest("r1")
