"""Versioned prompt templates in prompts/*.yaml (keys: name, version, description, system, user).

The template file's hash is logged with every call, so an edited prompt is always detectable
even if someone forgets to bump `version`.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, StrictUndefined

from eval_engine.config import REPO_ROOT
from eval_engine.hashing import sha256_hex


@dataclass(frozen=True)
class PromptTemplate:
    name: str
    version: int
    description: str
    system: str
    user: str
    file_hash: str


@dataclass(frozen=True)
class RenderedPrompt:
    name: str
    version: int
    template_hash: str
    system: str
    user: str


class PromptRegistry:
    def __init__(self, directory: Path | None = None) -> None:
        self._dir = directory or REPO_ROOT / "prompts"
        self._env = Environment(
            undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True
        )
        self._cache: dict[str, PromptTemplate] = {}

    def get(self, name: str) -> PromptTemplate:
        if name not in self._cache:
            self._cache[name] = self._load(name)
        return self._cache[name]

    def render(self, name: str, variables: dict[str, Any] | None = None) -> RenderedPrompt:
        t = self.get(name)
        v = variables or {}
        return RenderedPrompt(
            name=t.name,
            version=t.version,
            template_hash=t.file_hash,
            system=self._env.from_string(t.system).render(**v),
            user=self._env.from_string(t.user).render(**v),
        )

    def _load(self, name: str) -> PromptTemplate:
        path = self._dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"prompt {name!r} not found at {path}")
        raw = path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        missing = {"name", "version", "system", "user"} - set(data)
        if missing:
            raise ValueError(f"prompt {path.name} is missing keys: {sorted(missing)}")
        if data["name"] != name:
            raise ValueError(f"prompt {path.name} declares name {data['name']!r}")
        return PromptTemplate(
            name=name,
            version=int(data["version"]),
            description=str(data.get("description", "")),
            system=str(data["system"]),
            user=str(data["user"]),
            file_hash=sha256_hex(raw),
        )
