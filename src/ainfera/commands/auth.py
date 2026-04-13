"""ainfera auth — authenticate and check auth status."""

from __future__ import annotations

import json
import os

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import (
    get_api_key,
    get_api_url,
    load_config,
    save_config,
)
from ainfera.ui.console import console, print_error, print_success


@click.group()
def auth():
    """Manage authentication with the Ainfera platform."""


@auth.command("login")
@click.option("--key", default=None, help="Ainfera API key (starts with ainf_)")
@click.option("--api-url", default=None, help="Override API URL for this session")
@click.pass_context
def auth_login(ctx, key: str | None, api_url: str | None):
    """Authenticate with an API key and save it to ~/.ainfera/config.yaml.

    \b
    Examples:
      ainfera auth login                              # interactive prompt
      ainfera auth login --key ainf_xxx
      AINFERA_API_KEY=ainf_xxx ainfera auth login
      ainfera auth login --api-url https://api.staging.ainfera.ai
    """
    json_output = ctx.obj.get("json", False)

    if key is None:
        key = os.environ.get("AINFERA_API_KEY")
    if key is None:
        key = click.prompt("  API key", hide_input=True)

    if api_url is None:
        api_url = get_api_url()

    if not key.startswith("ainf_"):
        if json_output:
            click.echo(json.dumps({"error": "Invalid API key format"}))
            raise SystemExit(1)
        print_error(
            "Invalid API key format. Keys start with 'ainf_'.",
            "Get your API key at https://console.ainfera.ai/settings/api-keys",
        )
        raise SystemExit(1)

    client = AinferaClient(api_key=key, api_url=api_url)
    user_identity = None
    try:
        with console.status("  [ainfera.muted]Verifying API key...[/]"):
            health = client.health()
            user_identity = health.get("user") or health.get("account")
    except click.ClickException as e:
        if json_output:
            click.echo(json.dumps({"error": str(e)}))
            raise SystemExit(1)
        print_error("Could not verify API key.", str(e))
        raise SystemExit(1)
    finally:
        client.close()

    config = load_config()
    config["api_key"] = key
    config["api_url"] = api_url
    save_config(config)

    if json_output:
        click.echo(
            json.dumps(
                {"status": "authenticated", "api_url": api_url, "user": user_identity}
            )
        )
        return

    who = user_identity or "ainfera"
    print_success(f"Authenticated as {who}. API: {api_url}")


@auth.command("status")
@click.pass_context
def auth_status(ctx):
    """Show current authentication status and API health.

    \b
    Examples:
      ainfera auth status
      ainfera --json auth status
    """
    json_output = ctx.obj.get("json", False)

    api_key = get_api_key()
    api_url = get_api_url()
    masked = _mask_key(api_key)

    health_ok = False
    health_info: dict = {}
    if api_key:
        client = AinferaClient(api_key=api_key, api_url=api_url)
        try:
            health_info = client.health()
            health_ok = True
        except click.ClickException:
            health_ok = False
        finally:
            client.close()

    if json_output:
        click.echo(
            json.dumps(
                {
                    "api_url": api_url,
                    "api_key": masked,
                    "authenticated": bool(api_key),
                    "api_healthy": health_ok,
                    "health": health_info,
                }
            )
        )
        return

    console.print()
    console.print(f"  API URL:   [bold]{api_url}[/]")
    console.print(f"  API Key:   [ainfera.muted]{masked}[/]")
    if not api_key:
        print_error(
            "Not authenticated.",
            "Run 'ainfera auth login' to set your API key.",
        )
        raise SystemExit(1)
    if health_ok:
        print_success("API reachable and healthy.")
    else:
        print_error("API unreachable or auth failed.")
        raise SystemExit(1)


def _mask_key(key: str | None) -> str:
    if not key:
        return "<not set>"
    if len(key) <= 10:
        return "ainf_" + "*" * 6
    return key[:9] + "*" * (len(key) - 13) + key[-4:]
