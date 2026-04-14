"""ainfera init — scaffold ainfera.yaml in the current directory."""

from __future__ import annotations

import json
import os
from pathlib import Path

import click
from rich.panel import Panel
from rich.syntax import Syntax

from ainfera.ui.console import console, print_error, print_header, print_success

_FRAMEWORKS = [
    ("langchain", "LangChain"),
    ("crewai", "CrewAI"),
    ("openai_sdk", "OpenAI SDK"),
    ("autogen", "AutoGen"),
    ("adk", "ADK"),
    ("custom", "Custom"),
]

_TIERS = ["basic", "standard", "gpu"]


@click.command("init")
@click.option("--name", default=None, help="Agent name")
@click.option(
    "--framework",
    type=click.Choice([fw[0] for fw in _FRAMEWORKS], case_sensitive=False),
    default=None,
    help="Agent framework",
)
@click.option("--description", default=None, help="Short description")
@click.option(
    "--tier",
    type=click.Choice(_TIERS, case_sensitive=False),
    default=None,
    help="Compute tier",
)
@click.option("--force", is_flag=True, help="Overwrite existing ainfera.yaml")
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Use defaults instead of prompting (for scripts/CI)",
)
@click.pass_context
def init(
    ctx,
    name: str | None,
    framework: str | None,
    description: str | None,
    tier: str | None,
    force: bool,
    non_interactive: bool,
):
    """Create an ainfera.yaml config file in the current directory.

    \b
    Examples:
      ainfera init                                            # interactive
      ainfera init --name my-agent --framework langchain --tier standard
      ainfera init --force                                    # overwrite existing
    """
    json_output = ctx.obj.get("json", False)
    silent = json_output or non_interactive
    config_path = Path("ainfera.yaml")

    if config_path.exists() and not force:
        if silent:
            if json_output:
                click.echo(json.dumps({"error": "ainfera.yaml already exists"}))
            else:
                print_error(
                    "ainfera.yaml already exists. Re-run with --force to overwrite."
                )
            raise SystemExit(1)
        if not click.confirm(
            "  ainfera.yaml already exists. Overwrite?", default=False
        ):
            console.print("  [ainfera.muted]Aborted.[/]")
            return

    if not json_output:
        print_header()
        console.print("  [ainfera.info]Initializing Ainfera...[/]")
        console.print()

    if name is None:
        default_name = os.path.basename(os.getcwd())
        name = (
            default_name
            if silent
            else click.prompt("  Agent name", default=default_name)
        )

    if framework is None:
        framework = "custom" if silent else _prompt_framework(json_output)

    if description is None and not silent:
        description = click.prompt("  Description", default="", show_default=False)

    if tier is None:
        tier = (
            "standard"
            if silent
            else click.prompt(
                "  Compute tier",
                default="standard",
                type=click.Choice(_TIERS, case_sensitive=False),
            )
        )

    yaml_content = _render_yaml(
        name=name,
        framework=framework,
        description=description or "",
        tier=tier,
    )
    config_path.write_text(yaml_content)

    if json_output:
        click.echo(
            json.dumps(
                {
                    "path": str(config_path),
                    "name": name,
                    "framework": framework,
                    "description": description or "",
                    "tier": tier,
                }
            )
        )
        return

    console.print()
    syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=False)
    console.print(
        Panel(
            syntax,
            title="[bold]ainfera.yaml[/]",
            border_style="ainfera.muted",
            padding=(1, 2),
        )
    )
    console.print()
    print_success("Created ainfera.yaml")
    console.print()
    console.print("  [bold]Next steps:[/]")
    console.print("    1. Edit ainfera.yaml to customize your agent config")
    console.print("    2. Run [bold]ainfera deploy[/] to deploy your agent")
    console.print(
        "    3. Run [bold]ainfera trust score <agent-id>[/] to check trust scores"
    )
    console.print()


def _prompt_framework(json_output: bool) -> str:
    if json_output:
        return "custom"
    console.print("  [bold]Framework:[/]")
    for idx, (_, label) in enumerate(_FRAMEWORKS, start=1):
        console.print(f"    {idx}. {label}")
    choice = click.prompt(
        "  Select",
        type=click.IntRange(1, len(_FRAMEWORKS)),
        default=1,
    )
    return _FRAMEWORKS[choice - 1][0]


def _render_yaml(*, name: str, framework: str, description: str, tier: str) -> str:
    escaped = description.replace('"', '\\"')
    return (
        'version: "1"\n'
        "agent:\n"
        f"  name: {name}\n"
        f"  framework: {framework}\n"
        f'  description: "{escaped}"\n'
        "  compute:\n"
        f"    tier: {tier}\n"
        "    timeout: 30\n"
        "  trust:\n"
        "    min_score: 50\n"
        "    auto_kill_below: 20\n"
        "  billing:\n"
        "    model: per-call\n"
        "    price_per_call: 0.003\n"
    )
