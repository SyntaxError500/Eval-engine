import sqlite3

import pytest

from eval_engine.config import Limits
from eval_engine.providers.base import QuotaExhausted
from eval_engine.providers.ratelimit import RateLimiter
from eval_engine.storage import UsageCounter
from tests.conftest import FakeClock


def limiter(conn: sqlite3.Connection, clock: FakeClock, **limits: int) -> RateLimiter:
    return RateLimiter(
        "p",
        "m",
        Limits(**limits),
        UsageCounter(conn),
        clock=clock.now,
        sleep=clock.sleep,
        today=lambda tz: "2026-10-28",
    )


def test_rpm_blocks_until_window_frees(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, rpm=2)
    rl.acquire(1)
    rl.acquire(1)
    assert clock.sleeps == []
    rl.acquire(1)
    assert len(clock.sleeps) == 1 and 59 < clock.sleeps[0] <= 60.1


def test_tpm_blocks_on_token_budget(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, tpm=1000)
    rl.acquire(600)
    rl.acquire(600)
    assert len(clock.sleeps) == 1


def test_settle_corrects_estimate(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, tpm=1000)
    slot = rl.acquire(900)
    rl.settle(slot, 100)
    rl.acquire(800)
    assert clock.sleeps == []


def test_oversized_request_allowed_when_window_empty(
    conn: sqlite3.Connection, clock: FakeClock
) -> None:
    rl = limiter(conn, clock, tpm=100)
    rl.acquire(5000)
    assert clock.sleeps == []


def test_daily_cap_raises_and_persists(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, rpd=2)
    rl.acquire(1)
    rl.acquire(1)
    with pytest.raises(QuotaExhausted):
        rl.acquire(1)
    # A new limiter (new process) sees the same persisted count.
    with pytest.raises(QuotaExhausted):
        limiter(conn, clock, rpd=2).acquire(1)


def test_daily_cap_resets_next_day(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, rpd=1)
    rl.acquire(1)
    tomorrow = RateLimiter(
        "p",
        "m",
        Limits(rpd=1),
        UsageCounter(conn),
        clock=clock.now,
        sleep=clock.sleep,
        today=lambda tz: "2026-10-29",
    )
    tomorrow.acquire(1)


def test_daily_token_cap(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, tpd=1000)
    slot = rl.acquire(500)
    rl.settle(slot, 900)
    with pytest.raises(QuotaExhausted, match="tokens"):
        rl.acquire(200)


def test_output_tokens_per_minute(conn: sqlite3.Connection, clock: FakeClock) -> None:
    rl = limiter(conn, clock, otpm=1000)
    slot = rl.acquire(100, estimated_output=450)
    rl.settle(slot, 600, actual_output=500)
    rl.acquire(100, estimated_output=450)
    assert clock.sleeps == []
    rl.acquire(100, estimated_output=450)  # 500 + 450 + 450 > 1000
    assert len(clock.sleeps) == 1
