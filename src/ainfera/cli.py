"""Ainfera CLI — main entry point."""

from __future__ import annotations

import click

from ainfera import __version__
from ainfera.commands.deploy import deploy
from ainfera.commands.init import init
from ainfera.commands.kill import kill
from ainfera.commands.login import login
from ainfera.commands.logs import logs
from ainfera.commands.status import status
from ainfera.commands.trust import trust


@click.group()
@click.version_option(version=__version__, prog_name="ainfera")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging")
@click.pass_context
def main(ctx, json_output: bool, verbose: bool):
    """Ainfera \u2014 Deploy AI agents with trust scores, kill switches, and billing."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["verbose"] = verbose


main.add_command(login)
main.add_command(init)
main.add_command(deploy)
main.add_command(status)
main.add_command(trust)
main.add_command(kill)
main.add_command(logs)


if __name__ == "__main__":
    main()
