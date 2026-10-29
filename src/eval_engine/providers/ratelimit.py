"""Client-side rate limiting: sliding 60 s window on requests and tokens, plus a daily cap.

Free tiers enforce tokens-per-minute as well as requests-per-minute (Groq's 8K TPM is the
tightest), and some models also cap output tokens per minute (Groq qwen3.8-27b: 1,000),
so all three are tracked. Token use is estimated before the call and corrected after.
"""

import threading
import time
from collections import deque
from collections.abc import Callable
from datetime import datetime
from zoneinfo import ZoneInfo

from eval_engine.config import Limits
from eval_engine.providers.base import QuotaExhausted
from eval_engine.storage.calls import UsageCounter

WINDOW_S = 60.0


class _Slot:
    __slots__ = ("out_tokens", "tokens", "ts")

    def __init__(self, ts: float, tokens: int, out_tokens: int) -> None:
        self.ts = ts
        self.tokens = tokens
        self.out_tokens = out_tokens


class RateLimiter:
    def __init__(
        self,
        provider: str,
        model: str,
        limits: Limits,
        usage: UsageCounter,
        reset_tz: str = "UTC",
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        today: Callable[[ZoneInfo], str] | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self._limits = limits
        self._usage = usage
        self._tz = ZoneInfo(reset_tz)
        self._clock = clock
        self._sleep = sleep
        self._today = today or (lambda tz: datetime.now(tz).date().isoformat())
        self._window: deque[_Slot] = deque()
        # Guards the window across threads; never held while sleeping.
        self._lock = threading.Lock()

    def day(self) -> str:
        return self._today(self._tz)

    def acquire(self, estimated_tokens: int, estimated_output: int = 0) -> _Slot:
        """Block until a request of this size fits, then reserve it. Raises QuotaExhausted."""
        lim = self._limits
        day = self.day()
        if (
            lim.rpd is not None
            and self._usage.requests_on(self.provider, self.model, day) >= lim.rpd
        ):
            raise QuotaExhausted(
                f"{self.provider}/{self.model}: daily limit of {lim.rpd} requests reached ({day})"
            )
        if (
            lim.tpd is not None
            and self._usage.tokens_on(self.provider, self.model, day) + estimated_tokens > lim.tpd
        ):
            raise QuotaExhausted(
                f"{self.provider}/{self.model}: daily limit of {lim.tpd} tokens would be "
                f"exceeded ({day})"
            )
        while True:
            with self._lock:
                now = self._clock()
                while self._window and now - self._window[0].ts >= WINDOW_S:
                    self._window.popleft()
                rpm_ok = lim.rpm is None or len(self._window) < lim.rpm
                used = sum(s.tokens for s in self._window)
                # A single request larger than the TPM budget is allowed once the window is
                # empty; otherwise it could never be sent.
                tpm_ok = lim.tpm is None or used + estimated_tokens <= lim.tpm or not self._window
                used_out = sum(s.out_tokens for s in self._window)
                otpm_ok = (
                    lim.otpm is None or used_out + estimated_output <= lim.otpm or not self._window
                )
                if rpm_ok and tpm_ok and otpm_ok:
                    slot = _Slot(now, estimated_tokens, estimated_output)
                    self._window.append(slot)
                    self._usage.increment(self.provider, self.model, day)
                    return slot
                wait = WINDOW_S - (now - self._window[0].ts) + 0.05
            self._sleep(max(wait, 0.05))

    def settle(
        self, slot: _Slot, actual_tokens: int | None, actual_output: int | None = None
    ) -> None:
        """Replace the estimates with real usage once the provider reports it."""
        with self._lock:
            if actual_output is not None:
                slot.out_tokens = actual_output
            if actual_tokens is not None:
                slot.tokens = actual_tokens
        if actual_tokens is None:
            return
        self._usage.add_tokens(self.provider, self.model, self.day(), actual_tokens)
