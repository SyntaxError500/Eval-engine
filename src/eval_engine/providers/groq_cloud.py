from typing import Any

import groq

from eval_engine.providers.base import (
    Completion,
    CompletionRequest,
    ProviderError,
    is_retryable_status,
)


class GroqProvider:
    name = "groq"

    def __init__(self, api_key: str, timeout_s: float = 120.0) -> None:
        # Retries are handled by LLMClient so they are counted against our rate limits.
        self._client = groq.Groq(api_key=api_key, max_retries=0, timeout=timeout_s)

    def complete(self, req: CompletionRequest) -> Completion:
        kwargs: dict[str, Any] = {}
        if req.json_schema is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": req.schema_name,
                    "schema": req.json_schema,
                    "strict": False,
                },
            }
        if req.reasoning_effort is not None:
            kwargs["reasoning_effort"] = req.reasoning_effort
        try:
            resp = self._client.chat.completions.create(
                model=req.model,
                messages=[
                    {"role": "system", "content": req.system},
                    {"role": "user", "content": req.user},
                ],
                temperature=req.temperature,
                max_completion_tokens=req.max_output_tokens,
                **kwargs,
            )
        except groq.RateLimitError as e:
            raise ProviderError(
                f"groq 429: {e.message}",
                retryable=True,
                status=429,
                retry_after=_retry_after(e.response.headers.get("retry-after")),
            ) from e
        except groq.APIStatusError as e:
            failed = _failed_generation(e.body)
            if failed is not None:
                # Groq validates JSON server-side and rejects malformed output with a 400.
                # Hand the bad text back so LLMClient's schema repair can retry it, exactly as
                # if the model had returned it to us.
                return Completion(text=failed)
            raise ProviderError(
                f"groq {e.status_code}: {e.message}",
                retryable=is_retryable_status(e.status_code),
                status=e.status_code,
            ) from e
        except groq.APIConnectionError as e:  # includes timeouts
            raise ProviderError(f"groq connection error: {e}", retryable=True) from e

        if not resp.choices or not resp.choices[0].message.content:
            raise ProviderError("groq returned empty content", retryable=False)
        usage = resp.usage
        return Completion(
            text=resp.choices[0].message.content,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
        )


def _failed_generation(body: object) -> str | None:
    """The model's rejected output, if this is Groq's json_validate_failed error."""
    if not isinstance(body, dict):
        return None
    err = body.get("error", body)
    if not isinstance(err, dict) or err.get("code") != "json_validate_failed":
        return None
    text = err.get("failed_generation")
    return text if isinstance(text, str) else ""


def _retry_after(value: str | None) -> float | None:
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None
