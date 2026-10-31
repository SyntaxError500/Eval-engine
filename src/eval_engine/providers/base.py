"""Provider protocol. Adapters translate one request shape to each SDK and map its errors."""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class CompletionRequest:
    model: str
    system: str
    user: str
    json_schema: dict[str, Any] | None
    schema_name: str
    temperature: float
    max_output_tokens: int
    reasoning_effort: str | None = None
    # "schema": provider-side constrained decoding against json_schema.
    # "strict": constrained decoding with every field required and the object closed.
    # "object": plain JSON mode; the schema goes into the system prompt instead. Some
    # provider/model pairs break under constrained decoding (Groq + Qwen, 2026-10-28).
    json_mode: str = "schema"


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class ProviderError(Exception):
    def __init__(
        self,
        message: str,
        *,
        retryable: bool,
        status: int | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status = status
        self.retry_after = retry_after


class QuotaExhausted(ProviderError):
    """Daily quota reached. Not retryable within this run."""

    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=False)


class Provider(Protocol):
    name: str

    def complete(self, req: CompletionRequest) -> Completion: ...


def is_retryable_status(status: int | None) -> bool:
    return status is not None and (status in (408, 429) or status >= 500)
