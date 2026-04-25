"""ainfera gate — configure auto-trust-gating for skill installs."""

from __future__ import annotations

import json as _json

import click

from ainfera.config.settings import CONFIG_DIR, load_config, save_config
from ainfera.ui.console import console, print_success, print_warning


GATE_HOOK_PATH = CONFIG_DIR / "gate-hook.sh"

HOOK_TEMPLATE = """#!/usr/bin/env bash
# Ainfera trust gate — auto-generated. Do not edit by hand.
# Runs `ainfera skill-scan` before `openclaw skills install <name>`.
# Blocks installs below the configured trust threshold.

set -e
THRESHOLD={threshold}

openclaw() {{
    if [ "$1" = "skills" ] && [ "$2" = "install" ] && [ -n "$3" ]; then
        ainfera skill-scan "$3" --threshold "$THRESHOLD" || {{
            echo "✗ Ainfera trust gate blocked install of '$3' (below $THRESHOLD)." >&2
            return 1
        }}
    fi
    command openclaw "$@"
}}
"""


def _gate_config() -> dict:
    return load_config().get("gate", {}) or {}


def _save_gate(gate: dict) -> None:
    cfg = load_config()
    cfg["gate"] = gate
    save_config(cfg)


@click.command()
@click.option("--threshold", type=int, default=700, help="Minimum trust score to allow install (0-1000).")
@click.option("--enable", "action", flag_value="enable", help="Enable the trust gate.")
@click.option("--disable", "action", flag_value="disable", help="Disable the trust gate.")
@click.option("--status", "action", flag_value="status", default=True, help="Show current gate status.")
@click.pass_context
def gate(ctx, threshold: int, action: str):
    """Configure auto-trust-gating for skill installs.

    \b
    Examples:
      ainfera gate --status
      ainfera gate --enable --threshold 700
      ainfera gate --disable
    """
    json_output = ctx.obj.get("json", False)

    if action == "enable":
        GATE_HOOK_PATH.parent.mkdir(mode=0o700, exist_ok=True)
        GATE_HOOK_PATH.write_text(HOOK_TEMPLATE.format(threshold=threshold))
        GATE_HOOK_PATH.chmod(0o700)
        _save_gate({"enabled": True, "threshold": threshold, "hook": str(GATE_HOOK_PATH)})
        if json_output:
            click.echo(_json.dumps({"enabled": True, "threshold": threshold, "hook": str(GATE_HOOK_PATH)}))
            return
        console.print()
        print_success(f"Trust gate enabled (threshold: [ainfera.brand]{threshold}[/])")
        _letter = _grade_for(threshold)
        console.print(
            f"  Skills below [ainfera.brand]{_letter} ({threshold})[/] will be blocked before install."
        )
        console.print(
            f"  [ainfera.muted]Source this hook in your shell:[/] "
            f"[bold]source {GATE_HOOK_PATH}[/]"
        )
        console.print()
        return

    if action == "disable":
        if GATE_HOOK_PATH.exists():
            GATE_HOOK_PATH.unlink()
        _save_gate({"enabled": False})
        if json_output:
            click.echo(_json.dumps({"enabled": False}))
            return
        console.print()
        print_warning("Trust gate disabled. Skill installs are no longer checked.")
        console.print()
        return

    gate_cfg = _gate_config()
    if json_output:
        click.echo(_json.dumps(gate_cfg or {"enabled": False}))
        return
    console.print()
    if gate_cfg.get("enabled"):
        t = gate_cfg.get("threshold", 700)
        print_success(f"Trust gate enabled (threshold: [ainfera.brand]{t}[/])")
        console.print(f"  Hook: [ainfera.muted]{gate_cfg.get('hook', GATE_HOOK_PATH)}[/]")
    else:
        print_warning("Trust gate disabled.")
        console.print(
            "  [ainfera.muted]Run[/] [bold]ainfera gate --enable[/] "
            "[ainfera.muted]to block untrusted skills.[/]"
        )
    console.print()


def _grade_for(threshold: int) -> str:
    if threshold >= 900:
        return "AAA"
    if threshold >= 800:
        return "AA"
    if threshold >= 700:
        return "BBB"
    if threshold >= 600:
        return "BB"
    if threshold >= 500:
        return "B"
    return "C"
