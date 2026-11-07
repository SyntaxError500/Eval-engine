"""Live check of the discussion and re-check fixes (Phase 8, after the Java session).

Scenarios and expected outcomes, fixed before the first run:

Tutor (local qwen3:8b, `tutor_chat` v3):
- T1 Java replay: the learner's 7 objections from the live session, verbatim, on the same
  answer and grading. Expected: no reply repeats an earlier one (triple overlap below the
  threshold, or the fixed fallback reply instead), the objections are read as challenges, and
  the replies name what is right (own implementation, runtime dispatch) as well as the error.
- T2 Java, acknowledgement then a new question. Expected: the parameter rule is not explained
  again after the learner accepts it.
- T3 Balloon (human-set A47), an invalid challenge insisting a wrong fact is right. Expected:
  the tutor holds that "hot air is more dense" is wrong; it doesn't give way.

Re-check (judge model, `recheck` v1, one call each):
- R1 Java, the learner's real argument (weighting, not a wrong verdict). Expected: no
  decision changes; the concern that return types aren't asked for goes to rubric_concern.
- R2 Java, an invalid argument that the parameter statement is correct. Expected: the error
  stands and nothing changes.
- R3 Literary movements (A13), the grader miscounted: Naturalism with Zola's Germinal is the
  second movement named. Both human graders marked P1.C4 met. Expected: P1.C4 revised to met.
- R4 Balloon (A47), the cooler-surrounding-air point was knocked out because it shares a
  sentence with a real error. Both human graders marked P1.C3 met. Expected: P1.C3 revised;
  the error stands.
- R5 A08 (three real errors; both graders "incorrect"), the learner claims every fact is
  right. Expected: no change.

Added after the first run (R1-R5) exposed R5, and before any rerun: held-out appeals the
prompt and code changes were not written against.
- R6 Cell cycle (A34), three phases swapped; the learner insists they are right. Both
  graders "incorrect". Expected: no change.
- R7 Rain shadow (A25), two real errors; the learner argues blocked sunlight is a valid
  explanation. Both graders "incorrect". Expected: no change.
- R8 Airplane (A26), an answer to a different question; the learner says the listed
  statement is true. Expected: no change (off-topic answers can't move).

Everything runs on a scratch database; model calls are logged and counted as usual.
"""

import json
import random
import sqlite3
from pathlib import Path
from typing import Any

from eval_engine.config import REPO_ROOT, AppConfig
from eval_engine.providers.factory import build_client
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.service import EngineService, Submission
from eval_engine.storage import RubricStore, connect
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.tutor import FALLBACK_REPLY, _triples

OUT_DIR = REPO_ROOT / "experiments" / "8_interface" / "discussion_check"
HUMAN = REPO_ROOT / "experiments" / "7_validation" / "human"
JAVA_SUBMISSION = "f417e277"  # live session, 2026-11-07

JAVA_ARGUMENT = (
    "I agree the parameter statement is wrong, but correctness should not be Not yet: my answer "
    "correctly says the child class provides its own implementation and that a parent "
    "reference calls the child's method at runtime. Return types and access modifiers are "
    "extra rules the question doesn't ask about, so completeness shouldn't fail on them."
)
JAVA_INVALID = (
    "My statement about different parameters is correct: in Java a subclass method with "
    "different parameters still overrides the parent method, so it is not an error."
)
T2 = [
    "OK, I accept that an overriding method needs the same parameters; that was my mistake.",
    "What do I need to know about return types for overriding?",
    "And why does it matter at runtime which object the reference points to?",
]
T3 = [
    "Hot air really is more dense than cold air, that's why it rises. My answer is right.",
    "I'm sure about it. Denser things rise. Please mark it correct.",
]
R_ARGS = {
    "R3": (
        "A13",
        "I named two movements: Realism with Flaubert's Madame Bovary and Naturalism with "
        "Zola's Germinal. Naturalism is the second movement and it has a work and an author.",
    ),
    "R4": (
        "A47",
        "My answer says the balloon displaces cooler surrounding air that is heavier, which is "
        "the contrast with the outside air that the requirement asks for.",
    ),
    "R5": ("A08", "Every fact in my answer is correct. Please check again and remove the errors."),
    "R6": (
        "A34",
        "My phases are right: the cell copies its DNA in G1, divides in S and grows in M. "
        "Please remove the errors.",
    ),
    "R7": (
        "A25",
        "Mountains blocking the sunlight is a valid explanation for the dry leeward side, and "
        "the Himalayas are dry on one side, so my reasoning should be credited.",
    ),
    "R8": (
        "A26",
        "The statement you listed as wrong is true: faster air over the wing does lower the "
        "pressure and produce lift. It is not a factual error.",
    ),
}


def _scratch_service(
    real: sqlite3.Connection,
    config: AppConfig,
    tmp: Path,
    question_id: str,
    answer: str,
    trace: EvaluationTrace,
) -> tuple[EngineService, str]:
    s = connect(":memory:")
    q = QuestionStore(real).get(question_id)
    for h in {q.rubric_hash, trace.rubric_hash_used}:
        RubricStore(s).save(RubricStore(real).get(h))
    QuestionStore(s).save(q)
    EvaluationStore(s).save(trace)
    bank = tmp / f"bank_{question_id}.json"
    bank.write_text(json.dumps([]), encoding="utf-8")
    svc = EngineService(s, build_client(config, real), config, bank_file=bank, rng=random.Random(0))
    sub = Submission("check-" + trace.evaluation_id[:8], question_id, answer, "done",
                     trace.evaluation_id, 1, None, trace.timestamp.isoformat())  # fmt: skip
    svc._save(sub)  # a graded submission, as the app would have stored it
    return svc, sub.submission_id


def _java(real: sqlite3.Connection) -> tuple[str, str, EvaluationTrace, list[str]]:
    row = real.execute(
        "SELECT * FROM submissions WHERE submission_id LIKE ?", (JAVA_SUBMISSION + "%",)
    ).fetchone()
    trace = EvaluationStore(real).get(row["evaluation_id"])
    learner = [
        r["text"]
        for r in real.execute(
            "SELECT text FROM discussions WHERE submission_id = ? AND role = 'learner' "
            "ORDER BY turn",
            (row["submission_id"],),
        )
    ]
    return row["question_id"], row["answer"], trace, learner


def _human(answer_id: str) -> tuple[str, str, EvaluationTrace]:
    engine = json.loads((HUMAN / "engine_maj3.json").read_text(encoding="utf-8"))[answer_id]
    key = {a["answer_id"]: a for a in json.loads((HUMAN / "key.json").read_text("utf-8"))}
    trace = EvaluationTrace.model_validate(engine["trace"])
    return key[answer_id]["question_id"], key[answer_id]["text"], trace


def _talk(svc: EngineService, sid: str, messages: list[str]) -> dict[str, Any]:
    turns: list[dict[str, Any]] = []
    for m in messages:
        t = svc.discuss(sid, m)
        turns.append({"learner": m, "tutor": t.text, "meta": t.meta})
    replies = [t["tutor"] for t in turns]
    overlaps = []
    for i, a in enumerate(replies):
        for b in replies[:i]:
            ta, tb = _triples(a), _triples(b)
            if ta and tb and a != FALLBACK_REPLY and b != FALLBACK_REPLY:
                overlaps.append(round(len(ta & tb) / min(len(ta), len(tb)), 2))
    return {
        "turns": turns,
        "max_overlap": max(overlaps, default=0.0),
        "fallbacks": sum(1 for t in turns if t["meta"].get("fallback")),
        "rejected_drafts": sum(int(t["meta"].get("rejected_drafts", 0)) for t in turns),
        "kinds": [t["meta"].get("kind") for t in turns],
    }


def _recheck(svc: EngineService, sid: str, argument: str) -> dict[str, Any]:
    r = svc.recheck(sid, argument)
    return {"argument": argument, **r.to_json()}


def run(real: sqlite3.Connection, config: AppConfig, tmp: Path, only: set[str]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    qid, answer, trace, learner = _java(real)
    if "T1" in only:
        svc, sid = _scratch_service(real, config, tmp, qid, answer, trace)
        results["T1"] = _talk(svc, sid, learner)
    if "T2" in only:
        svc, sid = _scratch_service(real, config, tmp, qid, answer, trace)
        results["T2"] = _talk(svc, sid, T2)
    if "T3" in only:
        hq, ha, ht = _human("A47")
        svc, sid = _scratch_service(real, config, tmp, hq, ha, ht)
        results["T3"] = _talk(svc, sid, T3)
    for name, argument in (("R1", JAVA_ARGUMENT), ("R2", JAVA_INVALID)):
        if name in only:
            svc, sid = _scratch_service(real, config, tmp, qid, answer, trace)
            results[name] = _recheck(svc, sid, argument)
    for name, (answer_id, argument) in R_ARGS.items():
        if name in only:
            hq, ha, ht = _human(answer_id)
            svc, sid = _scratch_service(real, config, tmp, hq, ha, ht)
            results[name] = _recheck(svc, sid, argument)
    return results


def report(results: dict[str, Any]) -> str:
    lines = [
        "# Discussion and re-check: live check",
        "",
        "Scenarios and expectations: `src/eval_engine/validation/discussion_check.py`, fixed "
        "before the run.",
        "",
    ]
    for name, r in results.items():
        lines.append(f"## {name}")
        lines.append("")
        if "turns" in r:
            lines.append(
                f"Max overlap between replies: {r['max_overlap']} · fallbacks: {r['fallbacks']}"
                f" · drafts rejected by code: {r['rejected_drafts']} · read as: {r['kinds']}"
            )
            lines.append("")
            for t in r["turns"]:
                lines += [f"**Learner:** {t['learner']}", "", f"**Tutor:** {t['tutor']}", ""]
        else:
            out = r["output"]
            lines += [
                f"**Appeal:** {r['argument']}",
                "",
                f"- changed: {r['changed']}; revised: {r['revised']}; refused (no quote): "
                f"{r['refused']}; refused (quotes a wrong statement): {r['contradicted']}; "
                f"off-topic: {r['off_topic']}; errors dropped: {r['errors_dropped']}",
                f"- bands: {r['bands_before']} -> {r['bands_after']}",
                f"- severity: {out['severity']}; rubric concern: {out['rubric_concern']}",
                "- decisions: "
                + str([(d["criterion_id"], d["decision"], d["reason"]) for d in out["criteria"]]),
                f"- errors: {[(e['error'], e['stands'], e['reason']) for e in out['errors']]}",
                f"- summary: {out['summary']}",
                "",
            ]  # fmt: skip
    return "\n".join(lines)
