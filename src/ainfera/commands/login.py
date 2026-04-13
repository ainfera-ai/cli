"""ainfera login — authenticate with the Ainfera platform."""

from __future__ import annotations

import json
import os

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import get_api_url, save_config, load_config
from ainfera.ui.console import console, print_error, print_header, print_success


@click.command()
@click.option(
    "--key",
    default=None,
    help="Ainfera API key (starts with ainf_)",
)
@click.option(
    "--api-url",
    default=None,
    help="Ainfera API URL (default: https://api.ainfera.ai)",
)
@click.pass_context
def login(ctx, key: str | None, api_url: str | None):
    """Authenticate with the Ainfera platform."""
    json_output = ctx.obj.get("json", False)

    # Resolve API key: flag → env var → prompt
    if key is None:
        key = os.environ.get("AINFERA_API_KEY")
    if key is None:
        key = click.prompt("  API key", hide_input=True)

    # Resolve API URL
    if api_url is None:
        api_url = get_api_url()

    # Validate key format
    if not key.startswith("ainf_"):
        if json_output:
            click.echo(json.dumps({"error": "Invalid API key format"}))
            raise SystemExit(1)
        print_error(
            "Invalid API key format. Keys start with [bold]ainf_[/bold].",
            "Get your API key at https://console.ainfera.ai/settings/api-keys",
        )
        raise SystemExit(1)

    if not json_output:
        print_header()

    # Test the key
    client = AinferaClient(api_key=key, api_url=api_url)
    try:
        with console.status("  [ainfera.muted]Verifying API key...[/]"):
            client.health()
    except click.ClickException:
        if json_output:
            click.echo(json.dumps({"error": "Authentication failed"}))
            raise SystemExit(1)
        print_error(
            "Could not verify API key.",
            "Check your key and try again, or visit https://console.ainfera.ai",
        )
        raise SystemExit(1)
    finally:
        client.close()

    # Save to config
    config = load_config()
    config["api_key"] = key
    config["api_url"] = api_url
    save_config(config)

    if json_output:
        click.echo(json.dumps({"status": "authenticated", "api_url": api_url}))
    else:
        print_success("Authenticated successfully")
        console.print(f"  [ainfera.muted]Config saved to ~/.ainfera/config.yaml[/]")
        console.print()
