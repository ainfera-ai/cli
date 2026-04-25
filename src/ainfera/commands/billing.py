"""ainfera billing — usage and cost summary."""

from __future__ import annotations

import json

import click
from rich.table import Table

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url
from ainfera.ui.console import console


@click.command()
@click.option(
    "--period",
    default=None,
    metavar="YYYY-MM",
    help="Billing period (e.g. 2026-04). Defaults to current month.",
)
@click.option(
    "--agent",
    "agent_id",
    default=None,
    help="Restrict to a single agent ID. Omit to aggregate all agents.",
)
@click.pass_context
def billing(ctx, period: str | None, agent_id: str | None):
    """Show invocations, GPU seconds, and cost per agent.

    \b
    Examples:
      ainfera billing
      ainfera billing --period 2026-04
      ainfera billing --agent 8e7b4d6e-...
      ainfera --json billing
    """
    json_output = ctx.obj.get("json", False)
    client = _client()
    try:
        rows = _collect_rows(client, agent_id, period)
    finally:
        client.close()

    totals = _totals(rows)

    if json_output:
        click.echo(
            json.dumps(
                {
                    "period": period,
                    "agents": rows,
                    "totals": totals,
                }
            )
        )
        return

    _render_table(rows, totals, period)


def _client() -> AinferaClient:
    api_key = ensure_authenticated()
    return AinferaClient(api_key=api_key, api_url=get_api_url())


def _collect_rows(
    client: AinferaClient, agent_id: str | None, period: str | None
) -> list[dict]:
    targets: list[dict] = []
    if agent_id:
        agent = client.get_agent(agent_id)
        targets.append(agent)
    else:
        listing = client.list_agents(page=1, per_page=100)
        items = (
            listing.get("agents")
            or listing.get("items")
            or (listing if isinstance(listing, list) else [])
        )
        targets.extend(items)

    rows: list[dict] = []
    for a in targets:
        aid = a.get("id")
        if not aid:
            continue
        try:
            usage = client.get_usage(aid)
        except click.ClickException:
            usage = {}
        rows.append(
            {
                "id": aid,
                "name": a.get("name", aid),
                "invocations": _pick_int(usage, "invocations", "calls", "request_count"),
                "gpu_seconds": _pick_float(
                    usage, "gpu_seconds", "compute_seconds", "gpu_sec"
                ),
                "cost_usd": _pick_float(
                    usage, "cost_usd", "total_cost_usd", "cost", "total_cost"
                ),
                "metering": usage.get("metering_mode")
                or usage.get("billing_model")
                or "per_call",
                "period": usage.get("period") or period,
            }
        )
    return rows


def _totals(rows: list[dict]) -> dict:
    return {
        "invocations": sum(r["invocations"] for r in rows),
        "gpu_seconds": round(sum(r["gpu_seconds"] for r in rows), 2),
        "cost_usd": round(sum(r["cost_usd"] for r in rows), 4),
    }


def _pick_int(d: dict, *keys: str) -> int:
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)):
            return int(v)
    return 0


def _pick_float(d: dict, *keys: str) -> float:
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)):
            return float(v)
    return 0.0


def _render_table(rows: list[dict], totals: dict, period: str | None) -> None:
    console.print()
    title = "Billing Summary"
    if period:
        title += f"  [ainfera.muted]{period}[/]"
    console.print(f"  [bold]{title}[/]")
    console.print()

    if not rows:
        console.print("  [ainfera.muted]No agents found.[/]")
        console.print()
        return

    table = Table(border_style="ainfera.muted")
    table.add_column("Agent", style="bold")
    table.add_column("Metering", style="ainfera.muted")
    table.add_column("Invocations", justify="right")
    table.add_column("GPU Sec", justify="right")
    table.add_column("Cost (USD)", justify="right", style="ainfera.brand")

    for r in rows:
        table.add_row(
            r["name"],
            r["metering"],
            f"{r['invocations']:,}",
            f"{r['gpu_seconds']:,.2f}",
            f"${r['cost_usd']:,.4f}",
        )

    table.add_section()
    table.add_row(
        "[bold]TOTAL[/]",
        "",
        f"[bold]{totals['invocations']:,}[/]",
        f"[bold]{totals['gpu_seconds']:,.2f}[/]",
        f"[bold]${totals['cost_usd']:,.4f}[/]",
    )

    console.print(table)
    console.print()
