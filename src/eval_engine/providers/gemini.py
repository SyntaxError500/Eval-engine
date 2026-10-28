import httpx
from google import genai
from google.genai import errors, types

from eval_engine.providers.base import (
    Completion,
    CompletionRequest,
    ProviderError,
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
            raise ProviderError(
                f"gemini {e.code}: {e.message}",
                retryable=is_retryable_status(e.code),
                status=e.code,
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
