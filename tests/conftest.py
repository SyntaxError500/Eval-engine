import sqlite3
from collections.abc import Iterator
from typing import Any

import pytest

from eval_engine.config import AppConfig
from eval_engine.prompts import PromptRegistry
from eval_engine.providers.client import LLMClient
from eval_engine.providers.fake import FakeProvider
from eval_engine.schemas import Rubric
from eval_engine.storage import CallLog, ResponseCache, UsageCounter, connect


class FakeClock:
    def __init__(self) -> None:
        self.t = 1000.0
        self.sleeps: list[float] = []

    def now(self) -> float:
        return self.t

    def sleep(self, dt: float) -> None:
        self.sleeps.append(dt)
        self.t += dt


@pytest.fixture
def conn() -> Iterator[sqlite3.Connection]:
    c = connect(":memory:")
    yield c
    c.close()


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


def make_config(**overrides: Any) -> AppConfig:
    data: dict[str, Any] = {
        "providers": {
            "alpha": {"api_key_env": None, "limits": {"rpm": 100}},
            "beta": {"api_key_env": None, "limits": {"rpm": 100}},
        },
        "roles": {
            "judge": {
                "provider": "alpha",
                "model": "alpha-1",
                "family": "a",
                "temperature": 0.0,
                "max_output_tokens": 256,
            },
        },
        "retry": {"max_attempts": 3, "base_delay_s": 1.0, "max_delay_s": 10.0},
    }
    data.update(overrides)
    return AppConfig.model_validate(data)


@pytest.fixture
def providers() -> dict[str, FakeProvider]:
    return {"alpha": FakeProvider(name="alpha"), "beta": FakeProvider(name="beta")}


@pytest.fixture
def make_client(
    conn: sqlite3.Connection, clock: FakeClock, providers: dict[str, FakeProvider]
) -> Any:
    def _make(config: AppConfig | None = None, use_cache: bool = True) -> LLMClient:
        return LLMClient(
            config or make_config(),
            PromptRegistry(),
            lambda name: providers[name],
            cache=ResponseCache(conn),
            call_log=CallLog(conn),
            usage=UsageCounter(conn),
            use_cache=use_cache,
            clock=clock.now,
            sleep=clock.sleep,
            rng=lambda: 1.0,
        )

    return _make


def rubric_data(**overrides: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "rubric_id": "r1",
        "topic": "history",
        "version": 1,
        "source": "generated",
        "question": "Why did the Western Roman Empire fall?",
        "task_type": "analytical",
        "shape": "multi_path_claim_evidence",
        "paths": [
            {
                "path_id": "P1",
                "description": "Economic causes",
                "criteria": [
                    {
                        "criterion_id": "P1.C1",
                        "dimension": "reasoning",
                        "statement": "Links an economic cause to the collapse via a mechanism",
                        "evidence_hint": "A because/led-to chain",
                        "core": True,
                        "weight": 1.0,
                    },
                    {
                        "criterion_id": "P1.C2",
                        "dimension": "correctness",
                        "statement": "States at least one accurate economic fact",
                        "evidence_hint": "e.g. currency debasement",
                        "core": False,
                        "weight": 0.5,
                    },
                ],
            },
            {
                "path_id": "P2",
                "description": "Military pressure",
                "criteria": [
                    {
                        "criterion_id": "P2.C1",
                        "dimension": "reasoning",
                        "statement": "Connects external invasions to loss of state capacity",
                        "evidence_hint": "Names a group and a consequence",
                        "core": True,
                        "weight": 1.0,
                    }
                ],
            },
        ],
    }
    data.update(overrides)
    return data


def make_rubric(**overrides: Any) -> Rubric:
    return Rubric.model_validate(rubric_data(**overrides)).freeze()
