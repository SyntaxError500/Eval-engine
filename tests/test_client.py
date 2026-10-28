import json
from typing import Any

import pytest
from pydantic import BaseModel

from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import StructuredOutputError
from eval_engine.providers.fake import FakeProvider
from eval_engine.storage import CallLog
from tests.conftest import FakeClock, make_config


class Reply(BaseModel):
    status: str
    echo: str


def ok(token: str = "t1") -> str:
    return json.dumps({"status": "ok", "echo": token})


def call(client: Any, token: str = "t1", **kw: Any) -> Any:
    return client.complete("judge", "smoke", {"token": token}, Reply, **kw)


def test_valid_reply_is_parsed_and_logged(
    make_client: Any, providers: dict[str, FakeProvider], conn: Any
) -> None:
    providers["alpha"].push(ok())
    res = call(make_client())
    assert res.value.echo == "t1"
    assert not res.call.cache_hit and not res.call.repaired and res.call.attempts == 1
    assert res.call.provider == "alpha" and res.call.prompt_name == "smoke"
    assert CallLog(conn).count() == 1
    req = providers["alpha"].requests[0]
    assert req.json_schema is not None and "t1" in req.user


def test_invalid_reply_gets_one_repair(
    make_client: Any, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push('{"status": "ok"}', ok())
    res = call(make_client())
    assert res.call.repaired and res.call.attempts == 2
    assert "did not match the required JSON schema" in providers["alpha"].requests[1].user


def test_invalid_twice_raises_and_logs_error(
    make_client: Any, providers: dict[str, FakeProvider], conn: Any
) -> None:
    providers["alpha"].push("not json", '{"status": 1}')
    with pytest.raises(StructuredOutputError):
        call(make_client())
    rows = conn.execute("SELECT error FROM llm_calls").fetchall()
    assert len(rows) == 1 and "StructuredOutputError" in rows[0][0]


def test_cache_hit_skips_provider(make_client: Any, providers: dict[str, FakeProvider]) -> None:
    client = make_client()
    providers["alpha"].push(ok())
    call(client)
    res = call(client)
    assert res.call.cache_hit and len(providers["alpha"].requests) == 1


def test_fresh_bypasses_cache(make_client: Any, providers: dict[str, FakeProvider]) -> None:
    client = make_client()
    providers["alpha"].push(ok(), ok())
    call(client)
    assert not call(client, fresh=True).call.cache_hit
    assert len(providers["alpha"].requests) == 2


def test_different_variables_miss_cache(
    make_client: Any, providers: dict[str, FakeProvider]
) -> None:
    client = make_client()
    providers["alpha"].push(ok("a"), ok("b"))
    call(client, "a")
    assert call(client, "b").value.echo == "b"


def test_retryable_error_backs_off_then_succeeds(
    make_client: Any, providers: dict[str, FakeProvider], clock: FakeClock
) -> None:
    providers["alpha"].push(ProviderError("busy", retryable=True, status=503), ok())
    res = call(make_client())
    assert res.call.attempts == 2
    assert clock.sleeps == [1.0]  # base_delay * 2**0, jitter factor 1.0 in tests


def test_retry_after_is_respected(
    make_client: Any, providers: dict[str, FakeProvider], clock: FakeClock
) -> None:
    providers["alpha"].push(
        ProviderError("slow down", retryable=True, status=429, retry_after=7), ok()
    )
    call(make_client())
    assert clock.sleeps == [7.0]


def test_retries_are_bounded(make_client: Any, providers: dict[str, FakeProvider]) -> None:
    providers["alpha"].push(*[ProviderError("busy", retryable=True) for _ in range(3)])
    with pytest.raises(ProviderError):
        call(make_client())
    assert len(providers["alpha"].requests) == 3


def test_non_retryable_error_propagates_immediately(
    make_client: Any, providers: dict[str, FakeProvider]
) -> None:
    providers["alpha"].push(ProviderError("bad key", retryable=False, status=401))
    with pytest.raises(ProviderError, match="bad key"):
        call(make_client())
    assert len(providers["alpha"].requests) == 1


def test_role_swap_is_config_only(make_client: Any, providers: dict[str, FakeProvider]) -> None:
    providers["beta"].push(ok())
    config = make_config(
        roles={
            "judge": {
                "provider": "beta",
                "model": "beta-9",
                "family": "b",
                "temperature": 0.0,
                "max_output_tokens": 256,
            }
        }
    )
    res = call(make_client(config))
    assert res.call.provider == "beta" and res.call.model == "beta-9"
    assert not providers["alpha"].requests


def test_evaluation_id_links_calls(
    make_client: Any, providers: dict[str, FakeProvider], conn: Any
) -> None:
    providers["alpha"].push(ok())
    call(make_client(), evaluation_id="ev1")
    assert [c.role for c in CallLog(conn).for_evaluation("ev1")] == ["judge"]


def test_retry_errors_are_logged_even_on_success(
    make_client: Any, providers: dict[str, FakeProvider], conn: Any
) -> None:
    providers["alpha"].push(ProviderError("gemini 503: high demand", retryable=True), ok())
    res = call(make_client(), evaluation_id="ev2")
    assert res.call.retry_errors == ["gemini 503: high demand"]
    assert CallLog(conn).for_evaluation("ev2")[0].retry_errors == ["gemini 503: high demand"]


def test_short_retry_hint_is_raised_to_backoff(
    make_client: Any, providers: dict[str, FakeProvider], clock: FakeClock
) -> None:
    hint = ProviderError("otpm", retryable=True, status=429, retry_after=0.5)
    providers["alpha"].push(hint, hint, ok())
    call(make_client())
    assert clock.sleeps == [1.0, 2.0]
