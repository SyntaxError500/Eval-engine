from typing import Any

import ollama

from eval_engine.providers.base import (
    Completion,
    CompletionRequest,
    ProviderError,
    is_retryable_status,
)


class OllamaProvider:
    name = "ollama"

    def __init__(self, host: str, timeout_s: float = 600.0) -> None:
        self._host = host
        self._client = ollama.Client(host=host, timeout=timeout_s)

    def complete(self, req: CompletionRequest) -> Completion:
        kwargs: dict[str, Any] = {}
        # reasoning_effort: None -> model default; "none" -> thinking off; else passed through.
        if req.reasoning_effort is not None:
            kwargs["think"] = False if req.reasoning_effort == "none" else req.reasoning_effort
        try:
            resp = self._client.chat(
                model=req.model,
                messages=[
                    {"role": "system", "content": req.system},
                    {"role": "user", "content": req.user},
                ],
                format=req.json_schema,
                options={"temperature": req.temperature, "num_predict": req.max_output_tokens},
                **kwargs,
            )
        except ollama.ResponseError as e:
            hint = f" (run `ollama pull {req.model}`)" if e.status_code == 404 else ""
            raise ProviderError(
                f"ollama {e.status_code}: {e.error}{hint}",
                retryable=is_retryable_status(e.status_code),
                status=e.status_code,
            ) from e
        except ConnectionError as e:
            raise ProviderError(
                f"cannot reach Ollama at {self._host}; is it running? ({e})", retryable=False
            ) from e

        text = resp.message.content
        if not text:
            raise ProviderError("ollama returned empty content", retryable=False)
        return Completion(
            text=text, input_tokens=resp.prompt_eval_count, output_tokens=resp.eval_count
        )
