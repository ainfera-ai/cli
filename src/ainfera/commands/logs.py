"""ainfera logs — view or stream agent execution logs."""

from __future__ import annotations

import asyncio
import json

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url, get_default_agent
from ainfera.ui.console import console, print_error, print_header


@click.command()
@click.argument("agent_id", required=False)
@click.option("--follow", "-f", is_flag=True, help="Stream logs in real-time")
@click.option("--tail", default=50, help="Number of recent log lines")
@click.pass_context
def logs(ctx, agent_id: str | None, follow: bool, tail: int):
    """View or stream agent execution logs."""
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
        if follow:
            _stream_logs(client, agent_id, json_output)
        else:
            _show_logs(client, agent_id, tail, json_output)
    finally:
        client.close()


def _show_logs(
    client: AinferaClient, agent_id: str, tail: int, json_output: bool
):
    """Fetch and display recent logs."""
    with console.status("  [ainfera.muted]Fetching logs...[/]"):
        raw = client.get_logs(agent_id, tail=tail)

    if json_output:
        click.echo(json.dumps({"agent_id": agent_id, "logs": raw}))
        return

    print_header()
    console.print(f"  [ainfera.brand]\u25c6 AINFERA[/] \u2014 logs (last {tail} lines)")
    console.print()

    for line in raw.strip().splitlines():
        _print_log_line(line)

    console.print()


def _stream_logs(client: AinferaClient, agent_id: str, json_output: bool):
    """Stream logs via WebSocket."""
    try:
        import websockets
    except ImportError:
        print_error(
            "websockets package required for --follow.",
            "Install it: pip install websockets",
        )
        raise SystemExit(1)

    # Get the agent to find the current execution
    agent = client.get_agent(agent_id)
    execution_id = agent.get("current_execution_id", agent_id)

    if not json_output:
        print_header()
        console.print(
            f"  [ainfera.brand]\u25c6 AINFERA[/] \u2014 streaming logs (Ctrl+C to stop)"
        )
        console.print()

    ws_url = client.get_stream_url(execution_id)

    async def _ws_stream():
        try:
            async with websockets.connect(ws_url) as ws:
                async for message in ws:
                    if json_output:
                        click.echo(message)
                    else:
                        _print_ws_message(message)
        except Exception as e:
            if not json_output:
                console.print(f"  [ainfera.muted]Stream ended: {e}[/]")

    try:
        asyncio.run(_ws_stream())
    except KeyboardInterrupt:
        if not json_output:
            console.print()
            console.print("  [ainfera.muted]Stream stopped.[/]")


def _print_log_line(line: str):
    """Format and print a single log line with syntax highlighting."""
    # Try to parse structured log: "TIMESTAMP [LEVEL] message"
    parts = line.split(None, 2)
    if len(parts) >= 2:
        ts = parts[0]
        rest = " ".join(parts[1:])

        # Color by level keywords
        lower = rest.lower()
        if "error" in lower or "fatal" in lower:
            style = "ainfera.error"
        elif "warn" in lower:
            style = "ainfera.warning"
        elif "ainfera" in lower or "\u25c6" in line:
            style = "ainfera.brand"
        else:
            style = "ainfera.info"

        console.print(f"  [ainfera.muted]{ts}[/] [{style}]{rest}[/{style}]")
    else:
        console.print(f"  {line}")


def _print_ws_message(raw: str):
    """Format a WebSocket log message."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        console.print(f"  {raw}")
        return

    msg_type = data.get("type", "log")
    ts = data.get("timestamp", "")[:8]

    if msg_type == "heartbeat":
        return

    if msg_type == "log":
        level = data.get("level", "info")
        style = {
            "error": "ainfera.error",
            "warn": "ainfera.warning",
            "debug": "ainfera.muted",
        }.get(level, "ainfera.info")
        console.print(
            f"  [ainfera.muted]{ts}[/] [{style}][{level}][/{style}]  {data.get('message', '')}"
        )
    elif msg_type == "metric":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.info]"
            f"CPU: {data.get('cpu', 0)}% | Memory: {data.get('memory', '0MB')}[/]"
        )
    elif msg_type == "inference":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.brand]\u25c6 inference[/] | "
            f"{data.get('provider', '')}/{data.get('model', '')} | "
            f"{data.get('latency_ms', 0)}ms | {data.get('tokens', 0)} tok | "
            f"${data.get('cost', 0):.4f}"
        )
    elif msg_type == "trust_event":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.warning]\u25c6 trust[/] | "
            f"{data.get('message', '')}"
        )
    elif msg_type == "status_change":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.highlight]\u25c6 status[/] | "
            f"{data.get('message', '')}"
        )
    else:
        console.print(f"  [ainfera.muted]{ts}[/] {data.get('message', raw)}")
