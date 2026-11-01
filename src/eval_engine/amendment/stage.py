"""Amendment stage: propose -> verify -> on acceptance store rubric version n+1.

The frozen rubric stays binding. Anything short of a verified, accepted path (the proposer
finds nothing, the verifier rejects, a provider is down) leaves the grade on the original
rubric, and the reason is kept for feedback.
"""

import json
from dataclasses import dataclass, field

from eval_engine.amendment.propose import propose
from eval_engine.amendment.verify import verify
from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.schemas.amendment import AmendmentProposal, Framing, VerifierVerdict
from eval_engine.schemas.rubric import Rubric, SolutionPath
from eval_engine.storage.rubric_store import RubricStore


@dataclass
class AmendmentOutcome:
    framing: Framing
    proposal: AmendmentProposal | None = None
    verdict: VerifierVerdict | None = None
    rubric: Rubric | None = None  # the new version, when accepted
    divergence_reason: str | None = None
    error: str | None = None  # the stage couldn't finish; the original rubric stands
    call_ids: list[str] = field(default_factory=list)

    @property
    def proposal_json(self) -> str | None:
        return json.dumps(self.proposal.model_dump(mode="json")) if self.proposal else None


def amended(rubric: Rubric, path: SolutionPath) -> Rubric:
    """Version n+1 with the path appended. Validated, because model_copy wouldn't be."""
    body = rubric.model_dump(mode="json", exclude={"hash"})
    body.update(
        version=rubric.version + 1,
        parent_hash=rubric.hash,
        source="amendment",
        paths=[*body["paths"], path.model_dump(mode="json")],
    )
    return Rubric.model_validate(body).freeze()


def run_amendment(
    client: LLMClient,
    rubrics: RubricStore,
    rubric: Rubric,
    answer: str,
    weights: dict[str, dict[str, float]],
    framing: Framing,
    *,
    evaluation_id: str | None = None,
) -> AmendmentOutcome:
    outcome = AmendmentOutcome(framing)
    try:
        proposed = propose(client, rubric, answer, weights, evaluation_id=evaluation_id)
        outcome.proposal = proposed.proposal
        outcome.call_ids += proposed.call_ids
        if proposed.path is None:
            outcome.divergence_reason = (
                f"proposal failed the rubric checks: {'; '.join(proposed.problems)}"
                if proposed.problems
                else proposed.proposal.justification
            )
            return outcome
        checked = verify(
            client,
            rubric,
            proposed.path,
            proposed.proposal.justification,
            framing,
            evaluation_id=evaluation_id,
        )
    except (ProviderError, StructuredOutputError) as e:
        outcome.error = f"{type(e).__name__}: {str(e)[:300]}"
        return outcome
    outcome.verdict = checked.value
    outcome.call_ids.append(checked.call.call_id)
    if not checked.value.accepted:
        outcome.divergence_reason = checked.value.reasons
        return outcome
    outcome.rubric = amended(rubric, proposed.path)
    rubrics.save(outcome.rubric)
    return outcome
