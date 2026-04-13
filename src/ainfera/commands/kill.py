"""ainfera kill — trigger or clear the kill switch."""

from __future__ import annotations

import json

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url, get_default_agent
from ainfera.ui.console import console, print_error, print_header, print_success


@click.command()
@click.argument("agent_id", required=False)
@click.option("--reason", default="manual_kill", help="Reason for kill")
@click.option("--unkill", is_flag=True, help="Clear kill switch (un-quarantine)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def kill(ctx, agent_id: str | None, reason: str, unkill: bool, yes: bool):
    """Trigger or clear the kill switch for an agent.

    \b
    Examples:
      ainfera kill 8e7b4d6e-...
      ainfera kill 8e7b4d6e-... --reason "manual_test"
      ainfera kill 8e7b4d6e-... --unkill            # clear quarantine
      ainfera kill 8e7b4d6e-... --yes               # skip confirmation
    """
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
        if unkill:
            # Clear kill switch
            with console.status("  [ainfera.muted]Clearing kill switch...[/]"):
                result = client.unkill_agent(agent_id)

            if json_output:
                click.echo(json.dumps(result))
                return

            print_header()
            print_success("Kill switch cleared.")
            console.print(
                f"  Agent status: [ainfera.muted]{result.get('status', 'stopped')}[/]"
            )
            console.print()
        else:
            # Trigger kill switch
            if not json_output:
                print_header()

            # Confirmation
            if not yes and not json_output:
                console.print(
                    f"  [ainfera.warning]\u26a0  This will immediately stop agent [bold]{agent_id[:12]}...[/] and quarantine it.[/]"
                )
                console.print(f"     Reason: [ainfera.muted]{reason}[/]")
                console.print()
                if not click.confirm("     Continue?", default=False):
                    console.print("  [ainfera.muted]Cancelled.[/]")
                    return

            with console.status("  [ainfera.muted]Triggering kill switch...[/]"):
                result = client.kill_agent(agent_id, reason=reason)

            if json_output:
                click.echo(json.dumps(result))
                return

            console.print()
            console.print("  [ainfera.error bold]\u25c6 KILL SWITCH TRIGGERED[/]")
            console.print()
            console.print(f"  Agent:    [bold]{result.get('name', agent_id[:12])}[/]")
            console.print("  Status:   [ainfera.error]quarantined[/]")
            console.print(f"  Reason:   [ainfera.muted]{reason}[/]")
            console.print(
                f"  Time:     [ainfera.muted]{result.get('killed_at', 'now')}[/]"
            )
            console.print()
            console.print(
                "  The agent has been stopped. All pending requests will receive 503."
            )
            console.print(
                f"  To un-quarantine: [bold]ainfera kill --unkill {agent_id}[/]"
            )
            console.print()
    finally:
        client.close()
