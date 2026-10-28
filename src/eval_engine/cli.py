"""Command-line entry point: `eval-engine --help`."""

import secrets
from typing import Annotated, Literal

import typer
from pydantic import BaseModel

from eval_engine.config import ConfigError, db_path, load_config, load_env
from eval_engine.providers.base import ProviderError
from eval_engine.providers.client import StructuredOutputError
from eval_engine.providers.factory import build_client
from eval_engine.storage import UsageCounter, connect

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


if __name__ == "__main__":
    app()
