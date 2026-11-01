"""Proposer: does this answer contain a valid approach the rubric doesn't cover?

It sees the question, the answer and the existing path descriptions (so it doesn't re-propose
them), never the judge's scores, so it isn't anchored on "a mismatch means an error" (design
doc §7). A proposal that fails the rubric checks goes back once with the problems.
"""

from dataclasses import dataclass, field
from typing import Any

from eval_engine.generation.consistency import check_path, required_dimensions
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.amendment import AmendmentProposal, ProposedPath
from eval_engine.schemas.rubric import Criterion, Rubric, SolutionPath

PROPOSAL_ATTEMPTS = 2
PROPOSED_CRITERION_WEIGHT = 1.0  # 195 of the 210 accepted rubric criteria weigh 1.0


@dataclass
class ProposalResult:
    proposal: AmendmentProposal
    path: SolutionPath | None  # set when the proposal is usable
    problems: list[str] = field(default_factory=list)  # checks the last attempt failed
    call_ids: list[str] = field(default_factory=list)


def as_solution_path(rubric: Rubric, proposed: ProposedPath) -> SolutionPath:
    path_id = f"P{len(rubric.paths) + 1}"
    return SolutionPath(
        path_id=path_id,
        description=proposed.description,
        criteria=[
            Criterion(
                criterion_id=f"{path_id}.C{i}",
                dimension=c.dimension,
                statement=c.statement,
                evidence_hint=c.evidence_hint,
                core=c.core,
                weight=PROPOSED_CRITERION_WEIGHT,
                requires=c.requires,
            )
            for i, c in enumerate(proposed.criteria, start=1)
        ],
    )


def propose(
    client: LLMClient,
    rubric: Rubric,
    answer: str,
    weights: dict[str, dict[str, float]],
    *,
    evaluation_id: str | None = None,
) -> ProposalResult:
    variables: dict[str, Any] = {
        "question": rubric.question,
        "task_type": rubric.task_type.value,
        "required_dimensions": sorted(required_dimensions(rubric.task_type, weights)),
        "existing_paths": [p.description for p in rubric.paths],
        "answer": answer,
        "problems": [],
    }
    result: ProposalResult | None = None
    call_ids: list[str] = []
    for _ in range(PROPOSAL_ATTEMPTS):
        res = client.complete(
            "amendment_proposer",
            "amendment_propose",
            variables,
            AmendmentProposal,
            evaluation_id=evaluation_id,
        )
        call_ids.append(res.call.call_id)
        proposal = res.value
        if not proposal.is_new_valid_approach or proposal.proposed_path is None:
            return ProposalResult(proposal, None, call_ids=call_ids)
        path = as_solution_path(rubric, proposal.proposed_path)
        problems = check_path(rubric, path, weights)
        if not problems:
            return ProposalResult(proposal, path, call_ids=call_ids)
        result = ProposalResult(proposal, None, problems, call_ids)
        variables["problems"] = problems
    assert result is not None
    return result
