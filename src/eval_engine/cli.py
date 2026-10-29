"""Command-line entry point: `eval-engine --help`."""

import json
import secrets
from pathlib import Path
from typing import Annotated, Literal

import typer
from pydantic import BaseModel

from eval_engine.config import ConfigError, db_path, load_config, load_env
from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import LLMClient, StructuredOutputError
from eval_engine.providers.factory import build_client
from eval_engine.storage import RubricStore, UsageCounter, connect
from eval_engine.validation import pilot

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


if __name__ == "__main__":
    app()
