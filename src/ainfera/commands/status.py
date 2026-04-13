"""ainfera status — show agent status and trust score."""

from __future__ import annotations

import json

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url, get_default_agent
from ainfera.ui.console import console, print_error, print_header
from ainfera.ui.formatters import format_agent_panel, format_agent_table


@click.command()
@click.argument("agent_id", required=False)
@click.option("--all", "show_all", is_flag=True, help="List all agents")
@click.pass_context
def status(ctx, agent_id: str | None, show_all: bool):
    """Show agent status and trust score."""
    json_output = ctx.obj.get("json", False)
    api_key = ensure_authenticated()
    client = AinferaClient(api_key=api_key, api_url=get_api_url())

    try:
        if show_all or (agent_id is None and get_default_agent() is None):
            # List all agents
            with console.status("  [ainfera.muted]Fetching agents...[/]"):
                data = client.list_agents()

            agents = data.get("items", data.get("agents", []))

            if json_output:
                click.echo(json.dumps(data))
                return

            print_header()
            if not agents:
                console.print("  [ainfera.muted]No agents found. Run `ainfera deploy` to create one.[/]")
            else:
                console.print(format_agent_table(agents))
            console.print()
        else:
            # Show single agent
            agent_id = agent_id or get_default_agent()
            if not agent_id:
                print_error(
                    "No agent specified.",
                    "Pass an agent ID or run `ainfera status --all`.",
                )
                raise SystemExit(1)

            with console.status("  [ainfera.muted]Fetching agent...[/]"):
                agent = client.get_agent(agent_id)

            if json_output:
                click.echo(json.dumps(agent))
                return

            print_header()
            console.print(format_agent_panel(agent))
            console.print()
    finally:
        client.close()
