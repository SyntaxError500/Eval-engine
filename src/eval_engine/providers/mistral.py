from typing import Any

import httpx2  # the HTTP client mistralai 3.x is built on
from mistralai.client import Mistral, errors
from mistralai.client.models.jsonschema import JSONSchema
from mistralai.client.models.responseformat import ResponseFormat

from eval_engine.providers.base import (
    Completion,
    CompletionRequest,
    ProviderError,
    is_retryable_status,
)


class MistralProvider:
    name = "mistral"

    def __init__(self, api_key: str, timeout_ms: int = 120_000) -> None:
        self._client = Mistral(api_key=api_key, timeout_ms=timeout_ms)

    def complete(self, req: CompletionRequest) -> Completion:
        kwargs: dict[str, Any] = {}
        if req.json_schema is not None:
            kwargs["response_format"] = ResponseFormat(
                type="json_schema",
                json_schema=JSONSchema(
                    name=req.schema_name, schema_definition=req.json_schema, strict=False
                ),
            )
        if req.reasoning_effort is not None:
            kwargs["reasoning_effort"] = req.reasoning_effort
        messages: list[Any] = [
            {"role": "system", "content": req.system},
            {"role": "user", "content": req.user},
        ]
        try:
            resp = self._client.chat.complete(
                model=req.model,
                messages=messages,
                temperature=req.temperature,
                max_tokens=req.max_output_tokens,
                **kwargs,
            )
        except errors.SDKError as e:
            raise ProviderError(
                f"mistral {e.status_code}: {e.body or e}",
                retryable=is_retryable_status(e.status_code),
                status=e.status_code,
            ) from e
        except errors.NoResponseError as e:
            raise ProviderError(f"mistral no response: {e}", retryable=True) from e
        except (httpx2.TransportError, OSError) as e:
            raise ProviderError(f"mistral network error: {e}", retryable=True) from e

        if not resp.choices or resp.choices[0].message is None:
            raise ProviderError("mistral returned no message", retryable=False)
        text = _content_text(resp.choices[0].message.content)
        if not text:
            raise ProviderError("mistral returned empty content", retryable=False)
        usage = resp.usage
        return Completion(
            text=text,
            input_tokens=usage.prompt_tokens if usage else None,
            output_tokens=usage.completion_tokens if usage else None,
        )


def _content_text(content: Any) -> str:
    """Content is a string, or a list of chunks for some models (e.g. with reasoning)."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = [getattr(c, "text", None) for c in content if getattr(c, "type", None) == "text"]
    return "".join(p for p in parts if p)
