"""End-to-end pilot on synthetic corpora with fake providers (no network, no real data)."""

import json
import sqlite3
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from eval_engine.providers.base import CompletionRequest, QuotaExhausted
from eval_engine.providers.fake import FakeProvider
from eval_engine.storage import RubricStore
from eval_engine.validation import pilot
from eval_engine.validation.datasets import LABELS_5WAY, load_split, sample_by_question
from tests.conftest import make_config

LABEL_CYCLE = [0, 2, 1, 3, 0, 2]  # correct, partial, contradictory, irrelevant, ...


def write_corpus(root: Path, dataset: str, n_questions: int = 4, per_q: int = 6) -> None:
    rows = []
    for q in range(n_questions):
        for a in range(per_q):
            label = LABEL_CYCLE[a % len(LABEL_CYCLE)]
            rows.append(
                {
                    "id": f"{q}.{a}",
                    "question": f"{dataset} question {q}?",
                    "reference_answer": f"reference {q}",
                    "student_answer": f"{LABELS_5WAY[label]} answer {a}",
                    "label": label,
                }
            )
    (root / dataset).mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(rows), root / dataset / "test_ua.parquet")


def fake_rubric(req: CompletionRequest) -> str:
    return json.dumps(
        {
            "question": "overwritten by prepare",
            "task_type": "factual",
            "shape": "checklist",
            "paths": [
                {
                    "path_id": "P1",
                    "description": "Reference approach",
                    "criteria": [
                        {
                            "criterion_id": "P1.C1",
                            "dimension": "correctness",
                            "statement": "States the key idea",
                            "evidence_hint": "the idea",
                            "core": True,
                            "weight": 1.0,
                        },
                        {
                            "criterion_id": "P1.C2",
                            "dimension": "completeness",
                            "statement": "Mentions a supporting detail",
                            "evidence_hint": "the detail",
                            "core": False,
                            "weight": 0.5,
                        },
                    ],
                }
            ],
            "obvious_answers": [],
        }
    )


def fake_judge(req: CompletionRequest) -> str:
    """Grades the synthetic answers perfectly, from the label embedded in the answer text."""
    answer = req.user.split("<<<ANSWER", 1)[1]
    correct = "correct answer" in answer and "partially" not in answer
    partial = "partially" in answer
    errors = [{"quote": "x", "explanation": "y"}] if "contradictory" in answer else []
    return json.dumps(
        {
            "identified_path": "P1",
            "path_confidences": [{"path_id": "P1", "confidence": 0.9}],
            "verdicts": [
                {"criterion_id": "P1.C1", "met": correct, "evidence": "", "justification": ""},
                {
                    "criterion_id": "P1.C2",
                    "met": correct or partial,
                    "evidence": "",
                    "justification": "",
                },
            ],
            "errors": errors,
        }
    )


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "datasets"
    for ds, _ in pilot.SOURCES:
        write_corpus(root, ds)
    return root


@pytest.fixture
def pilot_client(make_client: Any, providers: dict[str, FakeProvider]) -> Any:
    providers["alpha"].push(*[fake_rubric] * 50)
    providers["beta"].push(*[fake_judge] * 200)
    role = {"temperature": 0.0, "max_output_tokens": 512}
    config = make_config(
        roles={
            "generator": {"provider": "alpha", "model": "gen", "family": "a", **role},
            "judge": {"provider": "beta", "model": "jdg", "family": "b", **role},
        }
    )
    return make_client(config)


def test_sampling_is_deterministic_and_diverse(corpus: Path) -> None:
    items = load_split("SciEntsBank", "test_ua", corpus)
    a = sample_by_question(items, 3, 4, seed=1)
    b = sample_by_question(items, 3, 4, seed=1)
    assert [i.item_id for i in a] == [i.item_id for i in b]
    assert len(a) == 12 and len({i.question_key for i in a}) == 3
    first_q = [i for i in a if i.question_key == a[0].question_key]
    assert len({i.label for i in first_q}) == 4  # round-robin across labels


def test_prepare_run_report(
    pilot_client: Any,
    providers: dict[str, FakeProvider],
    conn: sqlite3.Connection,
    corpus: Path,
    tmp_path: Path,
) -> None:
    out = tmp_path / "out"
    store = RubricStore(conn)
    cfg = pilot.PilotConfig(answers_per_dataset=8, max_per_question=4, seed=3)

    summary = pilot.prepare(pilot_client, store, cfg, data_dir=corpus, out_dir=out)
    assert summary["items"] == 16 and summary["questions"] == 4 and summary["built"] == 4
    assert (out / "rubrics_review.md").exists()
    # The generator never sees student answers.
    assert all(
        "answer" not in r.user.split("Reference answer")[0] for r in providers["alpha"].requests
    )

    again = pilot.prepare(pilot_client, store, cfg, data_dir=corpus, out_dir=out)
    assert again["built"] == 0 and again["reused"] == 4

    rows, stop = pilot.run(pilot_client, store, "judge", data_dir=corpus, out_dir=out)
    assert stop is None and len(rows) == 16 and all(r.error is None for r in rows)
    # The judge never sees the reference answer.
    assert all("reference" not in r.user for r in providers["beta"].requests)

    text, results = pilot.report(["judge"], out_dir=out, n_resamples=50)
    assert results[0].leniency.value == pytest.approx(0.0)
    assert "PASS" in text and (out / "REPORT.md").exists()


def test_run_stops_cleanly_on_quota(
    pilot_client: Any,
    providers: dict[str, FakeProvider],
    conn: sqlite3.Connection,
    corpus: Path,
    tmp_path: Path,
) -> None:
    out = tmp_path / "out"
    store = RubricStore(conn)
    pilot.prepare(pilot_client, store, pilot.PilotConfig(8, 4, 3), data_dir=corpus, out_dir=out)
    beta = providers["beta"]
    beta._script = [fake_judge, fake_judge, QuotaExhausted("daily limit")]
    rows, stop = pilot.run(pilot_client, store, "judge", data_dir=corpus, out_dir=out)
    assert len(rows) == 2 and stop is not None and "quota" in stop


def test_plan_sample_adapts_to_answers_per_question(tmp_path: Path) -> None:
    root = tmp_path / "d"
    write_corpus(root, "Four", n_questions=10, per_q=4)  # like SciEntsBank test_ua
    items = load_split("Four", "test_ua", root)
    assert pilot.plan_sample(items, pilot.PilotConfig(20, 5, 0)) == (5, 4)


def test_distinct_reference_answers_get_distinct_rubrics() -> None:
    from eval_engine.validation.datasets import GradedAnswer

    a = GradedAnswer("1", "B", "s", "Why?", "ref one", "x", "correct")
    b = GradedAnswer("2", "B", "s", "Why?", "ref two", "y", "correct")
    assert pilot.rubric_id_for(a) != pilot.rubric_id_for(b)
