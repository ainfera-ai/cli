"""ainfera agents — manage agents."""

from __future__ import annotations

import json

import click
from rich.table import Table

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url
from ainfera.ui.console import console, print_success
from ainfera.ui.formatters import (
    format_agent_panel,
    format_agent_status,
    format_trust_score,
)


@click.group()
def agents():
    """Manage Ainfera agents."""


@agents.command("list")
@click.option("--page", default=1, type=int, help="Page number (default: 1)")
@click.option("--per-page", default=20, type=int, help="Items per page (default: 20)")
@click.pass_context
def list_cmd(ctx, page: int, per_page: int):
    """List your agents.

    \b
    Examples:
      ainfera agents list
      ainfera agents list --per-page 50
      ainfera --json agents list | jq '.items[].name'
    """
    json_output = ctx.obj.get("json", False)
    client = _client()
    try:
        response = client.list_agents(page=page, per_page=per_page)
    finally:
        client.close()

    agents_list = response.get("agents", response) if isinstance(response, dict) else response
    if isinstance(agents_list, dict):
        agents_list = agents_list.get("items", [])

    if json_output:
        click.echo(json.dumps(response))
        return

    if not agents_list:
        console.print()
        console.print("  [ainfera.muted]No agents found.[/]")
        console.print("  [ainfera.muted]Create one with 'ainfera agents create'.[/]")
        console.print()
        return

    table = Table(border_style="ainfera.muted")
    table.add_column("Name", style="bold")
    table.add_column("Framework", style="ainfera.muted")
    table.add_column("Trust", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Created", style="ainfera.muted")

    for a in agents_list:
        trust = (
            format_trust_score(
                a.get("current_trust_score", 0),
                a.get("trust_grade", "\u2014"),
            )
            if a.get("current_trust_score")
            else "[ainfera.muted]pending[/]"
        )
        table.add_row(
            a.get("name", ""),
            a.get("framework", ""),
            trust,
            format_agent_status(a.get("status", "unknown")),
            (a.get("created_at") or "")[:10],
        )
    console.print()
    console.print(table)
    console.print()


@agents.command("get")
@click.argument("agent_id")
@click.pass_context
def get_cmd(ctx, agent_id: str):
    """Show detailed info for a single agent.

    \b
    Examples:
      ainfera agents get 8e7b4d6e-...
      ainfera --json agents get 8e7b4d6e-... | jq .agent.status
    """
    json_output = ctx.obj.get("json", False)
    client = _client()
    try:
        agent = client.get_agent(agent_id)
        trust = None
        try:
            trust = client.get_trust_score(agent_id)
        except click.ClickException:
            trust = None
    finally:
        client.close()

    if json_output:
        click.echo(json.dumps({"agent": agent, "trust": trust}))
        return

    console.print()
    console.print(format_agent_panel(agent))
    if trust and trust.get("score") is not None:
        console.print()
        console.print(
            f"  Trust Score  {format_trust_score(trust['score'], trust.get('grade', '—'))}"
        )
    console.print()


@agents.command("create")
@click.option("--name", required=True, help="Agent name")
@click.option(
    "--framework",
    required=True,
    type=click.Choice(
        ["langchain", "crewai", "openclaw", "custom"],
        case_sensitive=False,
    ),
    help="Agent framework",
)
@click.option("--description", default=None, help="Optional description")
@click.option(
    "--tier",
    default=None,
    type=click.Choice(["basic", "standard", "gpu"], case_sensitive=False),
    help="Compute tier (encoded into config_yaml)",
)
@click.pass_context
def create_cmd(
    ctx, name: str, framework: str, description: str | None, tier: str | None
):
    """Create a new agent on the platform.

    \b
    Examples:
      ainfera agents create --name my-agent --framework langchain
      ainfera agents create --name analyzer --framework crewai --description 'Data analysis crew'
      ainfera agents create --name bot --framework openai_sdk --tier gpu
    """
    json_output = ctx.obj.get("json", False)
    config_yaml = _tier_yaml(tier) if tier else None
    client = _client()
    try:
        agent = client.create_agent(
            name=name,
            framework=framework,
            description=description,
            config_yaml=config_yaml,
        )
    finally:
        client.close()

    if json_output:
        click.echo(json.dumps(agent))
        return

    console.print()
    print_success(f"Agent '{name}' created. ID: {agent.get('id', '')}")
    console.print(format_agent_panel(agent))
    console.print()


@agents.command("delete")
@click.argument("agent_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_cmd(ctx, agent_id: str, yes: bool):
    """Delete an agent.

    \b
    Examples:
      ainfera agents delete 8e7b4d6e-...
      ainfera agents delete 8e7b4d6e-... --yes
    """
    json_output = ctx.obj.get("json", False)
    client = _client()
    try:
        name = agent_id
        try:
            agent = client.get_agent(agent_id)
            name = agent.get("name", agent_id)
        except click.ClickException:
            pass

        if not yes and not json_output:
            if not click.confirm(
                f"  Delete agent {name}? This cannot be undone.",
                default=False,
            ):
                console.print("  [ainfera.muted]Aborted.[/]")
                return

        client.delete_agent(agent_id)
    finally:
        client.close()

    if json_output:
        click.echo(json.dumps({"status": "deleted", "id": agent_id}))
        return

    print_success("Agent deleted.")


def _client() -> AinferaClient:
    api_key = ensure_authenticated()
    return AinferaClient(api_key=api_key, api_url=get_api_url())


def _tier_yaml(tier: str) -> str:
    return (
        'version: "1"\n'
        "agent:\n"
        "  compute:\n"
        f"    tier: {tier}\n"
    )
