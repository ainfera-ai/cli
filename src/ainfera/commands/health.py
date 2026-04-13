"""ainfera health — check API health."""

from __future__ import annotations

import json

import click
import httpx

from ainfera.config.settings import get_api_url
from ainfera.ui.console import print_error, print_success


@click.command()
@click.pass_context
def health(ctx):
    """Check the Ainfera API health status (no auth required)."""
    json_output = ctx.obj.get("json", False)
    api_url = get_api_url()

    try:
        with httpx.Client(base_url=api_url, timeout=10.0) as client:
            response = client.get("/health")
    except httpx.ConnectError:
        if json_output:
            click.echo(json.dumps({"ok": False, "error": "connection_error"}))
            raise SystemExit(1)
        print_error(f"Cannot connect to {api_url}")
        raise SystemExit(1)
    except httpx.TimeoutException:
        if json_output:
            click.echo(json.dumps({"ok": False, "error": "timeout"}))
            raise SystemExit(1)
        print_error("API health check timed out.")
        raise SystemExit(1)

    if response.status_code >= 400:
        if json_output:
            click.echo(
                json.dumps({"ok": False, "status_code": response.status_code})
            )
            raise SystemExit(1)
        print_error(f"API returned HTTP {response.status_code}")
        raise SystemExit(1)

    try:
        data = response.json()
    except ValueError:
        data = {"raw": response.text}

    if json_output:
        click.echo(json.dumps(data))
        return

    version = data.get("version", "?")
    services = data.get("services") or {}
    db = services.get("db", data.get("db", "?"))
    redis = services.get("redis", data.get("redis", "?"))
    print_success(f"API healthy. Version: {version}. DB: {db}. Redis: {redis}.")
