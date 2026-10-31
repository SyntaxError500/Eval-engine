import re

import httpx
from google import genai
from google.genai import errors, types

from eval_engine.providers.base import (
    Completion,
    CompletionRequest,
    ProviderError,
    QuotaExhausted,
    is_retryable_status,
)


class GeminiProvider:
    name = "gemini"

    def __init__(self, api_key: str, timeout_ms: int = 90_000) -> None:
        # Without a timeout a stalled request can hang for minutes before the retry kicks in.
        self._client = genai.Client(
            api_key=api_key, http_options=types.HttpOptions(timeout=timeout_ms)
        )

    def complete(self, req: CompletionRequest) -> Completion:
        config = types.GenerateContentConfig(
            system_instruction=req.system,
            temperature=req.temperature,
            max_output_tokens=req.max_output_tokens,
            response_mime_type="application/json" if req.json_schema else None,
            response_json_schema=req.json_schema,
        )
        try:
            resp = self._client.models.generate_content(
                model=req.model, contents=req.user, config=config
            )
        except errors.APIError as e:
            message = str(e.message or "")
            if e.code == 429 and _is_daily_limit(message):
                raise QuotaExhausted(f"gemini daily limit: {message[:300]}") from e
            raise ProviderError(
                f"gemini {e.code}: {message}",
                retryable=is_retryable_status(e.code),
                status=e.code,
                # Google says how long the per-minute window needs; another process may have
                # used it, which our in-process limiter cannot see.
                retry_after=_retry_after(message) if e.code == 429 else None,
            ) from e
        except (httpx.TransportError, OSError) as e:
            raise ProviderError(f"gemini network error: {e}", retryable=True) from e

        text = resp.text
        if not text:
            finish = resp.candidates[0].finish_reason if resp.candidates else None
            raise ProviderError(
                f"gemini returned no text (finish_reason={finish})", retryable=False
            )
        usage = resp.usage_metadata
        return Completion(
            text=text,
            input_tokens=usage.prompt_token_count if usage else None,
            output_tokens=usage.candidates_token_count if usage else None,
        )


_RETRY_IN = re.compile(r"retry in ([\d.]+)\s*s", re.IGNORECASE)


def _retry_after(message: str) -> float | None:
    m = _RETRY_IN.search(message)
    return float(m.group(1)) + 1.0 if m else None


def _is_daily_limit(message: str) -> bool:
    m = message.lower()
    return "per day" in m or "perday" in m
