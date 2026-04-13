"""ainfera trust — detailed trust score breakdown."""

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
@click.option("--history", is_flag=True, help="Show score history")
@click.option("--anomalies", is_flag=True, help="Show detected anomalies")
@click.pass_context
def trust(ctx, agent_id: str | None, history: bool, anomalies: bool):
    """View detailed trust score breakdown."""
    json_output = ctx.obj.get("json", False)
    api_key = ensure_authenticated()
    client = AinferaClient(api_key=api_key, api_url=get_api_url())

    agent_id = agent_id or get_default_agent()
    if not agent_id:
        print_error(
            "No agent specified.",
            "Pass an agent ID or deploy an agent first.",
        )
        raise SystemExit(1)

    try:
        if history:
            with console.status("  [ainfera.muted]Fetching trust history...[/]"):
                data = client.get_trust_history(agent_id)

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

        elif anomalies:
            with console.status("  [ainfera.muted]Fetching anomalies...[/]"):
                data = client.get_anomalies(agent_id)

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

        else:
            with console.status("  [ainfera.muted]Fetching trust score...[/]"):
                data = client.get_trust_score(agent_id)

            if json_output:
                click.echo(json.dumps(data))
                return

            print_header()
            console.print(format_trust_panel(data))
            console.print()
    finally:
        client.close()
