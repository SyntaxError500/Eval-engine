"""Stage 2 orchestrator: evaluate(question, answer) -> stored EvaluationTrace.

Routes by task type (creative skips path identification and amendment), makes the judge
call, repairs malformed judge output, applies the code checks (a met verdict resting on a
statement the judge flagged as wrong, unquoted evidence, sentence counts), aggregates into dimension
scores and bands, flags low path confidence for the Phase 5 amendment stage, and stores the
full trace. Optionally (decision D6) a borderline result is re-judged and decided by a
majority of votes.
"""

import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from eval_engine.config import load_weights
from eval_engine.evaluation.aggregate import Bands, dimension_scores, load_bands, overall_score
from eval_engine.evaluation.counts import apply_count_checks
from eval_engine.evaluation.evidence import apply_error_contradictions, apply_evidence_check
from eval_engine.providers.client import LLMClient
from eval_engine.schemas.common import TaskType
from eval_engine.schemas.judge import (
    ClaimError,
    CreativeJudgeOutput,
    JudgeOutput,
    PathConfidence,
    Verdict,
)
from eval_engine.schemas.question import Question
from eval_engine.schemas.rubric import Rubric, SolutionPath
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.storage.rubric_store import RubricStore


@dataclass
class _Judged:
    path: SolutionPath
    confidences: list[PathConfidence]
    verdicts: list[Verdict]
    errors: list[ClaimError]
    overlap: list[int]
    call_id: str


def evaluate(
    client: LLMClient,
    rubrics: RubricStore,
    questions: QuestionStore,
    evaluations: EvaluationStore,
    question_id: str,
    answer: str,
    *,
    votes: int = 1,
    bands: Bands | None = None,
    weights: dict[str, dict[str, float]] | None = None,
) -> EvaluationTrace:
    bands = bands or load_bands()
    weights = weights or load_weights()
    q = questions.get(question_id)
    original = rubrics.get(q.rubric_hash)
    rubric = rubrics.latest(q.rubric_id)  # an accepted amendment (Phase 5) is a newer version
    evaluation_id = uuid.uuid4().hex
    creative = q.task_type == TaskType.CREATIVE

    judged = [_judge(client, q, rubric, answer, evaluation_id, fresh=False)]
    if votes > 1 and _borderline(judged[0], creative, bands):
        # Extra votes bypass the cache read and don't overwrite the first answer's cache.
        judged += [
            _judge(client, q, rubric, answer, evaluation_id, fresh=True) for _ in range(votes - 1)
        ]
    result = _majority(judged) if len(judged) > 1 else judged[0]

    criteria = result.path.criteria
    verdicts, contradicted = apply_error_contradictions(result.verdicts, result.errors)
    verdicts, downgraded = apply_evidence_check(verdicts, criteria, answer)
    verdicts, counted = apply_count_checks(verdicts, criteria, answer)
    scores = dimension_scores(
        result.path.criteria, verdicts, n_errors=len(result.errors), task_type=q.task_type
    )
    max_conf = max((p.confidence for p in result.confidences), default=0.0)
    trace = EvaluationTrace(
        evaluation_id=evaluation_id,
        timestamp=datetime.now(UTC),
        question_id=q.question_id,
        task_type=q.task_type,
        rubric_hash_original=original.hash or "",
        rubric_hash_used=rubric.hash or "",
        creative_route=creative,
        path_confidences=result.confidences,
        identified_path=None if creative else result.path.path_id,
        final_rubric_source=rubric.source,
        verdicts=verdicts,
        errors=result.errors,
        evidence_downgrades=downgraded,
        contradiction_downgrades=contradicted,
        count_overrides=counted,
        low_confidence=(not creative) and max_conf < bands.amendment_confidence_threshold,
        obvious_overlap=[
            rubric.obvious_answers[i - 1]
            for i in result.overlap
            if 1 <= i <= len(rubric.obvious_answers)
        ],
        judge_votes=len(judged),
        dimension_scores=scores,
        overall_score=overall_score(scores, weights[q.task_type.value]),
        bands={d: bands.label(s) for d, s in scores.items()},
        call_ids=[j.call_id for j in judged],
    )
    evaluations.save(trace)
    return trace


def _judge(
    client: LLMClient,
    q: Question,
    rubric: Rubric,
    answer: str,
    evaluation_id: str,
    *,
    fresh: bool,
) -> _Judged:
    if q.task_type == TaskType.CREATIVE:
        path = rubric.paths[0]
        res = client.complete(
            "judge",
            "score_creative",
            {
                "question": rubric.question,
                "criteria": [c.model_dump(mode="json") for c in path.criteria],
                "obvious_answers": rubric.obvious_answers,
                "answer": answer,
            },
            CreativeJudgeOutput,
            evaluation_id=evaluation_id,
            fresh=fresh,
            write_cache=not fresh,
        )
        c_out = res.value
        return _Judged(
            path, [], _complete(path, c_out.verdicts), [], c_out.obvious_overlap, res.call.call_id
        )

    variables: dict[str, Any] = {
        "question": rubric.question,
        "paths": [p.model_dump(mode="json") for p in rubric.paths],
        "answer": answer,
    }
    res2 = client.complete(
        "judge",
        "score_answer",
        variables,
        JudgeOutput,
        evaluation_id=evaluation_id,
        fresh=fresh,
        write_cache=not fresh,
    )
    out = res2.value
    path = _resolve_path(rubric, out)
    return _Judged(
        path, out.path_confidences, _complete(path, out.verdicts), out.errors, [], res2.call.call_id
    )


def _resolve_path(rubric: Rubric, out: JudgeOutput) -> SolutionPath:
    """The judge's path if it exists, else the valid path it was most confident in."""
    ids = {p.path_id for p in rubric.paths}
    if out.identified_path in ids:
        return rubric.path(out.identified_path)
    ranked = sorted(
        (pc for pc in out.path_confidences if pc.path_id in ids),
        key=lambda pc: pc.confidence,
        reverse=True,
    )
    return rubric.path(ranked[0].path_id) if ranked else rubric.paths[0]


def _complete(path: SolutionPath, verdicts: list[Verdict]) -> list[Verdict]:
    """One verdict per criterion of the path, in rubric order; a missing one is not met."""
    by_id = {v.criterion_id: v for v in verdicts}
    return [
        by_id.get(c.criterion_id)
        or Verdict(
            criterion_id=c.criterion_id,
            met=False,
            evidence="",
            justification="[no verdict returned by the judge]",
        )
        for c in path.criteria
    ]


def _borderline(j: _Judged, creative: bool, bands: Bands) -> bool:
    """D6: re-judge when the outcome hinges on one call: low path confidence, or exactly one
    core criterion unmet (one flipped verdict changes whether the answer is fully correct)."""
    if not creative:
        max_conf = max((p.confidence for p in j.confidences), default=0.0)
        if max_conf < bands.amendment_confidence_threshold:
            return True
    met = {v.criterion_id: v.met for v in j.verdicts}
    unmet_core = [c for c in j.path.criteria if c.core and not met.get(c.criterion_id, False)]
    return len(unmet_core) == 1


def _majority(judged: list[_Judged]) -> _Judged:
    """Most common path; on it, each criterion takes the majority verdict (ties: not met).
    Errors count if a majority of votes on that path reported any."""
    path_id = Counter(j.path.path_id for j in judged).most_common(1)[0][0]
    on_path = [j for j in judged if j.path.path_id == path_id]
    first = on_path[0]
    verdicts: list[Verdict] = []
    for c in first.path.criteria:
        votes = [next(v for v in j.verdicts if v.criterion_id == c.criterion_id) for j in on_path]
        yes = [v for v in votes if v.met]
        winner = yes[0] if len(yes) * 2 > len(votes) else next(v for v in votes if not v.met)
        verdicts.append(winner)
    with_errors = [j for j in on_path if j.errors]
    errors = with_errors[0].errors if len(with_errors) * 2 > len(on_path) else []
    overlap_votes = Counter(i for j in on_path for i in set(j.overlap))
    overlap = sorted(i for i, n in overlap_votes.items() if n * 2 > len(on_path))
    return _Judged(first.path, first.confidences, verdicts, errors, overlap, first.call_id)
