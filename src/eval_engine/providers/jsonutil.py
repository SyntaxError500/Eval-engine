"""JSON helpers shared by all providers."""

import json
import re
from typing import Any

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_DROP_KEYS = frozenset({"title", "default"})


def inline_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve local $refs and drop keys some structured-output backends reject.

    Pydantic emits `$defs` + `$ref`; not every provider follows references, so we inline them.
    """
    defs: dict[str, Any] = schema.get("$defs", {})

    def resolve(node: Any, seen: tuple[str, ...]) -> Any:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/$defs/"):
                name = ref.removeprefix("#/$defs/")
                if name in seen:
                    raise ValueError(f"recursive schema reference {name!r} cannot be inlined")
                merged = {**defs[name], **{k: v for k, v in node.items() if k != "$ref"}}
                return resolve(merged, (*seen, name))
            return {
                k: resolve(v, seen) for k, v in node.items() if k not in _DROP_KEYS and k != "$defs"
            }
        if isinstance(node, list):
            return [resolve(v, seen) for v in node]
        return node

    result: dict[str, Any] = resolve(schema, ())
    return result


def extract_json(text: str) -> Any:
    """Parse a model reply as JSON, tolerating code fences and leading/trailing prose."""
    s = _FENCE.sub("", text.strip()).strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        start, end = s.find("{"), s.rfind("}")
        if start == -1 or end <= start:
            raise
        return json.loads(s[start : end + 1])
