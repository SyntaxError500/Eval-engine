"""Phase 5 test-set tooling: review overrides, metrics, threshold sweep (no network)."""

import json
from pathlib import Path

import pytest

from eval_engine.validation import verifier_set as vs


def write_items(folder: Path, kinds: list[str]) -> None:
    items = [
        {
            "item_id": f"q{i}-{k}",
            "question_id": f"q{i}",
            "kind": k,
            "path": {"description": "d", "criteria": []},
            "justification": "j",
            "answer": "a",
            "note": "n",
        }
        for i, k in enumerate(kinds)
    ]
    (folder / "items.json").write_text(json.dumps({"items": items, "gaps": []}), encoding="utf-8")


def test_review_drops_and_relabels_override_the_authors_intent(tmp_path: Path) -> None:
    write_items(tmp_path, [vs.POSITIVE, "nonsense", "holed"])
    review = {f"q0-{vs.POSITIVE}": {"kind": "restatement"}, "q1-nonsense": {"drop": True}}
    (tmp_path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    items = vs.load_items(tmp_path)
    assert [(i.item_id, i.kind) for i in items] == [
        (f"q0-{vs.POSITIVE}", "restatement"),
        ("q2-holed", "holed"),
    ]
    assert not items[0].valid  # the relabel decides validity, not the item's id


def test_no_review_file_keeps_every_item(tmp_path: Path) -> None:
    write_items(tmp_path, [vs.POSITIVE, "nonsense"])
    assert [i.valid for i in vs.load_items(tmp_path)] == [True, False]


def row(kind: str, accepted: bool, failure: str | None = None) -> str:
    return json.dumps(
        {"item_id": "x", "kind": kind, "accepted": accepted, "failure_type": failure, "reasons": ""}
    )


def test_report_counts_per_framing_and_class(tmp_path: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    lines = [
        row(vs.POSITIVE, True),
        row(vs.POSITIVE, False, "missing_step"),
        row("nonsense", True),
        row("nonsense", False, "factual_error"),
        row("restatement", False, "duplicate_path"),
        json.dumps({"item_id": "y", "kind": "holed", "error": "bad json"}),
    ]
    (results / "adversarial.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    text, summary = vs.report(tmp_path)

    s = summary["adversarial"]
    assert s["tp"] == 1 and s["fp"] == 1 and s["positives"] == 2
    assert s["nonsense"] == {"accepted": 1, "n": 2}
    assert s["holed"] == {"accepted": 0, "n": 0}  # an errored item isn't counted as decided
    assert "5 items decided, 1 with errors" in text and "## neutral" not in text
    assert s["gate_passed"] is False and "1/2 (50%" in text  # 1 of 2 nonsense accepted


def test_gate_counts_misconceptions_with_nonsense(tmp_path: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    lines = [row("nonsense", False, "factual_error")] * 10 + [row(vs.MISCONCEPTION, True)]
    (results / "neutral.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    _, summary = vs.report(tmp_path)
    assert summary["neutral"]["gate_passed"] is True  # 1/11 is within 10%
    (results / "neutral.jsonl").write_text(
        "\n".join([*lines, row(vs.MISCONCEPTION, True)]) + "\n", encoding="utf-8"
    )
    assert vs.report(tmp_path)[1]["neutral"]["gate_passed"] is False  # 2/12


def test_e2e_table_counts_outcomes_per_class() -> None:
    rows = [
        {"kind": "nonsense", "outcome": "verifier rejected"},
        {"kind": "nonsense", "outcome": "proposer declined"},
        {"kind": vs.POSITIVE, "outcome": "accepted"},
    ]
    table = vs._e2e_table(rows)
    assert "| nonsense | 2 | 0 | 1 | 1 | 0 | 0 |" in table
    assert f"| {vs.POSITIVE} | 1 | 1 | 0 | 0 | 0 | 0 |" in table


def test_leak_check_catches_a_path_naming_its_own_flaw() -> None:
    criterion = {
        "dimension": "reasoning",
        "statement": "Explains the claim",
        "evidence_hint": "A link",
        "core": True,
        "requires": "q",
    }
    clean = vs.AuthoredItem(
        description="The market route",
        criteria=[criterion],
        possible=True,
        justification="It holds.",
        answer="a",
        note="This is circular.",  # the note is the one place a flaw may be named
    )
    assert vs._leaks(clean) == []
    leaking = clean.model_copy(update={"description": "Uses circular reasoning"})
    assert "circular" in vs._leaks(leaking)[0]


@pytest.mark.parametrize(("k", "n"), [(0, 19), (19, 19), (1, 19), (9, 19)])
def test_wilson_interval_contains_the_estimate_and_stays_in_range(k: int, n: int) -> None:
    lo, hi = vs.wilson(k, n)
    assert 0.0 <= lo <= k / n <= hi <= 1.0 and lo < hi


def test_wilson_is_not_degenerate_at_zero() -> None:
    assert vs.wilson(0, 19)[1] > 0.1  # 0/19 doesn't prove a rate of zero


def test_sweep_counts_only_answers_that_address_the_question() -> None:
    rows = [
        {"kind": "a", "item_id": "1", "confidence": 0.2, "addresses": True},
        {"kind": "a", "item_id": "2", "confidence": 0.2, "addresses": False},
        {"kind": "a", "item_id": "3", "confidence": 0.65, "addresses": True},
    ]
    assert "| a | 3 | 1 | 1 | 1 | 1 | 2 |" in vs._sweep(rows)
