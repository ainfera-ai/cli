"""ainfera init — detect framework and generate ainfera.yaml."""

from __future__ import annotations

import json
import os
from pathlib import Path

import click
from rich.panel import Panel
from rich.syntax import Syntax

from ainfera.config.yaml_parser import (
    AinferaConfig,
    InferenceConfig,
    generate_yaml,
)
from ainfera.ui.console import (
    console,
    print_error,
    print_header,
    print_success,
    print_warning,
)
from ainfera.utils.detect import detect_entrypoint, detect_framework


# Framework-specific inference defaults
_INFERENCE_DEFAULTS = {
    "langchain": InferenceConfig(provider="openai", model="gpt-4o-mini"),
    "crewai": InferenceConfig(provider="openai", model="gpt-4o-mini"),
    "autogen": InferenceConfig(provider="openai", model="gpt-4o-mini"),
    "openai_sdk": InferenceConfig(provider="openai", model="gpt-4o-mini"),
    "adk": InferenceConfig(provider="google", model="gemini-2.0-flash"),
    "custom": InferenceConfig(provider="openai", model="gpt-4o-mini"),
}


@click.command("init")
@click.option("--name", default=None, help="Agent name (default: directory name)")
@click.option(
    "--framework",
    type=click.Choice(
        ["langchain", "crewai", "autogen", "adk", "openai_sdk", "custom"]
    ),
    default=None,
    help="Override framework detection",
)
@click.option("--force", is_flag=True, help="Overwrite existing ainfera.yaml")
@click.pass_context
def init(ctx, name: str | None, framework: str | None, force: bool):
    """Initialize Ainfera in the current directory."""
    json_output = ctx.obj.get("json", False)
    config_path = Path("ainfera.yaml")

    if not json_output:
        print_header()
        console.print("  [ainfera.info]Initializing Ainfera...[/]")
        console.print()

    # Check for existing config
    if config_path.exists() and not force:
        if json_output:
            click.echo(json.dumps({"error": "ainfera.yaml already exists"}))
            raise SystemExit(1)
        print_error(
            "ainfera.yaml already exists.",
            "Use --force to overwrite.",
        )
        raise SystemExit(1)

    # Detect framework
    if framework:
        fw_name = framework
        details = {"framework": framework, "source_file": None, "confidence": "manual"}
    else:
        with console.status("  [ainfera.muted]Scanning project files...[/]"):
            fw_name, details = detect_framework(".")

    if not json_output:
        version_str = f" v{details['version']}" if details.get("version") else ""
        source_str = (
            f" (from {details['source_file']})" if details.get("source_file") else ""
        )
        print_success(
            f"Detected: [bold]{fw_name.replace('_', ' ').title()}[/]{version_str}{source_str}"
        )

        if details.get("confidence") == "low":
            print_warning(
                "Low confidence detection. Use --framework to specify manually."
            )

    # Detect entry point
    entrypoint = detect_entrypoint(".")
    if entrypoint and not json_output:
        print_success(f"Entry point: [bold]{entrypoint}[/]")

    # Determine agent name
    if name is None:
        name = os.path.basename(os.getcwd())
    if not json_output:
        print_success(f"Agent name: [bold]{name}[/]")

    # Build config
    inference = _INFERENCE_DEFAULTS.get(fw_name, _INFERENCE_DEFAULTS["custom"])
    config = AinferaConfig(
        name=name,
        framework=fw_name,
        inference=inference,
    )

    # Generate and write YAML
    yaml_content = generate_yaml(config)
    config_path.write_text(yaml_content)

    if json_output:
        click.echo(
            json.dumps(
                {
                    "framework": fw_name,
                    "config_path": str(config_path),
                    "config": config.model_dump(exclude_none=True),
                }
            )
        )
        return

    # Show the generated config
    console.print()
    syntax = Syntax(yaml_content, "yaml", theme="monokai", line_numbers=False)
    panel = Panel(
        syntax,
        title="[bold]ainfera.yaml[/bold]",
        border_style="ainfera.muted",
        padding=(1, 2),
    )
    console.print(panel)

    console.print()
    console.print("  [bold]Next steps:[/]")
    console.print("    1. Review ainfera.yaml and adjust settings")
    console.print("    2. Run [bold]ainfera deploy[/] to deploy your agent")
    console.print("    3. Run [bold]ainfera trust[/] to check your trust score")
    console.print()
