"""ainfera deploy — deploy agent to Ainfera platform."""

from __future__ import annotations

import json
import time
from pathlib import Path

import click
from rich.panel import Panel

from ainfera.api.client import AinferaClient
from ainfera.config.settings import (
    ensure_authenticated,
    get_api_url,
    set_default_agent,
)
from ainfera.config.yaml_parser import load_yaml_file
from ainfera.ui.console import console, print_error, print_header, print_step
from ainfera.ui.formatters import format_trust_score, format_kill_switch_status
from ainfera.utils.git import get_git_branch, get_git_remote_url


@click.command()
@click.option(
    "--config",
    "config_path",
    default="ainfera.yaml",
    type=click.Path(),
    help="Path to ainfera.yaml",
)
@click.option("--local", is_flag=True, help="Deploy locally in Docker (not to cloud)")
@click.option("--watch", is_flag=True, help="Stream logs after deploy")
@click.pass_context
def deploy(ctx, config_path: str, local: bool, watch: bool):
    """Deploy your agent to Ainfera."""
    json_output = ctx.obj.get("json", False)

    # Validate config file exists
    if not Path(config_path).exists():
        print_error(
            f"{config_path} not found.",
            "Run `ainfera init` to generate one.",
        )
        raise SystemExit(1)

    if not json_output:
        print_header()

    # Step 1: Read configuration
    if not json_output:
        console.print("  [ainfera.info]Deploying...[/]")
        console.print()

    try:
        config = load_yaml_file(config_path)
    except Exception as e:
        print_error(f"Invalid {config_path}: {e}")
        raise SystemExit(1)

    if not json_output:
        print_step("Reading configuration", f"{config_path} \u2713", done=True)
        console.print(f"    Framework: [ainfera.muted]{config.framework}[/]")
        console.print(
            f"    Compute: [ainfera.muted]{config.compute.sandbox} / "
            f"{config.compute.memory} / {config.compute.cpu} cpu / "
            f"{config.compute.timeout} timeout[/]"
        )
        console.print(
            f"    Billing: [ainfera.muted]{config.billing.model} @ "
            f"${config.billing.price_per_call} "
            f"({int(config.billing.creator_share * 100)}/{int((1 - config.billing.creator_share) * 100)} split)[/]"
        )
        console.print()

    # Handle local deploy
    if local:
        _deploy_local(config, json_output)
        return

    # Authenticate
    api_key = ensure_authenticated()
    client = AinferaClient(api_key=api_key, api_url=get_api_url())

    try:
        # Step 2: Register agent
        repo_url = get_git_remote_url()
        branch = get_git_branch()
        yaml_content = Path(config_path).read_text()

        with console.status("  [ainfera.muted]Registering agent...[/]"):
            agent = client.create_agent(
                name=config.name,
                framework=config.framework,
                repo_url=repo_url,
                branch=branch,
                config_yaml=yaml_content,
            )

        agent_id = agent["id"]
        set_default_agent(agent_id)

        if not json_output:
            print_step("Registering agent", "\u2713", done=True)
            console.print(f"    Agent ID: [ainfera.muted]{agent_id}[/]")
            console.print()

        # Step 3: Deploy to sandbox
        with console.status("  [ainfera.muted]Deploying to sandbox...[/]"):
            deploy_result = client.deploy_agent(agent_id)

        if not json_output:
            print_step("Deploying to sandbox", "\u2713", done=True)
            container = deploy_result.get("container_id", "")
            if container:
                console.print(
                    f"    Container: [ainfera.muted]{container} ({config.framework})[/]"
                )
            console.print(
                f"    Status: [ainfera.success]{deploy_result.get('status', 'running')}[/]"
            )
            console.print()

        # Step 4: Compute trust score (poll)
        trust_data = None
        if not json_output:
            with console.status("  [ainfera.muted]Computing trust score...[/]"):
                trust_data = _poll_trust_score(client, agent_id)
        else:
            trust_data = _poll_trust_score(client, agent_id)

        if not json_output and trust_data:
            print_step("Computing trust score", "\u2713", done=True)
            console.print()

        # Step 5: Summary
        if json_output:
            result = {
                "agent_id": agent_id,
                "status": deploy_result.get("status", "running"),
                "trust_score": trust_data.get("score") if trust_data else None,
                "trust_grade": trust_data.get("grade") if trust_data else None,
                "deploy_url": f"https://console.ainfera.ai/agents/{agent_id}",
                "badge_url": f"https://api.ainfera.ai/v1/trust/{agent_id}/badge",
            }
            click.echo(json.dumps(result))
        else:
            _print_deploy_summary(config, agent_id, deploy_result, trust_data)

        # Optional: stream logs
        if watch and not json_output:
            execution_id = deploy_result.get("execution_id")
            if execution_id:
                _stream_logs(client, execution_id)

    finally:
        client.close()


def _poll_trust_score(
    client: AinferaClient, agent_id: str, timeout: int = 30
) -> dict | None:
    """Poll for trust score with timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            data = client.get_trust_score(agent_id)
            if data.get("score") is not None:
                return data
        except click.ClickException:
            pass
        time.sleep(2)
    return None


def _print_deploy_summary(
    config, agent_id: str, deploy_result: dict, trust_data: dict | None
):
    """Print the deploy success panel."""
    lines = []
    lines.append("")
    lines.append(
        f"  [ainfera.brand]\u25c6 {config.name} deployed successfully[/ainfera.brand]"
    )
    lines.append("")

    if trust_data and trust_data.get("score"):
        lines.append(
            f"  Trust Score    {format_trust_score(trust_data['score'], trust_data.get('grade', '\u2014'))}"
        )
    else:
        lines.append("  Trust Score    [ainfera.muted]computing...[/]")

    lines.append(
        f"  Status         [ainfera.success]{deploy_result.get('status', 'running')}[/]"
    )
    lines.append(f"  Kill Switch    {format_kill_switch_status('armed')}")
    lines.append(
        f"  Billing        [ainfera.muted]${config.billing.price_per_call} / call[/]"
    )
    lines.append("")

    console_url = f"https://console.ainfera.ai/agents/{agent_id}"
    badge_url = f"https://api.ainfera.ai/v1/trust/{agent_id}/badge"
    lines.append(f"  Console   [ainfera.muted]{console_url}[/]")
    lines.append(f"  Badge     [ainfera.muted]{badge_url}[/]")
    lines.append("")
    lines.append("  Add badge to README:")
    lines.append(f"  [ainfera.muted][![Trust]({badge_url})]({console_url})[/]")
    lines.append("")

    panel = Panel(
        "\n".join(lines),
        border_style="ainfera.success",
        padding=(0, 2),
    )
    console.print(panel)
    console.print()


def _deploy_local(config, json_output: bool):
    """Deploy locally using Docker."""
    import subprocess

    image = f"ainfera/sandbox-{config.framework}:latest"
    cmd = ["docker", "run", "--rm", "-v", f"{Path.cwd()}:/agent", image]

    if json_output:
        click.echo(json.dumps({"mode": "local", "command": " ".join(cmd)}))
        return

    print_step("Deploying locally", f"docker ({config.framework})")
    console.print(f"    [ainfera.muted]$ {' '.join(cmd)}[/]")
    console.print()

    try:
        subprocess.run(cmd, check=True)
        print_step("Local deploy complete", "\u2713", done=True)
    except FileNotFoundError:
        print_error("Docker not found.", "Install Docker: https://docs.docker.com/get-docker/")
        raise SystemExit(1)
    except subprocess.CalledProcessError as e:
        print_error(f"Docker exited with code {e.returncode}")
        raise SystemExit(1)


def _stream_logs(client: AinferaClient, execution_id: str):
    """Stream execution logs via WebSocket."""
    import asyncio

    try:
        import websockets
    except ImportError:
        print_error("websockets package required for --watch")
        return

    console.print("  [ainfera.muted]Streaming logs (Ctrl+C to stop)...[/]")
    console.print()

    async def _ws_stream():
        url = client.get_stream_url(execution_id)
        try:
            async with websockets.connect(url) as ws:
                async for message in ws:
                    _format_log_message(message)
        except websockets.ConnectionClosed:
            console.print("  [ainfera.muted]Stream ended.[/]")

    try:
        asyncio.run(_ws_stream())
    except KeyboardInterrupt:
        console.print()
        console.print("  [ainfera.muted]Stream stopped.[/]")


def _format_log_message(raw: str):
    """Format and print a single log message."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        console.print(f"  {raw}")
        return

    msg_type = data.get("type", "log")
    ts = data.get("timestamp", "")[:8]

    if msg_type == "log":
        level = data.get("level", "info")
        style = {"error": "ainfera.error", "warn": "ainfera.warning"}.get(
            level, "ainfera.info"
        )
        console.print(f"  [ainfera.muted]{ts}[/] [{style}]{data.get('message', '')}[/{style}]")
    elif msg_type == "inference":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.brand]\u25c6 inference[/] | "
            f"{data.get('provider', '')}/{data.get('model', '')} | "
            f"{data.get('latency_ms', 0)}ms | {data.get('tokens', 0)} tok | "
            f"${data.get('cost', 0):.4f}"
        )
    elif msg_type == "trust_event":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.warning]\u25c6 trust[/] | {data.get('message', '')}"
        )
    elif msg_type == "status_change":
        console.print(
            f"  [ainfera.muted]{ts}[/] [ainfera.highlight]\u25c6 status[/] | {data.get('message', '')}"
        )
