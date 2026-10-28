"""Loading of config/*.yaml and environment settings."""

import os
from pathlib import Path
from typing import Literal, Self

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

# src/eval_engine/config.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]


class ConfigError(Exception):
    pass


class Limits(BaseModel):
    rpm: int | None = Field(default=None, gt=0)
    tpm: int | None = Field(default=None, gt=0)
    rpd: int | None = Field(default=None, gt=0)
    tpd: int | None = Field(default=None, gt=0)


class ProviderConfig(BaseModel):
    api_key_env: str | None
    limits: Limits = Field(default_factory=Limits)
    # Per-model overrides; free tiers differ a lot by model (Gemini Flash 20/day vs Lite 500).
    model_limits: dict[str, Limits] = Field(default_factory=dict)
    rpd_reset_tz: str = "UTC"

    def limits_for(self, model: str) -> Limits:
        return self.model_limits.get(model, self.limits)


class RoleConfig(BaseModel):
    provider: str
    model: str
    family: str = Field(min_length=1, description="Model family, for self-preference separation")
    temperature: float = Field(ge=0.0, le=2.0)
    max_output_tokens: int = Field(gt=0)
    reasoning_effort: str | None = None
    json_mode: Literal["schema", "object"] = "schema"


class RetryConfig(BaseModel):
    max_attempts: int = Field(default=4, ge=1)
    base_delay_s: float = Field(default=2.0, ge=0)
    max_delay_s: float = Field(default=60.0, ge=0)


class AppConfig(BaseModel):
    providers: dict[str, ProviderConfig]
    roles: dict[str, RoleConfig]
    retry: RetryConfig = Field(default_factory=RetryConfig)

    @model_validator(mode="after")
    def _roles_use_known_providers(self) -> Self:
        for name, role in self.roles.items():
            if role.provider not in self.providers:
                raise ValueError(f"role {name!r} uses unknown provider {role.provider!r}")
        return self

    def role(self, name: str) -> RoleConfig:
        try:
            return self.roles[name]
        except KeyError:
            raise ConfigError(f"unknown role {name!r}; known: {sorted(self.roles)}") from None


def load_config(path: Path | None = None) -> AppConfig:
    path = path or REPO_ROOT / "config" / "roles.yaml"
    with path.open(encoding="utf-8") as f:
        return AppConfig.model_validate(yaml.safe_load(f))


def load_env() -> None:
    load_dotenv(REPO_ROOT / ".env")


def db_path() -> Path:
    raw = os.environ.get("EVAL_ENGINE_DB", "data/eval_engine.db")
    p = Path(raw)
    return p if p.is_absolute() else REPO_ROOT / p
