"""Verifier: a different model family tries to break a proposed path (design doc §8).

It sees the path and the proposer's justification, never the learner's answer: an accepted
path joins the rubric for every later answer, so it has to stand on its own, however well
this answer was written.
"""

from eval_engine.providers.client import LLMClient, LLMResult
from eval_engine.schemas.amendment import Framing, VerifierVerdict
from eval_engine.schemas.rubric import Rubric, SolutionPath


def verify(
    client: LLMClient,
    rubric: Rubric,
    path: SolutionPath,
    justification: str,
    framing: Framing,
    *,
    evaluation_id: str | None = None,
) -> LLMResult[VerifierVerdict]:
    return client.complete(
        "verifier",
        "amendment_verify",
        {
            "framing": framing,
            "question": rubric.question,
            "existing_paths": [p.model_dump(mode="json") for p in rubric.paths],
            "proposed": path.model_dump(mode="json"),
            "justification": justification,
        },
        VerifierVerdict,
        evaluation_id=evaluation_id,
    )
