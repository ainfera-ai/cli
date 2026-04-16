"""ainfera register — register your agent in the Ainfera discovery marketplace."""

from __future__ import annotations

import json as _json

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url
from ainfera.ui.console import console, print_success


def _split(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@click.command()
@click.option("--name", required=True, help="Agent name (unique within your account).")
@click.option("--description", default=None, help="Short description shown in the marketplace.")
@click.option(
    "--framework",
    default="openclaw",
    help="Agent framework (langchain, crewai, openclaw, custom).",
)
@click.option("--capabilities", default=None, help="Comma-separated capabilities (e.g. research,summarize).")
@click.option("--channels", default=None, help="Comma-separated channels (e.g. telegram,slack).")
@click.pass_context
def register(
    ctx,
    name: str,
    description: str | None,
    framework: str,
    capabilities: str | None,
    channels: str | None,
):
    """Register your agent in the Ainfera discovery marketplace.

    \b
    Examples:
      ainfera register --name my-agent --framework openclaw
      ainfera register --name analyst --description "..." --capabilities research,summarize
      ainfera register --name bot --channels telegram,slack
    """
    json_output = ctx.obj.get("json", False)

    client = AinferaClient(api_key=ensure_authenticated(), api_url=get_api_url())
    try:
        with console.status("  [ainfera.muted]Registering agent...[/]"):
            data = client.register_openclaw_agent(
                name=name,
                description=description,
                framework=framework,
                capabilities=_split(capabilities),
                channels=_split(channels),
            )
    finally:
        client.close()

    if json_output:
        click.echo(_json.dumps(data))
        return

    did = data.get("did") or data.get("agent_did") or "—"
    score = data.get("score") or data.get("trust_score") or data.get("overall_score") or "—"
    grade = data.get("grade") or data.get("trust_grade") or "—"
    marketplace = data.get("marketplace_url") or data.get("marketplace")
    badge = data.get("badge_url") or data.get("badge")

    console.print()
    print_success(f"Agent registered: [bold]{name}[/]")
    print_success(f"DID: [ainfera.brand]{did}[/]")
    print_success(f"Trust Score: [ainfera.brand]{grade} {score}[/]")
    if marketplace:
        print_success(f"Marketplace: {marketplace}")
    if badge:
        console.print(
            f"  [ainfera.success]✓[/] Badge: "
            f"[ainfera.muted][![Ainfera Trust]({badge})][/]"
        )
    console.print()
