"""ainfera deploy — read ainfera.yaml and create or update the agent."""

from __future__ import annotations

import json
from pathlib import Path

import click
import yaml
from rich.panel import Panel

from ainfera.api.client import AinferaClient
from ainfera.config.settings import (
    ensure_authenticated,
    get_api_url,
    set_default_agent,
)
from ainfera.ui.console import console, print_error, print_header


@click.command()
@click.option(
    "--config",
    "config_path",
    default="ainfera.yaml",
    type=click.Path(),
    help="Path to ainfera.yaml",
)
@click.option("--dry-run", is_flag=True, help="Show planned action without calling the API")
@click.option(
    "--from-config",
    is_flag=True,
    help="Send raw YAML to POST /v1/agents/from-config",
)
@click.pass_context
def deploy(ctx, config_path: str, dry_run: bool, from_config: bool):
    """Deploy your agent from ainfera.yaml.

    \b
    Examples:
      ainfera deploy                                 # reads ./ainfera.yaml
      ainfera deploy --dry-run                       # show plan, don't call API
      ainfera deploy --config ./agents/bot.yaml
      ainfera deploy --from-config                   # send raw YAML to /v1/agents/from-config
    """
    json_output = ctx.obj.get("json", False)

    path = Path(config_path)
    if not path.exists():
        if json_output:
            click.echo(
                json.dumps(
                    {"error": f"{config_path} not found. Run 'ainfera init' to create one."}
                )
            )
            raise SystemExit(1)
        print_error(
            f"No {config_path} found.",
            "Run 'ainfera init' to create one.",
        )
        raise SystemExit(1)

    raw_yaml = path.read_text()
    try:
        parsed = yaml.safe_load(raw_yaml) or {}
    except yaml.YAMLError as e:
        if json_output:
            click.echo(json.dumps({"error": f"Invalid YAML: {e}"}))
            raise SystemExit(1)
        print_error(f"Invalid {config_path}: {e}")
        raise SystemExit(1)

    agent_section = parsed.get("agent") or {}
    if not agent_section:
        print_error(
            f"{config_path} is missing the 'agent:' section.",
            "Run 'ainfera init' to scaffold a valid file.",
        )
        raise SystemExit(1)

    name = agent_section.get("name")
    framework = agent_section.get("framework")
    description = agent_section.get("description", "")
    compute = agent_section.get("compute") or {}
    tier = compute.get("tier", "standard")
    trust_cfg = agent_section.get("trust") or {}
    min_score = trust_cfg.get("min_score", 50)
    auto_kill = trust_cfg.get("auto_kill_below", 20)

    if not name or not framework:
        print_error(
            "ainfera.yaml must include agent.name and agent.framework.",
        )
        raise SystemExit(1)

    if dry_run:
        _print_dry_run(
            name=name,
            framework=framework,
            tier=tier,
            min_score=min_score,
            auto_kill=auto_kill,
            from_config=from_config,
            json_output=json_output,
        )
        return

    if not json_output:
        print_header()

    api_key = ensure_authenticated()
    client = AinferaClient(api_key=api_key, api_url=get_api_url())

    try:
        if from_config:
            with console.status("  [ainfera.muted]Deploying from config...[/]"):
                agent = client.create_agent_from_config(raw_yaml)
            action = "created"
        else:
            existing = _find_existing_by_name(client, name)
            if existing:
                agent_id = existing["id"]
                with console.status(
                    f"  [ainfera.muted]Updating agent {agent_id}...[/]"
                ):
                    agent = client.update_agent(
                        agent_id,
                        framework=framework,
                        description=description,
                        config_yaml=raw_yaml,
                    )
                action = "updated"
            else:
                with console.status("  [ainfera.muted]Creating agent...[/]"):
                    agent = client.create_agent(
                        name=name,
                        framework=framework,
                        description=description,
                        config_yaml=raw_yaml,
                    )
                action = "created"

        agent_id = agent.get("id", "")
        if agent_id:
            set_default_agent(agent_id)

        if json_output:
            click.echo(json.dumps({"action": action, "agent": agent}))
            return

        _print_summary(
            name=name,
            framework=framework,
            tier=tier,
            min_score=min_score,
            auto_kill=auto_kill,
            agent=agent,
            action=action,
        )
    finally:
        client.close()


def _find_existing_by_name(client: AinferaClient, name: str) -> dict | None:
    try:
        response = client.list_agents(name=name, per_page=50)
    except click.ClickException:
        return None
    items = response.get("agents") if isinstance(response, dict) else None
    if items is None and isinstance(response, dict):
        items = response.get("items", [])
    if not items:
        return None
    for item in items:
        if item.get("name") == name:
            return item
    return None


def _print_dry_run(
    *,
    name: str,
    framework: str,
    tier: str,
    min_score: int,
    auto_kill: int,
    from_config: bool,
    json_output: bool,
):
    if json_output:
        click.echo(
            json.dumps(
                {
                    "dry_run": True,
                    "name": name,
                    "framework": framework,
                    "tier": tier,
                    "endpoint": (
                        "/v1/agents/from-config" if from_config else "/v1/agents"
                    ),
                }
            )
        )
        return
    print_header()
    endpoint = "/v1/agents/from-config" if from_config else "/v1/agents"
    console.print(
        Panel(
            f"\n  Agent:     {name}\n"
            f"  Framework: {framework}\n"
            f"  Tier:      {tier}\n"
            f"  Trust Min: {min_score}\n"
            f"  Kill Below: {auto_kill}\n\n"
            f"  [ainfera.muted]Would POST to {endpoint} (dry-run).[/]\n",
            title="[bold]Deploy Plan[/]",
            border_style="ainfera.muted",
            padding=(0, 2),
        )
    )


def _print_summary(
    *,
    name: str,
    framework: str,
    tier: str,
    min_score: int,
    auto_kill: int,
    agent: dict,
    action: str,
):
    agent_id = agent.get("id", "")
    status_str = agent.get("status", "published")
    url = f"https://api.ainfera.ai/v1/agents/{agent_id}"

    lines = [
        "",
        f"  Agent:     [bold]{name}[/]",
        f"  Framework: [ainfera.muted]{framework}[/]",
        f"  Tier:      [ainfera.muted]{tier}[/]",
        f"  Status:    [ainfera.success]{status_str}[/]",
        f"  Trust Min: [ainfera.muted]{min_score}[/]",
        f"  Kill Below: [ainfera.muted]{auto_kill}[/]",
        "",
        f"  [ainfera.success]\u2713 {action.capitalize()} successfully[/]",
        f"  ID: [ainfera.muted]{agent_id}[/]",
        f"  URL: [ainfera.muted]{url}[/]",
        "",
    ]
    console.print(
        Panel(
            "\n".join(lines),
            title="[bold]Deploy Summary[/]",
            border_style="ainfera.success",
            padding=(0, 2),
        )
    )
    console.print()
