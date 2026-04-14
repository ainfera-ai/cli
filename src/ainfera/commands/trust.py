"""ainfera trust — trust score command (flat interface with flags)."""

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


@click.command()
@click.argument("agent_id", required=False)
@click.option("--history", is_flag=True, help="Show trust score history instead of current score")
@click.option("--anomalies", is_flag=True, help="Show detected anomalies instead of current score")
@click.option("--days", type=int, default=30, help="History window in days (with --history)")
@click.pass_context
def trust(ctx, agent_id: str | None, history: bool, anomalies: bool, days: int):
    """View trust scores, history, and anomalies.

    \b
    Examples:
      ainfera trust                          # default agent, current score
      ainfera trust 8e7b4d6e-...             # explicit agent
      ainfera trust --history --days 7
      ainfera trust --anomalies
      ainfera --json trust                   # machine-readable
    """
    json_output = ctx.obj.get("json", False)
    resolved = _resolve_agent_id(agent_id)

    client = AinferaClient(api_key=ensure_authenticated(), api_url=get_api_url())
    try:
        if anomalies:
            with console.status("  [ainfera.muted]Fetching anomalies...[/]"):
                data = client.get_anomalies(resolved)
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
            return

        if history:
            with console.status("  [ainfera.muted]Fetching trust history...[/]"):
                data = client.get_trust_history(resolved)
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
            return

        with console.status("  [ainfera.muted]Fetching trust score...[/]"):
            data = client.get_trust_score(resolved)
        if json_output:
            click.echo(json.dumps(data))
            return
        print_header()
        console.print(format_trust_panel(data))
        console.print()
    finally:
        client.close()


def _resolve_agent_id(agent_id: str | None) -> str:
    resolved = agent_id or get_default_agent()
    if not resolved:
        print_error(
            "No agent specified.",
            "Pass an agent ID or deploy an agent first.",
        )
        raise SystemExit(1)
    return resolved
