"""Evaluation & Feedback Engine demo (plan Phase 8). Run: `streamlit run app/streamlit_app.py`.

A thin page over `eval_engine.service`; the behaviour (queueing, degradation, quota) lives
there and is tested without a browser.
"""

from typing import Any

import streamlit as st

from eval_engine.config import db_path, load_config, load_env
from eval_engine.providers.factory import build_client
from eval_engine.schemas.common import TaskType
from eval_engine.schemas.trace import EvaluationTrace
from eval_engine.service import (
    AnswerRejected,
    EngineService,
    GenerationFailed,
    RecheckUnavailable,
    Submission,
    TopicRejected,
    TutorUnavailable,
)
from eval_engine.storage import connect
from eval_engine.tutor import RecheckResult

st.set_page_config(page_title="Answer feedback", page_icon="📝", layout="wide")


@st.cache_resource
def service() -> EngineService:
    load_env()
    config = load_config()
    conn = connect(db_path())
    return EngineService(conn, build_client(config, conn), config)


svc = service()
state: Any = st.session_state


# ---------------------------------------------------------------- sidebar: quota and queue

with st.sidebar:
    st.subheader("Requests left today")
    for quota in svc.quota():
        left = "no limit" if quota.remaining is None else f"{quota.remaining} of {quota.limit}"
        st.caption(f"**{quota.role}** · {quota.model}: {left}")
    waiting = svc.queued()
    if waiting:
        st.warning(f"{len(waiting)} answer(s) waiting for the grader.")
        if st.button("Try the waiting answers again"):
            with st.spinner("Evaluating…"):
                svc.retry_queued()
            st.rerun()


def show_feedback(trace: EvaluationTrace) -> None:
    items = trace.feedback.items if trace.feedback else []
    for item in items:
        if item.kind in ("approach", "divergence", "off_topic"):
            st.info(item.text)
    improve = [i for i in items if i.kind == "improve"]
    if improve:
        st.markdown("**To work on**")
        for n, i in enumerate(improve, start=1):
            st.markdown(f"{n}. {i.text}")
    for item in items:
        if item.kind == "originality":
            st.caption(item.text)
    worked = [i for i in items if i.kind == "worked"]
    if worked:
        st.markdown("**What worked**")
        for i in worked:
            st.markdown(f"- {i.text}")
    st.markdown("**Bands**")
    cols = st.columns(max(1, len(trace.bands)))
    for col, (dimension, band) in zip(cols, trace.bands.items(), strict=True):
        col.metric(dimension.value.capitalize(), band)


def sentence(e: Exception) -> str:
    text = str(e)
    return text[:1].upper() + text[1:] + "."


def show_recheck(result: RecheckResult) -> None:
    out = result.output
    st.markdown("**Re-check result** (final)")
    if result.changed:
        st.success(out.summary)
    else:
        st.info(out.summary)
    if out.correct_parts:
        st.markdown("Right in your answer: " + "; ".join(out.correct_parts))
    if out.incorrect_statement:
        how = {"significant": "a misconception", "minor": "a minor slip"}.get(out.severity, "")
        st.markdown(f'Wrong: "{out.incorrect_statement}"' + (f" ({how})" if how else ""))
    moved = [
        (d, result.bands_before.get(d, "-"), b)
        for d, b in result.bands_after.items()
        if result.bands_before.get(d) != b
    ]
    if moved:
        cols = st.columns(len(moved))
        for col, (d, before, after) in zip(cols, moved, strict=True):
            col.metric(d.capitalize(), after, delta=f"was {before}", delta_color="off")
    else:
        st.caption("No band changed.")


def show_discussion(sub: Submission) -> None:
    st.divider()
    st.markdown("**Discuss your answer**")
    st.caption(
        "Ask about the feedback, a fact, or how to improve. The tutor is an AI model: it can "
        "be wrong, and it can't change your result. The conversation is saved so the "
        "grading can be reviewed."
    )
    turns = svc.discussion(sub.submission_id)
    for turn in turns:
        if turn.role == "flag":
            continue
        with st.chat_message("user" if turn.role == "learner" else "assistant"):
            st.write(turn.text)
            if turn.meta.get("role") == "tutor_fallback":
                st.caption("Answered by the backup local model; it can be less reliable.")
    message = st.chat_input("Ask the tutor about your answer", key=f"chat-{sub.submission_id}")
    if message:
        with st.chat_message("user"):
            st.write(message)
        try:
            with st.spinner("The tutor is thinking…"):
                svc.discuss(sub.submission_id, message)
            st.rerun()
        except (AnswerRejected, TutorUnavailable) as e:
            st.error(sentence(e))

    result = svc.recheck_result(sub.submission_id)
    if result is not None:
        show_recheck(result)
        return
    tutor_turns = [t for t in turns if t.role == "tutor"]
    disputed = any(t.meta.get("kind") == "challenge" for t in tutor_turns)
    with (
        st.expander("Think a decision is wrong? Ask for a re-check", expanded=disputed),
        st.form(f"recheck-{sub.submission_id}"),
    ):
        st.caption(
            "The grader looks again at the decisions that counted against your answer, using "
            "only what your answer says. It can go your way or not; it is done once, and your "
            "argument is saved for the people who review the grading."
        )
        argument = st.text_area("Which decision is wrong, and why?", height=100)
        if st.form_submit_button("Ask for a re-check"):
            try:
                with st.spinner("Re-checking…"):
                    svc.recheck(sub.submission_id, argument)
                st.rerun()
            except (AnswerRejected, RecheckUnavailable) as e:
                st.error(sentence(e))


def show_waiting(sub: Submission) -> None:
    st.info(
        "Evaluating… The grader isn't available right now (its rate limit or daily quota). "
        "Your answer is saved and will be graded as soon as it is back. It won't be graded by "
        "a different model instead."
    )
    if st.button("Check again"):
        with st.spinner("Evaluating…"):
            svc.retry_queued()
        st.rerun()
    st.caption(f"Attempts so far: {sub.attempts}")


BANK, NEW = "From the question bank", "Generate a new question"
KINDS = {
    "Explain how or why something happens": TaskType.EXPLANATORY,
    "Take a position and argue for it": TaskType.ANALYTICAL,
    "Recall facts": TaskType.FACTUAL,
    "Write something creative": TaskType.CREATIVE,
}

learner, admin = st.tabs(["Answer a question", "Admin"])

# ---------------------------------------------------------------- learner view

with learner:
    st.title("Answer a question")
    source = st.radio(
        "Where should the question come from?",
        [BANK, NEW],
        horizontal=True,
        captions=["Questions a person has reviewed", "Describe any topic; made on the spot"],
    )
    if source == BANK:
        topic = st.selectbox("Pick a topic", svc.topics(), index=None, placeholder="Choose a topic")
        if topic and st.button("Get a question", type="primary"):
            seen = state.get("seen", set())
            q = svc.question_for(topic, exclude=seen)
            state.seen = seen | {q.question_id}
            state.question_id, state.submission_id = q.question_id, None
    else:
        with st.form("describe"):
            described = st.text_input(
                "Describe the topic",
                placeholder="e.g. how vaccines train the immune system",
            )
            kind = st.selectbox("Kind of question", list(KINDS))
            if st.form_submit_button("Generate a question", type="primary"):
                try:
                    with st.spinner("Writing and checking a question… (up to a minute)"):
                        q = svc.generate(described, KINDS[kind])
                    state.question_id, state.submission_id = q.question_id, None
                except (TopicRejected, GenerationFailed) as e:
                    st.error(str(e)[:1].upper() + str(e)[1:] + ". Try again or reword the topic.")

    if state.get("question_id"):
        q = svc.question(state.question_id)
        st.markdown(f"#### {q.text}")
        st.caption(f"{q.topic} · {q.task_type.value}")
        if not svc.is_reviewed(q.question_id):
            st.warning(
                "New question: written just now and checked automatically, but nobody has "
                "reviewed how it is graded, so the feedback is less certain than for questions "
                "from the bank."
            )
        sub_id = state.get("submission_id")
        if sub_id is None:
            with st.form("answer"):
                answer = st.text_area("Your answer", height=220)
                if st.form_submit_button("Submit", type="primary"):
                    try:
                        with st.spinner("Evaluating… (usually under a minute)"):
                            state.submission_id = svc.submit(q.question_id, answer).submission_id
                        st.rerun()
                    except AnswerRejected as e:
                        st.error(str(e).capitalize() + ".")
        else:
            sub = svc.get(sub_id)
            st.markdown("**Your answer**")
            st.write(sub.answer)
            trace = svc.trace(sub)
            if trace is None:
                show_waiting(sub)
            else:
                st.divider()
                show_feedback(trace)
                # No reference answer here (D2 as tightened in Phase 3, binding): Phase 3
                # review found errors in about a third of them, and they play no part in
                # grading, so showing one could teach a learner something wrong.
                show_discussion(sub)
            if st.button("Try another question"):
                state.question_id, state.submission_id = None, None
                st.rerun()

# ---------------------------------------------------------------- admin view

with admin:
    st.title("Admin")
    only_amended = st.checkbox("Only answers where the amendment stage fired")
    only_flagged = st.checkbox("Only answers the learner reported as wrongly graded")
    subs = svc.recent(100)
    rows = []
    for s in subs:
        t = svc.trace(s)
        if only_amended and not (t and t.amendment_fired):
            continue
        if only_flagged and not svc.is_flagged(s.submission_id):
            continue
        rows.append((s, t))
    if not rows:
        st.caption("No submissions yet." if not subs else "None match the filter.")
    labels = {
        f"{s.created_at[:19]} · {s.status} · {svc.question(s.question_id).topic}"
        + (" · amendment" if t and t.amendment_fired else "")
        + ("" if svc.is_reviewed(s.question_id) else " · generated")
        + (" · discussed" if svc.discussion(s.submission_id) else "")
        + (" · REPORTED" if svc.is_flagged(s.submission_id) else ""): (s, t)
        for s, t in rows
    }
    choice = st.selectbox("Submission", list(labels), index=None)
    if choice:
        s, t = labels[choice]
        q = svc.question(s.question_id)
        reviewed = "reviewed bank" if svc.is_reviewed(q.question_id) else "generated, unreviewed"
        st.markdown(f"**Question** ({q.task_type.value}, {reviewed}): {q.text}")
        st.markdown(f"**Answer:** {s.answer}")
        if t is None:
            st.warning(f"Waiting for the grader. Last error: {s.last_error}")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Path", t.identified_path or "creative")
            c2.metric("Rubric used", t.final_rubric_source)
            c3.metric("Judge votes", t.judge_votes)
            if t.amendment_fired:
                st.markdown("**Amendment stage**")
                st.write(
                    {
                        "verifier verdict": t.verifier_verdict,
                        "framing": t.verifier_framing,
                        "failure type": t.verifier_failure_type,
                        "reasoning": t.verifier_reasoning,
                        "divergence reason": t.divergence_reason,
                        "error": t.amendment_error,
                    }
                )
            st.markdown("**Verdicts**")
            st.dataframe(
                [
                    {"criterion": v.criterion_id, "met": v.met, "justification": v.justification}
                    for v in t.verdicts
                ],
                hide_index=True,
            )
            if t.feedback:
                st.markdown("**Feedback items**")
                st.dataframe(
                    [
                        {"kind": i.kind, "source": i.source, "text": i.text}
                        for i in t.feedback.items
                    ],
                    hide_index=True,
                )
                if t.feedback.fallbacks:
                    st.caption(f"Template fallbacks: {t.feedback.fallbacks}")
            turns = svc.discussion(s.submission_id)
            if turns:
                st.markdown(f"**Discussion with the tutor** ({len(turns)} messages)")
                for turn in turns:
                    who = {"learner": "Learner", "tutor": "Tutor"}.get(turn.role, "REPORT")
                    note = ""
                    if turn.role == "tutor" and turn.meta:
                        note = f" _(read as: {turn.meta.get('kind')}"
                        if turn.meta.get("rejected_drafts"):
                            note += f"; {turn.meta['rejected_drafts']} draft(s) rejected"
                        if turn.meta.get("fallback"):
                            note += "; fixed reply"
                        note += ")_"
                    st.caption(f"**{who}:** {turn.text}{note}")
            rc = svc.recheck_result(s.submission_id)
            if rc is not None:
                st.markdown("**Re-check**")
                st.write(
                    {
                        "changed": rc.changed,
                        "revised to met": rc.revised,
                        "revise refused (no quote in answer)": rc.refused,
                        "errors dropped": rc.errors_dropped,
                        "bands before": rc.bands_before,
                        "bands after": rc.bands_after,
                        "severity": rc.output.severity,
                        "concern about the question's requirements": rc.output.rubric_concern,
                        "decisions": [d.model_dump() for d in rc.output.criteria],
                    }
                )
            with st.expander("Full trace"):
                st.json(t.model_dump(mode="json"))
        st.markdown("**Rubric versions**")
        for r in svc.rubric_history(s.question_id):
            paths = ", ".join(p.description for p in r.paths)
            st.caption(f"v{r.version} · {r.source} · {(r.hash or '')[:12]} · paths: {paths}")
