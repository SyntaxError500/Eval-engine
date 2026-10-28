import json

import pytest
from pydantic import ValidationError

from eval_engine.providers.jsonutil import inline_schema
from eval_engine.schemas import JudgeOutput, Rubric, RubricDraft
from tests.conftest import make_rubric, rubric_data


def test_hash_ignores_key_order() -> None:
    data = rubric_data()
    reordered = json.loads(json.dumps(dict(reversed(list(data.items())))))
    assert (
        Rubric.model_validate(data).compute_hash()
        == Rubric.model_validate(reordered).compute_hash()
    )


def test_hash_changes_when_content_changes() -> None:
    a = make_rubric()
    data = rubric_data()
    data["paths"][0]["criteria"][0]["weight"] = 2.0
    assert Rubric.model_validate(data).compute_hash() != a.hash


def test_freeze_and_round_trip() -> None:
    r = make_rubric()
    assert r.is_frozen
    loaded = Rubric.model_validate_json(r.model_dump_json())
    assert loaded.is_frozen and loaded.hash == r.hash


def test_tampered_hash_detected() -> None:
    r = make_rubric().model_copy(update={"topic": "ethics"})
    assert not r.is_frozen


def test_rubric_is_immutable() -> None:
    r = make_rubric()
    with pytest.raises(ValidationError):
        r.topic = "ethics"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"shape": "checklist"}, "requires shape"),
        ({"task_type": "factual", "shape": "checklist"}, "exactly one path"),
        ({"obvious_answers": ["a"]}, "only allowed for creative"),
    ],
)
def test_structural_invariants(overrides: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        Rubric.model_validate(rubric_data(**overrides))


def test_duplicate_criterion_ids_rejected() -> None:
    data = rubric_data()
    data["paths"][1]["criteria"][0]["criterion_id"] = "P1.C1"
    with pytest.raises(ValidationError, match="criterion_id"):
        Rubric.model_validate(data)


def test_creative_requires_five_obvious_answers() -> None:
    single = rubric_data()["paths"][:1]
    base = {"task_type": "creative", "shape": "craft_tests", "paths": single}
    with pytest.raises(ValidationError, match="exactly 5"):
        Rubric.model_validate(rubric_data(**base, obvious_answers=["a", "b"]))
    Rubric.model_validate(rubric_data(**base, obvious_answers=list("abcde")))


@pytest.mark.parametrize("model", [RubricDraft, JudgeOutput])
def test_llm_facing_schemas_inline_cleanly(model: type) -> None:
    schema = inline_schema(model.model_json_schema())
    text = json.dumps(schema)
    assert "$ref" not in text and "$defs" not in text
    assert schema["type"] == "object"
