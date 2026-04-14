"""ainfera status — platform-wide overview."""

from __future__ import annotations

import json

import click
import httpx
from rich.panel import Panel

from ainfera import __version__
from ainfera.api.client import AinferaClient
from ainfera.config.settings import (
    CONFIG_FILE,
    get_api_key,
    get_api_url,
)
from ainfera.ui.console import console


@click.command()
@click.pass_context
def status(ctx):
    """Show the full Ainfera platform overview.

    \b
    Examples:
      ainfera status
      ainfera --json status
    """
    json_output = ctx.obj.get("json", False)
    api_url = get_api_url()
    api_key = get_api_key()

    health_data: dict | None = None
    health_error: str | None = None
    try:
        with httpx.Client(base_url=api_url, timeout=10.0) as client:
            r = client.get("/health")
            if r.status_code == 200:
                health_data = r.json()
            else:
                health_error = f"HTTP {r.status_code}"
    except httpx.ConnectError:
        health_error = "connection refused"
    except httpx.TimeoutException:
        health_error = "timeout"
    except Exception as e:
        health_error = str(e)

    auth_ok = False
    auth_user: str | None = None
    agent_stats: dict | None = None
    if api_key and health_data:
        ac = AinferaClient(api_key=api_key, api_url=api_url)
        try:
            listing = ac.list_agents(page=1, per_page=50)
            auth_ok = True
            items = (
                listing.get("agents")
                or listing.get("items")
                or (listing if isinstance(listing, list) else [])
            )
            total = listing.get("total") if isinstance(listing, dict) else None
            if total is None:
                total = len(items)
            published = sum(1 for a in items if a.get("status") == "published")
            draft = sum(1 for a in items if a.get("status") == "draft")
            scores = [
                a.get("current_trust_score")
                for a in items
                if isinstance(a.get("current_trust_score"), (int, float))
            ]
            avg_trust = round(sum(scores) / len(scores), 1) if scores else None
            agent_stats = {
                "total_agents": total,
                "published_agents": published,
                "draft_agents": draft,
                "avg_trust_score": avg_trust,
            }
        except click.ClickException:
            auth_ok = False
        finally:
            ac.close()

    payload = {
        "api_url": api_url,
        "api_online": health_data is not None,
        "api_error": health_error,
        "api_version": (health_data or {}).get("version"),
        "services": (health_data or {}).get("services", {}),
        "stats": agent_stats or (health_data or {}).get("stats"),
        "cli_version": __version__,
        "authenticated": bool(api_key) and auth_ok,
        "user": auth_user,
        "config_path": str(CONFIG_FILE),
    }

    if json_output:
        click.echo(json.dumps(payload))
        return

    console.print()
    console.print(Panel(_render(payload), title="[bold]Ainfera Platform Status[/]",
                       border_style="ainfera.brand", padding=(1, 2)))
    console.print()


def _dot(ok: bool) -> str:
    return "[ainfera.success]\u25cf[/]" if ok else "[ainfera.error]\u25cf[/]"


def _empty() -> str:
    return "[ainfera.muted]\u25cb[/]"


def _render(p: dict) -> str:
    services = p.get("services") or {}
    stats = p.get("stats") or {}

    api_status = (
        f"{_dot(True)} online" if p["api_online"]
        else f"{_dot(False)} offline ({p.get('api_error') or 'unknown'})"
    )

    db_ok = services.get("db") == "ok"
    redis_ok = services.get("redis") == "ok"
    db_line = (
        f"{_dot(db_ok)} {services.get('db', 'unknown')}"
        if "db" in services
        else "[ainfera.muted]unknown[/]"
    )
    redis_line = (
        f"{_dot(redis_ok)} {services.get('redis', 'unknown')}"
        if "redis" in services
        else "[ainfera.muted]unknown[/]"
    )

    lines = [
        f"  API:      [bold]{p['api_url']}[/]   {api_status}",
        f"  Version:  {p.get('api_version') or '[ainfera.muted]?[/]'}",
        f"  DB:       {db_line}",
        f"  Redis:    {redis_line}",
        "",
    ]

    if stats:
        total = stats.get("total_agents", stats.get("agents_total", "?"))
        published = stats.get("published_agents", stats.get("agents_published"))
        draft = stats.get("draft_agents", stats.get("agents_draft"))
        avg_trust = stats.get("avg_trust_score") or stats.get("average_trust_score")
        avg_grade = stats.get("avg_trust_grade") or stats.get("average_trust_grade") or "\u2014"
        breakdown = ""
        if published is not None and draft is not None:
            breakdown = f" ({published} published, {draft} draft)"
        lines.append(f"  Agents:   [bold]{total}[/]{breakdown}")
        if avg_trust is not None:
            lines.append(f"  Avg Trust: [bold]{avg_trust}[/] ({avg_grade})")
        lines.append("")

    lines.append(f"  CLI:      ainfera v{p['cli_version']}")
    if p["authenticated"]:
        who = p.get("user")
        suffix = f" as [bold]{who}[/]" if who else ""
        lines.append(f"  Auth:     {_dot(True)} authenticated{suffix}")
    elif get_api_key():
        lines.append(f"  Auth:     {_dot(False)} api key set but not verified")
    else:
        lines.append(
            f"  Auth:     {_empty()} not authenticated \u2014 run "
            "[bold]'ainfera auth login'[/]"
        )
    lines.append(f"  Config:   [ainfera.muted]{p['config_path']}[/]")

    return "\n".join(lines)
