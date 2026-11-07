"""LLMClient: the single entry point for every model call.

role -> provider/model (config) -> render prompt -> cache lookup -> rate limit -> call with
retries -> validate against the Pydantic schema (one repair attempt) -> cache -> log.
"""

import json
import os
import random
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from eval_engine.config import AppConfig, RoleConfig
from eval_engine.hashing import hash_data, sha256_hex
from eval_engine.prompts import PromptRegistry, RenderedPrompt
from eval_engine.providers.base import Completion, CompletionRequest, Provider, ProviderError
from eval_engine.providers.jsonutil import extract_json, inline_schema
from eval_engine.providers.ratelimit import RateLimiter
from eval_engine.schemas.trace import LLMCall
from eval_engine.storage.calls import CallLog, ResponseCache, UsageCounter

ProviderFactory = Callable[[str], Provider]

REPAIR_SUFFIX = (
    "\n\n---\nYour previous reply could not be used because it did not match the required "
    "JSON schema.\nError: {error}\nPrevious reply:\n{reply}\n\n"
    "Reply again with only the corrected JSON object."
)


# Parse attempts per call: the first, then a fresh resend (syntax errors) or a repair
# prompt (schema errors). Groq gpt-oss broke JSON syntax on about a third of first replies.
MAX_PARSE_ATTEMPTS = 3


def usage_label(provider: str, api_key_env: str | None) -> str:
    """Name under which daily usage is counted: the provider plus a short fingerprint of the
    API key in use. Free-tier quotas belong to the key's account, so a different key starts
    its own count. The key itself is never stored."""
    key = os.environ.get(api_key_env, "").strip() if api_key_env else ""
    return f"{provider}#{sha256_hex(key)[:8]}" if key else provider


class CacheMiss(Exception):
    """Offline client: the response isn't cached. Deliberately not a ProviderError, so no
    degradation path (template feedback, original rubric) can quietly absorb it: a
    reproduction that needs a live call fails instead of producing different numbers."""


class StructuredOutputError(Exception):
    """The model's reply failed schema validation even after one repair attempt."""


@dataclass(frozen=True)
class LLMResult[T: BaseModel]:
    value: T
    call: LLMCall


class LLMClient:
    def __init__(
        self,
        config: AppConfig,
        prompts: PromptRegistry,
        provider_factory: ProviderFactory,
        *,
        cache: ResponseCache,
        call_log: CallLog,
        usage: UsageCounter,
        use_cache: bool = True,
        offline: bool = False,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        rng: Callable[[], float] = random.random,
    ) -> None:
        self._config = config
        self._prompts = prompts
        self._factory = provider_factory
        self._cache = cache
        self._log = call_log
        self._usage = usage
        self._use_cache = use_cache
        self._offline = offline  # answer only from the cache; never call a provider
        self._clock = clock
        self._sleep = sleep
        self._rng = rng
        self._providers: dict[str, Provider] = {}
        self._limiters: dict[tuple[str, str], RateLimiter] = {}
        self._registry_lock = threading.Lock()  # complete() may be called from several threads

    @property
    def prompts(self) -> PromptRegistry:
        return self._prompts

    def complete[T: BaseModel](
        self,
        role: str,
        prompt: str,
        variables: dict[str, Any],
        schema: type[T],
        *,
        evaluation_id: str | None = None,
        fresh: bool = False,
        write_cache: bool = True,
    ) -> LLMResult[T]:
        """`fresh` skips the cache lookup. `write_cache=False` keeps a call (e.g. a stability
        rerun) from replacing the cached answer that earlier results were computed from."""
        rcfg = self._config.role(role)
        rendered = self._prompts.render(prompt, variables)
        json_schema = inline_schema(schema.model_json_schema())
        req = CompletionRequest(
            model=rcfg.model,
            system=rendered.system,
            user=rendered.user,
            json_schema=json_schema,
            schema_name=schema.__name__,
            temperature=rcfg.temperature,
            max_output_tokens=rcfg.max_output_tokens,
            reasoning_effort=rcfg.reasoning_effort,
            json_mode=rcfg.json_mode,
        )
        key_fields: dict[str, Any] = {
            "provider": rcfg.provider,
            "model": rcfg.model,
            "temperature": rcfg.temperature,
            "max_output_tokens": rcfg.max_output_tokens,
            "reasoning_effort": rcfg.reasoning_effort,
            "system": req.system,
            "user": req.user,
            "schema": json_schema,
        }
        # New request options join the key only when set away from their default, so adding
        # an option never invalidates responses cached before it existed.
        if rcfg.json_mode != "schema":
            key_fields["json_mode"] = rcfg.json_mode
        key = hash_data(key_fields)
        record = _CallRecorder(role, rcfg, rendered, key, evaluation_id)

        if self._use_cache and not fresh:
            hit = self._cache.get(key)
            if hit is not None:
                try:
                    value = _parse(hit.text, schema)
                except (ValueError, ValidationError):
                    pass  # stale or corrupt entry: fall through to a live call
                else:
                    record.cache_hit = True
                    record.input_tokens, record.output_tokens = hit.input_tokens, hit.output_tokens
                    return LLMResult(value, self._write(record))

        if self._offline:
            raise CacheMiss(f"{role}/{prompt}: not in the cache (offline; fresh={fresh})")

        t0 = self._clock()
        try:
            next_req = req
            for parse_attempt in range(1, MAX_PARSE_ATTEMPTS + 1):
                completion = self._send(rcfg, next_req, record)
                try:
                    value = _parse(completion.text, schema)
                    break
                except (ValueError, ValidationError) as e:
                    if parse_attempt == MAX_PARSE_ATTEMPTS:
                        raise StructuredOutputError(
                            f"{role}/{prompt}: invalid {schema.__name__} after "
                            f"{MAX_PARSE_ATTEMPTS} attempts: {_short(e)}"
                        ) from e
                    record.repaired = True
                    if isinstance(e, json.JSONDecodeError):
                        # Broken syntax: a fresh sample usually comes out whole, while
                        # echoing the long broken reply back tends to get it broken again.
                        next_req = req
                    else:
                        # Valid JSON, wrong content: the model needs to see what was wrong.
                        next_req = replace(
                            req,
                            user=req.user
                            + REPAIR_SUFFIX.format(error=_short(e), reply=completion.text[:4000]),
                        )
        except Exception as e:
            record.error = f"{type(e).__name__}: {e}"
            record.latency_ms = int((self._clock() - t0) * 1000)
            self._write(record)
            raise

        record.latency_ms = int((self._clock() - t0) * 1000)
        if write_cache:
            self._cache.put(
                key,
                rcfg.provider,
                rcfg.model,
                completion.text,
                record.input_tokens,
                record.output_tokens,
            )
        return LLMResult(value, self._write(record))

    def _send(
        self, rcfg: RoleConfig, req: CompletionRequest, record: "_CallRecorder"
    ) -> Completion:
        provider = self._provider(rcfg.provider)
        limiter = self._limiter(rcfg.provider, rcfg.model)
        est_output = req.max_output_tokens // 2
        estimate = (len(req.system) + len(req.user)) // 4 + est_output
        retry = self._config.retry
        for attempt in range(1, retry.max_attempts + 1):
            slot = limiter.acquire(estimate, est_output)
            record.attempts += 1
            try:
                completion = provider.complete(req)
            except ProviderError as e:
                limiter.settle(slot, 0, 0)
                record.retry_errors.append(str(e)[:300])
                if not e.retryable or attempt == retry.max_attempts:
                    raise
                backoff = min(retry.max_delay_s, retry.base_delay_s * 2 ** (attempt - 1))
                # A provider's retry hint is a floor, not the whole wait: Groq says "retry in
                # 0.54 s" for per-minute token caps, and four such retries all fail.
                # Jitter only our own backoff; never shorten a provider's stated wait.
                if e.retry_after is not None:
                    delay = max(e.retry_after, backoff)
                else:
                    delay = backoff * (0.5 + 0.5 * self._rng())
                self._sleep(delay)
                continue
            used = (completion.input_tokens or 0) + (completion.output_tokens or 0)
            limiter.settle(slot, used or None, completion.output_tokens)
            record.add_tokens(completion)
            return completion
        raise AssertionError("unreachable")

    def _provider(self, name: str) -> Provider:
        with self._registry_lock:
            if name not in self._providers:
                self._providers[name] = self._factory(name)
            return self._providers[name]

    def _limiter(self, provider: str, model: str) -> RateLimiter:
        k = (provider, model)
        with self._registry_lock:
            return self._limiters.get(k) or self._new_limiter(provider, model)

    def _new_limiter(self, provider: str, model: str) -> RateLimiter:
        k = (provider, model)
        if k not in self._limiters:
            pcfg = self._config.providers[provider]
            self._limiters[k] = RateLimiter(
                usage_label(provider, pcfg.api_key_env),
                model,
                pcfg.limits_for(model),
                self._usage,
                pcfg.rpd_reset_tz,
                clock=self._clock,
                sleep=self._sleep,
            )
        return self._limiters[k]

    def _write(self, record: "_CallRecorder") -> LLMCall:
        call = record.build()
        self._log.record(call)
        return call


class _CallRecorder:
    def __init__(
        self,
        role: str,
        rcfg: RoleConfig,
        rendered: RenderedPrompt,
        key: str,
        evaluation_id: str | None,
    ) -> None:
        self.role = role
        self.rcfg = rcfg
        self.rendered = rendered
        self.key = key
        self.evaluation_id = evaluation_id
        self.cache_hit = False
        self.repaired = False
        self.attempts = 0
        self.input_tokens: int | None = None
        self.output_tokens: int | None = None
        self.latency_ms: int | None = None
        self.error: str | None = None
        self.retry_errors: list[str] = []

    def add_tokens(self, c: Completion) -> None:
        if c.input_tokens is not None:
            self.input_tokens = (self.input_tokens or 0) + c.input_tokens
        if c.output_tokens is not None:
            self.output_tokens = (self.output_tokens or 0) + c.output_tokens

    def build(self) -> LLMCall:
        return LLMCall(
            call_id=uuid.uuid4().hex,
            timestamp=datetime.now(UTC),
            role=self.role,
            provider=self.rcfg.provider,
            model=self.rcfg.model,
            prompt_name=self.rendered.name,
            prompt_version=self.rendered.version,
            prompt_hash=self.rendered.template_hash,
            request_key=self.key,
            retry_errors=self.retry_errors,
            cache_hit=self.cache_hit,
            repaired=self.repaired,
            attempts=self.attempts,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
            latency_ms=self.latency_ms,
            error=self.error,
            evaluation_id=self.evaluation_id,
        )


def _parse[T: BaseModel](text: str, schema: type[T]) -> T:
    return schema.model_validate(extract_json(text))


def _short(e: Exception, limit: int = 1500) -> str:
    s = str(e)
    return s if len(s) <= limit else s[:limit] + "..."
