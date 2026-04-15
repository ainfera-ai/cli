"""Ainfera CLI — main entry point."""

from __future__ import annotations

import click

from ainfera import __version__
from ainfera.commands.agents import agents
from ainfera.commands.auth import auth
from ainfera.commands.billing import billing
from ainfera.commands.deploy import deploy
from ainfera.commands.health import health
from ainfera.commands.init import init
from ainfera.commands.kill import kill
from ainfera.commands.login import login
from ainfera.commands.logs import logs
from ainfera.commands.status import status
from ainfera.commands.trust import trust
from ainfera.commands.trust_check import trust_check


@click.group()
@click.version_option(version=__version__, prog_name="ainfera")
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON instead of formatted tables")
@click.option("--api-url", default=None, help="Override the configured API URL for this command")
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
@click.pass_context
def main(ctx, json_output: bool, api_url: str | None, verbose: bool):
    """Ainfera \u2014 Deploy AI agents with trust scores, kill switches, and billing.

    \b
    Common workflows:
      ainfera auth login                    Authenticate with your API key
      ainfera init                          Scaffold ainfera.yaml in this folder
      ainfera deploy                        Deploy your agent to the platform
      ainfera status                        Show platform + auth overview
      ainfera agents list                   List your agents
      ainfera trust score <agent-id>        Check an agent's trust score
    """
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["verbose"] = verbose
    if api_url:
        import os
        os.environ["AINFERA_API_URL"] = api_url


main.add_command(auth)
main.add_command(agents)
main.add_command(trust)
main.add_command(trust_check)
main.add_command(health)
main.add_command(init)
main.add_command(deploy)
main.add_command(status)
main.add_command(kill)
main.add_command(logs)
main.add_command(billing)
main.add_command(login)


if __name__ == "__main__":
    main()
