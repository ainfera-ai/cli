"""ainfera skill-scan — scan an OpenClaw SKILL.md for trust before installing."""

from __future__ import annotations

import json as _json
from pathlib import Path

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url
from ainfera.ui.console import console, print_error


DIMENSIONS = ("safety", "reliability", "quality", "performance", "reputation")


@click.command("skill-scan")
@click.argument("target")
@click.option(
    "--threshold",
    type=int,
    default=0,
    help="Minimum trust score (0-1000). Exits non-zero if the score falls below.",
)
@click.option(
    "--source",
    type=click.Choice(["clawhub", "local"]),
    default=None,
    help="Force source: 'clawhub' (registry lookup) or 'local' (SKILL.md file).",
)
@click.pass_context
def skill_scan(ctx, target: str, threshold: int, source: str | None):
    """Scan an OpenClaw SKILL.md for trust before installing.

    \b
    Examples:
      ainfera skill-scan github-manager
      ainfera skill-scan ./SKILL.md --threshold 700
      ainfera skill-scan data-analyst --threshold 800 --source clawhub
    """
    json_output = ctx.obj.get("json", False)

    path = Path(target)
    is_local = source == "local" or (source is None and path.exists() and path.is_file())

    skill_name = target
    content: str | None = None
    if is_local:
        if not path.exists():
            print_error(f"File not found: {target}")
            raise SystemExit(1)
        content = path.read_text(encoding="utf-8")
        skill_name = path.stem or target

    client = AinferaClient(api_key=ensure_authenticated(), api_url=get_api_url())
    try:
        with console.status("  [ainfera.muted]Scanning skill...[/]"):
            data = client.skill_scan(skill_name, content=content)
    finally:
        client.close()

    score = int(data.get("overall_score", data.get("score", 0)) or 0)
    grade = data.get("grade") or "—"
    dimensions = _extract_dimensions(data)
    threats = data.get("threats") or []
    recommendation = data.get("recommendation")
    passed = score >= threshold

    if json_output:
        click.echo(_json.dumps(data))
        if threshold and not passed:
            raise SystemExit(1)
        return

    _print_radar(skill_name, score, grade, dimensions, threats, recommendation, passed, threshold)

    if threshold and not passed:
        raise SystemExit(1)


def _extract_dimensions(data: dict) -> dict[str, float]:
    if not isinstance(data, dict):
        return {}
    raw = data.get("dimensions") or {}
    if isinstance(raw, dict) and raw:
        return {
            k.lower(): float(v)
            for k, v in raw.items()
            if isinstance(v, (int, float))
        }
    return {
        k: float(data[f"{k}_score"])
        for k in DIMENSIONS
        if isinstance(data.get(f"{k}_score"), (int, float))
    }


def _print_radar(
    name: str,
    score: int,
    grade: str,
    dimensions: dict[str, float],
    threats: list,
    recommendation: str | None,
    passed: bool,
    threshold: int,
) -> None:
    console.print()
    console.print(f"  [bold]Skill:[/] {name}")
    console.print(f"  [bold]Trust Score:[/] [ainfera.brand]{grade} {score}[/]")
    console.print()
    width = 20
    last = len([d for d in DIMENSIONS if d in dimensions]) - 1
    for idx, dim in enumerate(d for d in DIMENSIONS if d in dimensions):
        value = dimensions[dim]
        filled = int(value * width)
        empty = width - filled
        bar = f"[ainfera.brand]{'█' * filled}[/]{'░' * empty}"
        label = dim.capitalize().ljust(12)
        branch = "└─" if idx == last else "├─"
        console.print(f"  {branch}{label} {value:.2f}  {bar}")
    console.print()

    n = len(threats)
    if n == 0:
        console.print("  [ainfera.success]Threats: 0 found[/]")
    else:
        console.print(f"  [ainfera.error]Threats: {n} found[/]")
        for t in threats[:5]:
            if isinstance(t, dict):
                label = t.get("title") or t.get("type") or "issue"
                severity = t.get("severity", "")
                console.print(f"    [ainfera.error]•[/] {label} [ainfera.muted]{severity}[/]")
            else:
                console.print(f"    [ainfera.error]•[/] {t}")

    if recommendation:
        tag = (
            "[ainfera.success]✓[/]" if passed or threshold == 0
            else "[ainfera.error]✗[/]"
        )
        console.print(f"  Recommendation: {tag} {recommendation}")
    else:
        if threshold:
            if passed:
                console.print(
                    f"  Recommendation: [ainfera.success]✓ Safe to install[/] "
                    f"[ainfera.muted]score {score} ≥ threshold {threshold}[/]"
                )
            else:
                console.print(
                    f"  Recommendation: [ainfera.error]✗ Blocked[/] "
                    f"[ainfera.muted]score {score} < threshold {threshold}[/]"
                )
        else:
            console.print("  Recommendation: [ainfera.success]✓ Safe to install[/]")
    console.print()
