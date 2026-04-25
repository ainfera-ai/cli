"""ainfera trust-check — gate command for CI/CD. Fetches trust score and exits non-zero if below threshold."""

from __future__ import annotations

import json

import click

from ainfera.api.client import AinferaClient
from ainfera.config.settings import ensure_authenticated, get_api_url, get_default_agent
from ainfera.ui.console import console, print_error


DIMENSIONS = ("safety", "reliability", "quality", "performance", "reputation")


@click.command("trust-check")
@click.option(
    "--agent-id",
    "agent_id",
    default=None,
    help="Agent ID to evaluate (defaults to the configured default agent).",
)
@click.option(
    "--threshold",
    type=int,
    default=0,
    help="Minimum trust score (0-1000). Exits non-zero if the score falls below.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format. 'json' emits a machine-readable payload suitable for CI.",
)
@click.pass_context
def trust_check(ctx, agent_id: str | None, threshold: int, fmt: str):
    """Evaluate an agent's trust score as a CI/CD gate.

    \b
    Examples:
      ainfera trust-check --agent-id abc123
      ainfera trust-check --agent-id abc123 --threshold 800
      ainfera trust-check --agent-id abc123 --format json
    """
    resolved = agent_id or get_default_agent()
    if not resolved:
        print_error(
            "No agent specified.",
            "Pass --agent-id or deploy an agent first.",
        )
        raise SystemExit(1)

    client = AinferaClient(api_key=ensure_authenticated(), api_url=get_api_url())
    try:
        data = client.get_trust_score(resolved)
    finally:
        client.close()

    score = int(data.get("overall_score", data.get("score", 0)) or 0)
    grade = data.get("grade") or "—"
    dimensions = _extract_dimensions(data)
    passed = score >= threshold

    if fmt == "json":
        payload = {
            "agent_id": resolved,
            "score": score,
            "grade": grade,
            "dimensions": dimensions,
            "threshold": threshold,
            "pass": passed,
            "comment_markdown": _build_pr_comment(
                score, grade, dimensions, threshold, passed
            ),
        }
        click.echo(json.dumps(payload))
        if not passed:
            raise SystemExit(1)
        return

    _print_trust_radar(score, grade, dimensions)

    if threshold > 0:
        if passed:
            console.print(
                f"  [ainfera.success]\u2713 PASS[/] "
                f"[ainfera.muted]score {score} \u2265 threshold {threshold}[/]"
            )
        else:
            console.print(
                f"  [ainfera.error]\u2717 FAIL[/] "
                f"[ainfera.muted]score {score} < threshold {threshold}[/]"
            )
        console.print()

    if not passed:
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
    flat = {
        k: float(data[f"{k}_score"])
        for k in DIMENSIONS
        if isinstance(data.get(f"{k}_score"), (int, float))
    }
    return flat


def _print_trust_radar(score: int, grade: str, dimensions: dict[str, float]) -> None:
    console.print()
    console.print(
        f"  [bold]Trust Score:[/] [ainfera.brand]{grade} {score}[/]"
    )
    console.print()
    width = 20
    for dim in DIMENSIONS:
        if dim not in dimensions:
            continue
        value = dimensions[dim]
        filled = int(value * width)
        empty = width - filled
        bar = f"[ainfera.brand]{'█' * filled}[/]{'░' * empty}"
        label = dim.capitalize().ljust(12)
        console.print(f"  {label} {value:.2f}  {bar}")
    console.print()
    console.print(
        "  [ainfera.muted]Grade: geometric mean across dimensions[/]"
    )
    console.print()


def _build_pr_comment(
    score: int, grade: str, dimensions: dict[str, float], threshold: int, passed: bool
) -> str:
    """Build a markdown PR comment body for GitHub Actions to post."""
    status = "PASS" if passed else "FAIL"
    lines = [
        "## Ainfera Trust Check",
        "",
        f"**Score:** {grade} {score}  ",
        f"**Threshold:** {threshold}  ",
        f"**Status:** {status}",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
    ]
    for dim in DIMENSIONS:
        if dim not in dimensions:
            continue
        lines.append(f"| {dim.capitalize()} | {dimensions[dim]:.2f} |")
    lines.append("")
    return "\n".join(lines)
