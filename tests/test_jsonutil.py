import json

import pytest

from eval_engine.providers.jsonutil import extract_json


@pytest.mark.parametrize(
    "text",
    [
        '{"a": 1}',
        '```json\n{"a": 1}\n```',
        '```\n{"a": 1}\n```',
        'Sure! Here it is:\n{"a": 1}\nHope that helps.',
    ],
)
def test_extract_json_tolerates_wrapping(text: str) -> None:
    assert extract_json(text) == {"a": 1}


def test_extract_json_raises_on_garbage() -> None:
    with pytest.raises(json.JSONDecodeError):
        extract_json("no json here")


def test_strict_schema_closes_objects_and_requires_all_fields() -> None:
    from eval_engine.providers.jsonutil import inline_schema, strict_schema
    from eval_engine.schemas import RubricDraft

    s = strict_schema(inline_schema(RubricDraft.model_json_schema()))
    assert s["additionalProperties"] is False
    assert set(s["required"]) == set(s["properties"])
    crit = s["properties"]["paths"]["items"]["properties"]["criteria"]["items"]
    assert crit["additionalProperties"] is False and "weight" in crit["required"]
    text = json.dumps(s)
    assert "minLength" not in text and "exclusiveMinimum" not in text
