"""Scripted provider for tests. Never makes network calls."""

from collections.abc import Callable, Iterable

from eval_engine.providers.base import Completion, CompletionRequest, ProviderError

Step = str | Completion | ProviderError | Callable[[CompletionRequest], str]


class FakeProvider:
    def __init__(self, script: Iterable[Step] = (), name: str = "fake") -> None:
        self.name = name
        self._script = list(script)
        self.requests: list[CompletionRequest] = []

    def push(self, *steps: Step) -> None:
        self._script.extend(steps)

    def complete(self, req: CompletionRequest) -> Completion:
        self.requests.append(req)
        if not self._script:
            raise AssertionError(f"FakeProvider {self.name!r} ran out of scripted responses")
        step = self._script.pop(0)
        if isinstance(step, ProviderError):
            raise step
        if isinstance(step, Completion):
            return step
        text = step(req) if callable(step) else step
        return Completion(text=text, input_tokens=len(req.user) // 4, output_tokens=len(text) // 4)
