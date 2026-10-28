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
