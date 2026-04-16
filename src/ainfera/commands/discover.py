"""ainfera discover — search the Ainfera marketplace for trusted agents."""

from __future__ import annotations

import json as _json

import click
from rich.table import Table

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url
from ainfera.ui.console import console


@click.command()
@click.argument("query")
@click.option("--min-trust", type=int, default=None, help="Minimum trust score (0-1000).")
@click.option(
    "--framework",
    default=None,
    help="Filter by framework (langchain, crewai, openclaw).",
)
@click.option("--channel", default=None, help="Filter by channel (telegram, slack, discord, whatsapp).")
@click.pass_context
def discover(
    ctx,
    query: str,
    min_trust: int | None,
    framework: str | None,
    channel: str | None,
):
    """Search the Ainfera marketplace for trusted agents.

    \b
    Examples:
      ainfera discover "research assistant"
      ainfera discover "data" --min-trust 800
      ainfera discover "writer" --framework langchain --channel telegram
    """
    json_output = ctx.obj.get("json", False)

    client = AinferaClient(api_key=ensure_authenticated(), api_url=get_api_url())
    try:
        with console.status("  [ainfera.muted]Searching marketplace...[/]"):
            data = client.discover_agents(
                query=query,
                min_trust=min_trust,
                framework=framework,
                channel=channel,
            )
    finally:
        client.close()

    if json_output:
        click.echo(_json.dumps(data))
        return

    items = data.get("items") or data.get("agents") or []
    total = data.get("total", len(items))

    console.print()
    console.print(f"  Found {total} agents matching [bold]\"{query}\"[/]")
    console.print()

    if not items:
        console.print("  [ainfera.muted]No agents found. Try a broader query or lower --min-trust.[/]")
        console.print()
        return

    table = Table(show_header=True, header_style="ainfera.brand", box=None, pad_edge=False)
    table.add_column("NAME", no_wrap=True)
    table.add_column("GRADE")
    table.add_column("SCORE", justify="right")
    table.add_column("FRAMEWORK")
    table.add_column("CHANNELS")

    for item in items:
        name = item.get("name", "—")
        grade = item.get("grade") or item.get("trust_grade") or "—"
        score = item.get("score") or item.get("trust_score") or item.get("overall_score")
        score_str = str(int(score)) if isinstance(score, (int, float)) else "—"
        fw = item.get("framework") or "—"
        channels = item.get("channels") or []
        channels_str = ", ".join(channels) if channels else "—"
        table.add_row(name, grade, score_str, fw, channels_str)

    console.print(table)
    console.print()
