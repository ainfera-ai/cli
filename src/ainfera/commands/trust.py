"""ainfera trust — trust score commands."""

from __future__ import annotations

import json

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url, get_default_agent
from ainfera.ui.console import console, print_error, print_header
from ainfera.ui.formatters import (
    format_anomalies_table,
    format_trust_history_table,
    format_trust_panel,
)


@click.group()
def trust():
    """View trust scores, history, and anomalies."""


@trust.command("score")
@click.argument("agent_id", required=False)
@click.pass_context
def score_cmd(ctx, agent_id: str | None):
    """Show trust score with dimension breakdown.

    \b
    Examples:
      ainfera trust score                       # uses default agent
      ainfera trust score 8e7b4d6e-...
      ainfera --json trust score 8e7b4d6e-...
    """
    json_output = ctx.obj.get("json", False)
    agent_id = _resolve_agent_id(agent_id)

    client = _client()
    try:
        with console.status("  [ainfera.muted]Fetching trust score...[/]"):
            data = client.get_trust_score(agent_id)
    finally:
        client.close()

    if json_output:
        click.echo(json.dumps(data))
        return

    print_header()
    console.print(format_trust_panel(data))
    console.print()


@trust.command("history")
@click.argument("agent_id", required=False)
@click.pass_context
def history_cmd(ctx, agent_id: str | None):
    """Show trust score history."""
    json_output = ctx.obj.get("json", False)
    agent_id = _resolve_agent_id(agent_id)

    client = _client()
    try:
        with console.status("  [ainfera.muted]Fetching trust history...[/]"):
            data = client.get_trust_history(agent_id)
    finally:
        client.close()

    if json_output:
        click.echo(json.dumps(data))
        return

    print_header()
    entries = data.get("items", data.get("history", []))
    if entries:
        console.print(format_trust_history_table(entries))
    else:
        console.print("  [ainfera.muted]No trust history yet.[/]")
    console.print()


@trust.command("anomalies")
@click.argument("agent_id", required=False)
@click.pass_context
def anomalies_cmd(ctx, agent_id: str | None):
    """Show detected anomalies for an agent."""
    json_output = ctx.obj.get("json", False)
    agent_id = _resolve_agent_id(agent_id)

    client = _client()
    try:
        with console.status("  [ainfera.muted]Fetching anomalies...[/]"):
            data = client.get_anomalies(agent_id)
    finally:
        client.close()

    if json_output:
        click.echo(json.dumps(data))
        return

    print_header()
    items = data.get("items", data.get("anomalies", []))
    if items:
        console.print(format_anomalies_table(items))
    else:
        console.print("  [ainfera.success]\u2713 No anomalies detected[/]")
    console.print()


def _resolve_agent_id(agent_id: str | None) -> str:
    resolved = agent_id or get_default_agent()
    if not resolved:
        print_error(
            "No agent specified.",
            "Pass an agent ID or deploy an agent first.",
        )
        raise SystemExit(1)
    return resolved


def _client() -> AinferaClient:
    return AinferaClient(api_key=ensure_authenticated(), api_url=get_api_url())
