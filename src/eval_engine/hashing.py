"""Canonical JSON and hashing. Anything that is hashed must go through here."""

import hashlib
import json
from typing import Any


def canonical_json(data: Any) -> str:
    """Deterministic JSON: sorted keys, no insignificant whitespace, UTF-8 preserved."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_data(data: Any) -> str:
    return sha256_hex(canonical_json(data))
