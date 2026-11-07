"""The engine behind the app (plan Phase 8): question bank, submissions and quota.

Kept separate from the Streamlit page so its behaviour, above all the degradation rules, can
be tested without a browser:

- **The judge is unavailable** (rate-limited, quota spent, provider down): the submission is
  queued, the learner sees "evaluating…", and it is retried later. It is never graded by
  another model, because that would be a silent switch to a judge nobody validated.
- **The verifier is down:** the amendment stage records the error, and the grade stands on the
  original rubric (`amendment/stage.py`).
- **The feedback model is down:** feedback falls back to plain templates, marked as such
  (`feedback/phrase.py`).

After feedback, the learner can discuss the answer with a tutor on the local model (no quota).
The tutor sees how the grade was reached but can't change it; the discussion is stored for the
admin view and never fed back into grading. A learner who disputes a decision can ask for one
re-check, done by the judge's model, which can reverse a decision only with a quote from the
answer (`tutor.py`).

Questions come from the reviewed bank (Phase 3 `accepted.json`) by default. A learner can also
ask for a new question on a topic they describe; it goes through the same generator and checks
as Phase 3 but nobody has reviewed its rubric, so it is always shown as unreviewed.
"""

import json
import random
import sqlite3
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from eval_engine import tutor
from eval_engine.config import REPO_ROOT, AppConfig
from eval_engine.evaluation.aggregate import load_bands
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.generation.generate import GenerationError, generate_question
from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import LLMClient, StructuredOutputError, usage_label
from eval_engine.schemas.common import TaskType
from eval_engine.schemas.feedback import RecheckOutput, TutorReply
from eval_engine.schemas.question import Question
from eval_engine.schemas.rubric import Rubric
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.storage import RubricStore, UsageCounter
from eval_engine.storage.db import lock_for, locked, utc_now
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore

BANK_FILE = REPO_ROOT / "experiments" / "3_generation" / "accepted.json"
MAX_ANSWER_CHARS = 4000
QUOTA_ROLES = (
    "judge",
    "generator",
    "amendment_proposer",
    "verifier",
    "feedback_phraser",
    "rechecker",
    "tutor",
    "tutor_fallback",
)
TOPIC_CHARS = (3, 200)
MAX_MESSAGE_CHARS = 1000
HISTORY_TURNS = 12  # most recent turns sent to the tutor; older ones drop out of its view
MIN_ARGUMENT_CHARS = 15


class AnswerRejected(ValueError):
    """The answer can't be graded as given (empty or too long)."""


class TopicRejected(ValueError):
    """The described topic can't be used (too short or too long)."""


class GenerationFailed(RuntimeError):
    """No question could be generated: the rubric failed its checks or a provider was down."""


class TutorUnavailable(RuntimeError):
    """The tutor (local model) couldn't reply."""


class RecheckUnavailable(RuntimeError):
    """The judge model couldn't do the re-check (quota or provider). Nothing was stored."""


@dataclass
class Turn:
    role: str  # learner | tutor | flag (the learner reported a grading problem)
    text: str
    # For tutor turns: the model's reading of the learner's message (kind, learner_point,
    # accepts), how many drafts the code checks rejected, and whether the fallback was used.
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Submission:
    submission_id: str
    question_id: str
    answer: str
    status: str  # done | queued
    evaluation_id: str | None
    attempts: int
    last_error: str | None
    created_at: str


@dataclass
class Quota:
    role: str
    provider: str
    model: str
    used: int
    limit: int | None

    @property
    def remaining(self) -> int | None:
        return None if self.limit is None else max(0, self.limit - self.used)


class EngineService:
    def __init__(
        self,
        conn: sqlite3.Connection,
        client: LLMClient,
        config: AppConfig,
        *,
        bank_file: Path = BANK_FILE,
        rng: random.Random | None = None,
    ) -> None:
        self._conn = conn
        self._lock = lock_for(conn)
        self._client = client
        self._config = config
        self._rubrics = RubricStore(conn)
        self._questions = QuestionStore(conn)
        self._evaluations = EvaluationStore(conn)
        self._bank = [e["question_id"] for e in json.loads(bank_file.read_text(encoding="utf-8"))]
        self._rng = rng or random.Random()

    # ------------------------------------------------------------ questions

    def topics(self) -> list[str]:
        return sorted({self._questions.get(q).topic for q in self._bank})

    def question_for(self, topic: str, exclude: set[str] | None = None) -> Question:
        pool = [q for q in self._bank if self._questions.get(q).topic == topic]
        fresh = [q for q in pool if q not in (exclude or set())] or pool
        if not fresh:
            raise KeyError(f"no reviewed question for topic {topic!r}")
        return self._questions.get(self._rng.choice(fresh))

    def question(self, question_id: str) -> Question:
        return self._questions.get(question_id)

    def is_reviewed(self, question_id: str) -> bool:
        return question_id in self._bank

    def generate(self, topic: str, task_type: TaskType) -> Question:
        """A new question on a topic the learner describes: generated, code-checked,
        fact-checked and frozen exactly as in Phase 3, but not reviewed by anyone."""
        text = " ".join(topic.split())
        low, high = TOPIC_CHARS
        if len(text) < low:
            raise TopicRejected("describe the topic in a few words")
        if len(text) > high:
            raise TopicRejected(f"keep the topic under {high} characters")
        try:
            return generate_question(
                self._client, self._rubrics, self._questions, text, task_type
            ).question
        except GenerationError as e:
            raise GenerationFailed(
                "the generated question didn't pass the checks: " + "; ".join(e.problems[:3])
            ) from e
        except (ProviderError, StructuredOutputError) as e:
            raise GenerationFailed(
                f"the question generator isn't available right now ({type(e).__name__})"
            ) from e

    # ------------------------------------------------------------ submissions

    def submit(self, question_id: str, answer: str) -> Submission:
        text = answer.strip()
        if not text:
            raise AnswerRejected("write an answer first")
        if len(text) > MAX_ANSWER_CHARS:
            raise AnswerRejected(f"answers are limited to {MAX_ANSWER_CHARS} characters")
        self._questions.get(question_id)  # unknown ids fail here, before anything is stored
        sub = Submission(uuid.uuid4().hex, question_id, text, "queued", None, 0, None, utc_now())
        self._save(sub)
        return self._attempt(sub)

    def retry_queued(self) -> list[Submission]:
        """One more attempt for every queued submission, oldest first."""
        return [self._attempt(s) for s in self.queued()]

    def _attempt(self, sub: Submission) -> Submission:
        sub.attempts += 1
        try:
            trace = evaluate(
                self._client,
                self._rubrics,
                self._questions,
                self._evaluations,
                sub.question_id,
                sub.answer,
                feedback=True,
            )
        except (ProviderError, StructuredOutputError) as e:
            # Amendment and feedback failures are handled inside `evaluate`, so anything that
            # escapes is the judge. Wait for it; never grade with something else.
            sub.status, sub.last_error = "queued", f"{type(e).__name__}: {str(e)[:300]}"
            self._save(sub)
            return sub
        sub.status, sub.evaluation_id, sub.last_error = "done", trace.evaluation_id, None
        self._save(sub)
        return sub

    def get(self, submission_id: str) -> Submission:
        return self._row("SELECT * FROM submissions WHERE submission_id = ?", (submission_id,))[0]

    def queued(self) -> list[Submission]:
        return self._row(
            "SELECT * FROM submissions WHERE status = 'queued' ORDER BY created_at", ()
        )

    def recent(self, limit: int = 50) -> list[Submission]:
        return self._row("SELECT * FROM submissions ORDER BY created_at DESC LIMIT ?", (limit,))

    def trace(self, sub: Submission) -> EvaluationTrace | None:
        return self._evaluations.get(sub.evaluation_id) if sub.evaluation_id else None

    def rubric_history(self, question_id: str) -> list[Rubric]:
        return list(self._rubrics.history(self._questions.get(question_id).rubric_id))

    # ------------------------------------------------------------ discussion

    def discussion(self, submission_id: str) -> list[Turn]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT role, text, meta FROM discussions WHERE submission_id = ? ORDER BY turn",
                (submission_id,),
            ).fetchall()
        return [Turn(r["role"], r["text"], json.loads(r["meta"] or "{}")) for r in rows]

    def discuss(self, submission_id: str, message: str) -> Turn:
        """The tutor's reply to the learner's latest message about a graded submission. The
        grade is fixed before this is reachable and nothing here changes it."""
        text = message.strip()
        if not text:
            raise AnswerRejected("write a message first")
        if len(text) > MAX_MESSAGE_CHARS:
            raise AnswerRejected(f"messages are limited to {MAX_MESSAGE_CHARS} characters")
        sub = self.get(submission_id)
        trace = self.trace(sub)
        if trace is None:
            raise AnswerRejected("the answer hasn't been graded yet")
        question = self._questions.get(sub.question_id)
        criteria = tutor.path_criteria(trace, self._rubrics.get(trace.rubric_hash_used))
        history = self.discussion(submission_id)
        talk = [t for t in history if t.role in ("learner", "tutor")]
        earlier = [t.text for t in talk if t.role == "tutor"]
        recheck = self.recheck_result(submission_id)
        variables: dict[str, object] = {
            "question": question.text,
            "answer": sub.answer,
            "dimensions": tutor.grade_breakdown(trace, criteria),
            "feedback": [i.text for i in trace.feedback.items] if trace.feedback else [],
            "reference": question.reference_answer,
            "recheck": recheck.for_tutor() if recheck else None,
            "settled": tutor.settled_points([t.meta for t in talk if t.role == "tutor"]),
            "earlier": earlier[-tutor.EARLIER_SHOWN :],
            "history": [{"role": t.role, "text": t.text} for t in talk[-HISTORY_TURNS:]],
            "message": text,
        }
        problems: list[str] = []
        reply, call_id, rejected = tutor.FALLBACK_REPLY, None, 0
        meta: dict[str, object] = {}
        role = "tutor"
        for _ in range(tutor.TUTOR_ATTEMPTS):
            try:
                res = self._client.complete(
                    role, "tutor_chat", {**variables, "problems": problems}, TutorReply
                )
            except (ProviderError, StructuredOutputError) as e:
                # Groq rate-limited or down: the local model takes over for this reply.
                if role == "tutor" and "tutor_fallback" in self._config.roles:
                    role = "tutor_fallback"
                    try:
                        res = self._client.complete(
                            role, "tutor_chat", {**variables, "problems": problems}, TutorReply
                        )
                    except (ProviderError, StructuredOutputError) as e2:
                        raise TutorUnavailable(
                            f"the tutor isn't available right now ({type(e2).__name__})"
                        ) from e2
                else:
                    raise TutorUnavailable(
                        f"the tutor isn't available right now ({type(e).__name__})"
                    ) from e
            out = res.value
            problems = tutor.reply_problems(out.reply, earlier, out.learner_point)
            meta = {"kind": out.kind, "learner_point": out.learner_point, "accepts": out.accepts}
            if not problems:
                reply, call_id = out.reply.strip(), res.call.call_id
                break
            rejected += 1
        # If every draft repeated itself or claimed a change, the fixed reply says so plainly.
        meta.update(rejected_drafts=rejected, fallback=call_id is None, role=role)
        turn = Turn("tutor", reply, meta)
        self._add_turns(
            submission_id,
            len(history),
            [("learner", text, None, {}), ("tutor", reply, call_id, meta)],
        )
        return turn

    def flag(self, submission_id: str, note: str) -> None:
        """The learner reports a grading problem. Stored with the discussion for review; it
        doesn't change the grade, and no model decides whether it is right."""
        text = note.strip() or "(no details given)"
        if len(text) > MAX_MESSAGE_CHARS:
            raise AnswerRejected(f"messages are limited to {MAX_MESSAGE_CHARS} characters")
        self.get(submission_id)  # unknown ids fail here
        self._add_turns(
            submission_id, len(self.discussion(submission_id)), [("flag", text, None, {})]
        )

    def is_flagged(self, submission_id: str) -> bool:
        return any(t.role == "flag" for t in self.discussion(submission_id))

    # ------------------------------------------------------------ re-check

    def recheck(self, submission_id: str, argument: str) -> tutor.RecheckResult:
        """One second look, by the judge's model, at the decisions that counted against the
        answer. Never the local model, never twice. The original evaluation is kept; the
        result is stored beside it, and the argument is saved as a report for review."""
        text = argument.strip()
        if len(text) < MIN_ARGUMENT_CHARS:
            raise AnswerRejected("say which decision you think is wrong, and why")
        if len(text) > MAX_MESSAGE_CHARS:
            raise AnswerRejected(f"messages are limited to {MAX_MESSAGE_CHARS} characters")
        if self.recheck_result(submission_id) is not None:
            raise AnswerRejected("this answer has already been re-checked; it is final")
        sub = self.get(submission_id)
        trace = self.trace(sub)
        if trace is None:
            raise AnswerRejected("the answer hasn't been graded yet")
        question = self._questions.get(sub.question_id)
        criteria = tutor.path_criteria(trace, self._rubrics.get(trace.rubric_hash_used))
        variables = tutor.recheck_variables(question.text, sub.answer, trace, criteria, text)
        try:
            res = self._client.complete("rechecker", "recheck", variables, RecheckOutput)
        except (ProviderError, StructuredOutputError) as e:
            raise RecheckUnavailable(
                f"the grader isn't available for a re-check right now ({type(e).__name__}); "
                "try again later"
            ) from e
        result = tutor.apply_recheck(trace, criteria, sub.answer, res.value, load_bands())
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO rechecks (submission_id, evaluation_id, argument, result_json, "
                "call_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    submission_id, trace.evaluation_id, text, json.dumps(result.to_json()),
                    res.call.call_id, utc_now(),
                ),
            )  # fmt: skip
        self.flag(submission_id, text)
        return result

    def recheck_result(self, submission_id: str) -> tutor.RecheckResult | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT result_json FROM rechecks WHERE submission_id = ?", (submission_id,)
            ).fetchone()
        return tutor.RecheckResult.from_json(json.loads(row[0])) if row else None

    @locked
    def _add_turns(
        self,
        submission_id: str,
        start: int,
        turns: list[tuple[str, str, str | None, dict[str, object]]],
    ) -> None:
        with self._conn:
            self._conn.executemany(
                "INSERT INTO discussions "
                "(submission_id, turn, role, text, call_id, created_at, meta) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (submission_id, start + n, role, text, call_id, utc_now(), json.dumps(meta))
                    for n, (role, text, call_id, meta) in enumerate(turns)
                ],
            )

    @locked
    def _save(self, s: Submission) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO submissions (submission_id, question_id, answer, status, "
                "evaluation_id, attempts, last_error, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(submission_id) DO UPDATE SET "
                "status = excluded.status, evaluation_id = excluded.evaluation_id, "
                "attempts = excluded.attempts, last_error = excluded.last_error, "
                "updated_at = excluded.updated_at",
                (
                    s.submission_id, s.question_id, s.answer, s.status, s.evaluation_id,
                    s.attempts, s.last_error, s.created_at, utc_now(),
                ),
            )  # fmt: skip

    @locked
    def _row(self, sql: str, args: tuple[object, ...]) -> list[Submission]:
        rows = self._conn.execute(sql, args).fetchall()
        return [
            Submission(
                r["submission_id"], r["question_id"], r["answer"], r["status"],
                r["evaluation_id"], r["attempts"], r["last_error"], r["created_at"],
            )
            for r in rows
        ]  # fmt: skip

    # ------------------------------------------------------------ quota

    def quota(self) -> list[Quota]:
        """Requests left today per role, from the same counters the rate limiter enforces."""
        usage = UsageCounter(self._conn)
        out = []
        for role in QUOTA_ROLES:
            if role not in self._config.roles:
                continue
            rcfg = self._config.role(role)
            pcfg = self._config.providers[rcfg.provider]
            day = datetime.now(ZoneInfo(pcfg.rpd_reset_tz)).date().isoformat()
            label = usage_label(rcfg.provider, pcfg.api_key_env)
            used = usage.requests_on(label, rcfg.model, day)
            out.append(
                Quota(role, rcfg.provider, rcfg.model, used, pcfg.limits_for(rcfg.model).rpd)
            )
        return out
