"""Command-line entry point: `eval-engine --help`."""

import json
import secrets
import sqlite3
from pathlib import Path
from typing import Annotated, Literal

import typer
from pydantic import BaseModel

from eval_engine.config import ConfigError, db_path, load_config, load_env
from eval_engine.evaluation.pipeline import evaluate
from eval_engine.feedback.render import learner_view
from eval_engine.generation.generate import GenerationError, generate_question
from eval_engine.generation.review import REVIEW_DIR, _question_block, build_batch
from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.providers.factory import build_client
from eval_engine.schemas.amendment import Framing
from eval_engine.schemas.common import TaskType
from eval_engine.storage import RubricStore, UsageCounter, connect
from eval_engine.storage.evaluation_store import EvaluationStore
from eval_engine.storage.question_store import QuestionStore
from eval_engine.validation import (
    corpus,
    degrade,
    feedback_review,
    golden,
    human_analysis,
    human_set,
    perturb,
    pilot,
    verifier_set,
)

app = typer.Typer(no_args_is_help=True, add_completion=False)


class SmokeReply(BaseModel):
    status: Literal["ok"]
    echo: str


@app.command()
def smoke(
    role: Annotated[
        list[str] | None,
        typer.Option(help="Role(s) to test. Default: one role per configured provider."),
    ] = None,
) -> None:
    """Phase 0 gate: one live, schema-validated call per provider (bypasses the cache)."""
    load_env()
    config = load_config()
    conn = connect(db_path())
    client = build_client(config, conn)

    if role:
        roles = role
    else:
        seen: dict[str, str] = {}
        for name, rcfg in config.roles.items():
            seen.setdefault(rcfg.provider, name)
        roles = list(seen.values())

    failures = 0
    for r in roles:
        rcfg = config.role(r)
        token = secrets.token_hex(4)
        label = f"{r:<20} {rcfg.provider}/{rcfg.model}"
        try:
            res = client.complete(r, "smoke", {"token": token}, SmokeReply, fresh=True)
        except (ProviderError, ConfigError, StructuredOutputError) as e:
            failures += 1
            typer.secho(f"FAIL  {label}\n      {e}", fg=typer.colors.RED)
            continue
        if res.value.echo != token:
            failures += 1
            typer.secho(f"FAIL  {label}  echo mismatch: {res.value.echo!r}", fg=typer.colors.RED)
            continue
        c = res.call
        extra = " (repaired)" if c.repaired else ""
        typer.secho(
            f"OK    {label}  {c.latency_ms} ms, {c.input_tokens}/{c.output_tokens} tok{extra}",
            fg=typer.colors.GREEN,
        )
    raise typer.Exit(code=1 if failures else 0)


@app.command()
def usage(day: Annotated[str | None, typer.Option(help="YYYY-MM-DD; default all")] = None) -> None:
    """Requests and tokens sent per provider/model/day."""
    load_env()
    rows = UsageCounter(connect(db_path())).summary(day)
    if not rows:
        typer.echo("no usage recorded")
        return
    for r in rows:
        typer.echo(
            f"{r['day']}  {r['provider']:<8} {r['model']:<28} {r['requests']:>6} req  "
            f"{r['tokens']:>9} tok"
        )


pilot_app = typer.Typer(no_args_is_help=True, help="Phase 2 judge pilot (SciEntsBank + Beetle).")
app.add_typer(pilot_app, name="pilot")

DEFAULT_JUDGES = ["judge", "judge_candidate_qwen", "judge_candidate_local"]


def _pilot_deps() -> tuple[LLMClient, RubricStore]:
    load_env()
    conn = connect(db_path())
    return build_client(load_config(), conn), RubricStore(conn)


OutDir = Annotated[
    Path,
    typer.Option("--out", help="Experiment folder (default: the held-out test pilot)"),
]


@pilot_app.command("prepare")
def pilot_prepare(
    answers: Annotated[int, typer.Option(help="Target answers per dataset")] = 150,
    max_per_question: Annotated[int, typer.Option(help="Cap on answers per question")] = 5,
    seed: int = 13,
    split: Annotated[str, typer.Option(help="test_ua (held-out) or train (dev)")] = "test_ua",
    exclude_from: Annotated[
        Path | None, typer.Option(help="Folder whose sample's questions to exclude")
    ] = None,
    rubric_prompt: Annotated[str, typer.Option(help="Rubric prompt name")] = "dataset_rubric",
    out: OutDir = pilot.PILOT_DIR,
) -> None:
    """Sample items and build one rubric per question with the generator role.

    Dev set: --split train --exclude-from experiments/2_judge_pilot --out .../dev"""
    if (split != "test_ua" or rubric_prompt != "dataset_rubric") and out == pilot.PILOT_DIR:
        raise typer.BadParameter("a different split or rubric prompt needs its own --out folder")
    client, store = _pilot_deps()
    excl = str(exclude_from) if exclude_from else None
    cfg = pilot.PilotConfig(answers, max_per_question, seed, split, excl, rubric_prompt)
    summary = pilot.prepare(client, store, cfg, out_dir=out)
    typer.echo(json.dumps(summary, indent=1))
    typer.echo(f"Review rubrics in {out / 'rubrics_review.md'}")
    if summary["stopped"]:
        typer.secho(
            f"Stopped with {summary['missing']} rubric(s) missing: {summary['stopped']}\n"
            "Judges can run now on the rest; rerun `pilot prepare` after the quota resets.",
            fg="yellow",
        )
        raise typer.Exit(2)


@pilot_app.command("run")
def pilot_run(
    role: Annotated[str, typer.Option(help="Judge role from roles.yaml")] = "judge",
    workers: Annotated[int, typer.Option(help="Calls in flight at once")] = 4,
    out: OutDir = pilot.PILOT_DIR,
) -> None:
    """Grade every sampled answer with one judge. Safe to rerun: finished items come from cache."""
    client, store = _pilot_deps()
    rows, stop = pilot.run(client, store, role, workers=workers, out_dir=out)
    errors = sum(r.error is not None for r in rows)
    total = len(pilot._manifest(out))
    typer.echo(f"{role}: {len(rows)}/{total} items processed, {errors} with errors")
    if stop:
        typer.secho(f"Stopped early ({stop}). Rerun later to resume.", fg="yellow")
        raise typer.Exit(2)


@pilot_app.command("stability")
def pilot_stability(
    role: str = "judge",
    items: Annotated[int, typer.Option(help="Items to rerun")] = 50,
    repeats: int = 3,
    out: OutDir = pilot.PILOT_DIR,
) -> None:
    """Fresh reruns of a subset to measure verdict flip rate (never overwrites the cache)."""
    client, store = _pilot_deps()
    result = pilot.stability(client, store, role, n_items=items, repeats=repeats, out_dir=out)
    typer.echo(json.dumps(result))


@pilot_app.command("report")
def pilot_report(
    role: Annotated[list[str] | None, typer.Option(help="Judge roles to include")] = None,
    out: OutDir = pilot.PILOT_DIR,
) -> None:
    """Compute metrics and the gate verdict; writes REPORT.md in the experiment folder."""
    text, _ = pilot.report(role or DEFAULT_JUDGES, out_dir=out)
    typer.echo(text)


gen_app = typer.Typer(no_args_is_help=True, help="Phase 3: question and rubric generation.")
app.add_typer(gen_app, name="gen")


def _gen_deps() -> tuple[LLMClient, RubricStore, QuestionStore]:
    load_env()
    conn = connect(db_path())
    return build_client(load_config(), conn), RubricStore(conn), QuestionStore(conn)


@gen_app.command("question")
def gen_question(
    topic: Annotated[str, typer.Option(help="Topic from config/topics.yaml")],
    task_type: Annotated[TaskType, typer.Option(help="Task type to generate")],
) -> None:
    """Generate one question + frozen rubric + reference answer, and print it."""
    client, rubrics, questions = _gen_deps()
    try:
        g = generate_question(client, rubrics, questions, topic, task_type)
    except GenerationError as e:
        typer.secho("Failed checks twice:\n- " + "\n- ".join(e.problems), fg="red")
        raise typer.Exit(1) from e
    except (StructuredOutputError, ProviderError) as e:
        typer.secho(f"Generation failed: {str(e)[:800]}", fg="red")
        raise typer.Exit(1) from e
    typer.echo("\n".join(_question_block(1, g.question, g.rubric)))
    if g.first_attempt_problems:
        typer.secho(
            "First attempt was rejected for: " + "; ".join(g.first_attempt_problems), fg="yellow"
        )


@gen_app.command("batch")
def gen_batch(
    per_type: Annotated[int, typer.Option(help="Questions per task type")] = 10,
) -> None:
    """Phase 3 gate batch (task types x topics). Resumable; writes the review sheet."""
    client, rubrics, questions = _gen_deps()
    summary = build_batch(client, rubrics, questions, per_type=per_type)
    typer.echo(json.dumps(summary, indent=1))
    typer.echo(f"Review sheet: {REVIEW_DIR / 'review.md'}")
    if summary["stopped"]:
        typer.secho(f"Stopped: {summary['stopped']}. Rerun later to continue.", fg="yellow")
        raise typer.Exit(2)


@app.command("evaluate")
def evaluate_cmd(
    question: Annotated[str, typer.Option(help="Question id")],
    answer_file: Annotated[Path | None, typer.Option(help="File with the answer")] = None,
    answer: Annotated[str | None, typer.Option(help="Answer text (instead of a file)")] = None,
    votes: Annotated[int, typer.Option(help="Judge votes on borderline answers (D6)")] = 1,
    feedback: Annotated[bool, typer.Option(help="Write the learner's feedback")] = True,
) -> None:
    """Grade one answer against its question's frozen rubric and print the result: what the
    learner sees first, then the grading details."""
    if (answer_file is None) == (answer is None):
        raise typer.BadParameter("give exactly one of --answer-file or --answer")
    text = answer_file.read_text(encoding="utf-8") if answer_file else str(answer)
    load_env()
    conn = connect(db_path())
    client = build_client(load_config(), conn)
    rubrics, questions = RubricStore(conn), QuestionStore(conn)
    t = evaluate(
        client,
        rubrics,
        questions,
        EvaluationStore(conn),
        question,
        text,
        votes=votes,
        feedback=feedback,
    )
    q = questions.get(question)
    typer.echo(f"Question ({q.task_type.value}): {q.text}\n")
    typer.echo("\n".join(learner_view(t)))
    typer.secho("\nDetails (not shown to the learner)", bold=True)
    if t.feedback and t.feedback.fallbacks:
        typer.secho(f"  feedback templates used: {t.feedback.fallbacks}", fg="yellow")
    if t.identified_path:
        conf = ", ".join(f"{p.path_id}={p.confidence:.2f}" for p in t.path_confidences)
        typer.echo(f"Path: {t.identified_path}  ({conf})")
    if t.amendment_fired:
        outcome = "accepted" if t.verifier_verdict else "not accepted"
        typer.secho(f"Amendment {outcome} ({t.verifier_framing})", fg="yellow")
        for note in (t.verifier_reasoning, t.divergence_reason, t.amendment_error):
            if note:
                typer.echo(f"  {note}")
    for v in t.verdicts:
        mark = "MET " if v.met else "    "
        typer.echo(f"  {mark} {v.criterion_id}: {v.justification}")
    for e in t.errors:
        typer.secho(f'  error: "{e.quote}": {e.explanation}', fg="red")
    if t.evidence_downgrades:
        typer.secho(f"  evidence not found, downgraded: {t.evidence_downgrades}", fg="yellow")
    if t.contradiction_downgrades:
        typer.secho(
            f"  met on a flagged error, downgraded: {t.contradiction_downgrades}", fg="yellow"
        )
    if t.count_overrides:
        typer.secho(f"  sentence count decided in code: {t.count_overrides}", fg="yellow")
    if t.obvious_overlap:
        typer.echo(f"  reuses obvious ideas: {t.obvious_overlap}")
    typer.echo("")
    for d, sc in t.dimension_scores.items():
        typer.echo(f"  {d.value:<13} {t.bands[d]:<11} ({sc:.2f})")
    typer.echo(f"\nevaluation {t.evaluation_id}, votes {t.judge_votes}")


@app.command("golden")
def golden_cmd(
    votes: Annotated[
        int, typer.Option(help=">1: D6 study against the recorded single votes (no fixture write)")
    ] = 1,
) -> None:
    """Phase 4: grade the golden answers live, record the replay fixture, print the report."""
    load_env()
    conn = connect(db_path())
    client = build_client(load_config(), conn)
    if votes > 1:
        study = golden.vote_study(client, conn, golden.load_items(), votes)
        (golden.GOLDEN_DIR / "d6_votes.md").write_text(study + "\n", encoding="utf-8")
        typer.echo(study)
        return
    outcomes = golden.run(client, conn, golden.load_items())
    text = golden.report(outcomes)
    (golden.GOLDEN_DIR / "golden_report.md").write_text(text + "\n", encoding="utf-8")
    typer.echo(text)


@app.command("feedback-review")
def feedback_review_cmd() -> None:
    """Phase 6: 30 evaluations with feedback, written to a review sheet. Grading replies come
    from the cache; feedback calls go to the local model."""
    load_env()
    conn = connect(db_path())
    rows = feedback_review.run(build_client(load_config(), conn), conn)
    sheet = feedback_review.FEEDBACK_DIR / "review.md"
    sheet.write_text(feedback_review.review_sheet(rows, QuestionStore(conn)), encoding="utf-8")
    typer.echo(json.dumps(feedback_review.summary(rows)))
    typer.echo(f"Review sheet: {sheet}")


validate_app = typer.Typer(no_args_is_help=True, help="Phase 7 full validation.")
app.add_typer(validate_app, name="validate")


@validate_app.command("corpus")
def validate_corpus() -> None:
    """The Phase 2 held-out sample through the full engine. Resumable from the cache."""
    load_env()
    conn = connect(db_path())
    runs, stopped = corpus.run(build_client(load_config(), conn), conn)
    text = corpus.report(runs)
    (corpus.CORPUS_DIR / "REPORT.md").write_text(text + "\n", encoding="utf-8")
    typer.echo(text)
    if stopped:
        typer.secho(f"Stopped ({stopped[:200]}). Rerun later to resume.", fg="yellow")
        raise typer.Exit(2)


@validate_app.command("perturb")
def validate_perturb(
    step: Annotated[str, typer.Argument(help="baseline | build | run | report, in that order")],
) -> None:
    """Synthetic perturbation. `build` uses the local model; `baseline` and `run` the judge.
    Read items.json by hand between `build` and `run`; drops go in review.json."""
    load_env()
    conn = connect(db_path())
    client = build_client(load_config(), conn)
    stopped = None
    if step == "baseline":
        rows, stopped = perturb.baseline(client, conn)
        typer.echo(f"{len(rows)} bases graded")
    elif step == "build":
        typer.echo(json.dumps(perturb.build(client, conn)))
    elif step == "run":
        rows, stopped = perturb.run(client, conn)
        typer.echo(f"{len(rows)} perturbations graded")
    elif step == "report":
        rows = json.loads((perturb.PERTURB_DIR / "results.json").read_text(encoding="utf-8"))
        text, _ = perturb.report(rows)
        (perturb.PERTURB_DIR / "REPORT.md").write_text(text + "\n", encoding="utf-8")
        typer.echo(text)
    else:
        raise typer.BadParameter("step must be baseline, build, run or report")
    if stopped:
        typer.secho(f"Stopped ({stopped[:200]}). Rerun later to resume.", fg="yellow")
        raise typer.Exit(2)


@validate_app.command("human")
def validate_human() -> None:
    """Pre-registered analysis of the human-graded set. Needs both graders' CSVs in
    experiments/7_validation/human/grades/ (grader1.csv, grader2.csv)."""
    load_env()
    conn = connect(db_path())
    expected = human_analysis.expected_items(conn)
    g1 = human_analysis.load_grades(human_analysis.GRADES_DIR / "grader1.csv", expected)
    g2 = human_analysis.load_grades(human_analysis.GRADES_DIR / "grader2.csv", expected)
    key = json.loads((human_set.HUMAN_DIR / "key.json").read_text(encoding="utf-8"))
    engine = human_analysis.engine_scores(build_client(load_config(), conn), conn)
    criteria = human_analysis.criteria_by_hash(conn, engine)
    text, _ = human_analysis.analyse(key, g1, g2, expected, engine, criteria)
    (human_set.HUMAN_DIR / "REPORT.md").write_text(text + "\n", encoding="utf-8")
    typer.echo(text)


@validate_app.command("degrade")
def validate_degrade() -> None:
    """Phase 8 gate: break the judge, the verifier and the feedback model one at a time."""
    import tempfile

    load_env()
    conn = connect(db_path())
    with tempfile.TemporaryDirectory() as tmp:
        results = degrade.run(conn, load_config(), Path(tmp))
    text = degrade.report(results)
    degrade.DEGRADE_DIR.mkdir(parents=True, exist_ok=True)
    (degrade.DEGRADE_DIR / "DEGRADATION.md").write_text(text + "\n", encoding="utf-8")
    typer.echo(text)


@validate_app.command("discussion")
def validate_discussion(
    only: Annotated[
        str, typer.Option(help="Comma-separated scenarios")
    ] = "T1,T2,T3,R1,R2,R3,R4,R5,R6,R7,R8",
) -> None:
    """Phase 8: the tutor and re-check fixes, live, on scenarios fixed in advance."""
    import tempfile

    from eval_engine.validation import discussion_check as dc

    load_env()
    conn = connect(db_path())
    with tempfile.TemporaryDirectory() as tmp:
        results = dc.run(conn, load_config(), Path(tmp), set(only.split(",")))
    dc.OUT_DIR.mkdir(parents=True, exist_ok=True)
    # The tutor model is in the name, so a run with another tutor never overwrites a report.
    tutor_model = load_config().roles["tutor"].model.split("/")[-1].replace(":", "-")
    stamp = "_".join(sorted(results)) + "_" + tutor_model
    (dc.OUT_DIR / f"results_{stamp}.json").write_text(
        json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    text = dc.report(results)
    (dc.OUT_DIR / f"REPORT_{stamp}.md").write_text(text, encoding="utf-8")
    typer.echo(text)


snapshot_app = typer.Typer(
    no_args_is_help=True, help="Phase 9: the committed copy of what a fresh clone needs."
)
app.add_typer(snapshot_app, name="snapshot")


@snapshot_app.command("import")
def snapshot_import() -> None:
    """Fill data/ from snapshot/: rubrics, questions, evaluations, cached responses and the
    borrowed corpora. Run once after cloning; rows already present are kept."""
    from eval_engine.storage import snapshot

    added = snapshot.load(db_path())
    typer.echo(json.dumps(added, indent=1))


@snapshot_app.command("export")
def snapshot_export() -> None:
    """Write snapshot/ from data/ (after new results; unchanged data gives no git diff)."""
    from eval_engine.storage import snapshot

    typer.echo(json.dumps(snapshot.export(db_path()), indent=1))


@app.command("amendment-frequency")
def amendment_frequency_cmd() -> None:
    """Phase 9: how often amendment fires and is accepted, per task type, from the traces."""
    from eval_engine.validation import amendment_freq

    conn = connect(db_path())
    text = amendment_freq.report(conn)
    amendment_freq.OUT_DIR.mkdir(parents=True, exist_ok=True)
    (amendment_freq.OUT_DIR / "AMENDMENT_FREQUENCY.md").write_text(text, encoding="utf-8")
    typer.echo(text)


@app.command("reproduce")
def reproduce_cmd(
    only: Annotated[
        list[str] | None, typer.Option(help="Run only steps whose name contains this")
    ] = None,
) -> None:
    """Phase 9 gate: regenerate every validation report from cached responses (no live calls,
    on a copy of the database) and check each matches the committed report."""
    from eval_engine.validation import reproduce

    load_env()
    results = reproduce.run(db_path(), load_config(), set(only) if only else None)
    typer.echo(reproduce.report(results))
    if not all(r.ok for r in results):
        raise typer.Exit(1)


verifier_app = typer.Typer(no_args_is_help=True, help="Phase 5 verifier test set.")
app.add_typer(verifier_app, name="verifier")


def _verifier_deps() -> tuple[LLMClient, sqlite3.Connection]:
    load_env()
    conn = connect(db_path())
    return build_client(load_config(), conn), conn


@verifier_app.command("build")
def verifier_build() -> None:
    """Author the test set and write its review sheet. Resumable from the cache."""
    client, conn = _verifier_deps()
    summary = verifier_set.build(client, conn)
    typer.echo(json.dumps(summary))
    sheet = verifier_set.VERIFIER_DIR / "review.md"
    sheet.write_text(verifier_set.review_sheet(conn), encoding="utf-8")
    typer.echo(f"Review sheet: {sheet}")
    if summary["stopped"]:
        typer.secho("Stopped on quota. Rerun later to continue.", fg="yellow")
        raise typer.Exit(2)


@verifier_app.command("run")
def verifier_run(framing: Annotated[Framing, typer.Option(help="Verifier prompt framing")]) -> None:
    """Verify every item under one framing. Resumable from the cache."""
    client, conn = _verifier_deps()
    rows, stopped = verifier_set.run(client, conn, framing)
    typer.echo(f"{framing}: {len(rows)} items done")
    if stopped:
        typer.secho(f"Stopped ({stopped[:200]}). Rerun later to resume.", fg="yellow")
        raise typer.Exit(2)


@verifier_app.command("calibrate")
def verifier_calibrate() -> None:
    """Judge the set's answers and sweep the confidence threshold."""
    client, conn = _verifier_deps()
    text, _ = verifier_set.calibrate(client, conn)
    typer.echo(text)


@verifier_app.command("e2e")
def verifier_e2e() -> None:
    """Run the whole chain on the answers that trigger amendment. Real rubrics are untouched."""
    client, conn = _verifier_deps()
    text, stopped = verifier_set.end_to_end(client, conn)
    typer.echo(text)
    if stopped:
        typer.secho(f"Stopped ({stopped[:200]}). Rerun later to resume.", fg="yellow")
        raise typer.Exit(2)


@verifier_app.command("report")
def verifier_report() -> None:
    """Metrics per framing; writes REPORT.md."""
    text, _ = verifier_set.report()
    (verifier_set.VERIFIER_DIR / "REPORT.md").write_text(text + "\n", encoding="utf-8")
    typer.echo(text)


if __name__ == "__main__":
    app()
