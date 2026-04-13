"""Rich formatting helpers for trust scores, agent status, and tables."""

from rich.panel import Panel
from rich.table import Table

from .themes import grade_style


def format_trust_score(score: int, grade: str) -> str:
    """Format trust score with color-coded grade."""
    style = grade_style(grade)
    return f"[{style}]{score} / 1000  ({grade})[/{style}]"


def format_agent_status(status: str) -> str:
    """Format agent status with color."""
    colors = {
        "running": "ainfera.success",
        "stopped": "ainfera.muted",
        "deploying": "ainfera.info",
        "quarantined": "ainfera.error",
        "failed": "ainfera.error",
        "draft": "ainfera.muted",
    }
    style = colors.get(status, "ainfera.muted")
    return f"[{style}]{status}[/{style}]"


def format_kill_switch_status(status: str) -> str:
    """Format kill switch status."""
    colors = {
        "armed": "ainfera.success",
        "triggered": "ainfera.error",
        "disarmed": "ainfera.muted",
    }
    style = colors.get(status, "ainfera.muted")
    return f"[{style}]{status}[/{style}]"


def format_agent_table(agents: list[dict]) -> Table:
    """Format agent list as a Rich table."""
    table = Table(title="Your Agents", border_style="ainfera.muted")
    table.add_column("Name", style="bold")
    table.add_column("Framework", style="ainfera.muted")
    table.add_column("Trust", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Agent ID", style="ainfera.muted")
    for agent in agents:
        trust = (
            format_trust_score(
                agent.get("current_trust_score", 0),
                agent.get("trust_grade", "\u2014"),
            )
            if agent.get("current_trust_score")
            else "[ainfera.muted]pending[/]"
        )
        table.add_row(
            agent["name"],
            agent["framework"],
            trust,
            format_agent_status(agent["status"]),
            agent["id"][:8] + "\u2026",
        )
    return table


def format_agent_panel(agent: dict) -> Panel:
    """Format a single agent as a Rich panel."""
    from rich.text import Text

    lines = []
    lines.append(f"  Status         {format_agent_status(agent.get('status', 'unknown'))}")
    lines.append(f"  Framework      [ainfera.muted]{agent.get('framework', 'unknown')}[/]")
    lines.append(f"  Agent ID       [ainfera.muted]{agent.get('id', 'unknown')}[/]")
    lines.append("")

    if agent.get("current_trust_score"):
        lines.append(
            f"  Trust Score    {format_trust_score(agent['current_trust_score'], agent.get('trust_grade', '—'))}"
        )
    else:
        lines.append("  Trust Score    [ainfera.muted]pending[/]")

    ks = agent.get("kill_switch_status", "armed")
    lines.append(f"  Kill Switch    {format_kill_switch_status(ks)}")
    lines.append("")

    if agent.get("repo_url"):
        lines.append(f"  Repo           [ainfera.muted]{agent['repo_url']}[/]")
    if agent.get("branch"):
        lines.append(f"  Branch         [ainfera.muted]{agent['branch']}[/]")
    if agent.get("last_deployed_at"):
        lines.append(f"  Last Deploy    [ainfera.muted]{agent['last_deployed_at']}[/]")

    content = "\n".join(lines)
    name = agent.get("name", "agent")
    return Panel(
        content,
        title=f"[bold]{name}[/bold]",
        border_style="ainfera.muted",
        padding=(1, 2),
    )


def render_dimension_bar(value: float, width: int = 18) -> str:
    """Render a trust dimension as a colored bar."""
    filled = int(value * width)
    empty = width - filled
    if value > 0.8:
        color = "ainfera.success"
    elif value > 0.6:
        color = "ainfera.warning"
    else:
        color = "ainfera.error"
    return f"[{color}]{'\u2588' * filled}[/{color}]{'\u2591' * empty}  {value:.2f}"


def format_trust_panel(trust_data: dict) -> Panel:
    """Format trust score breakdown as a Rich panel."""
    score = trust_data.get("score", 0)
    grade = trust_data.get("grade", "\u2014")
    dimensions = trust_data.get("dimensions", {})

    lines = []
    lines.append(f"  Overall    {format_trust_score(score, grade)}")
    lines.append("")

    for dim_name, dim_value in dimensions.items():
        label = dim_name.capitalize().ljust(14)
        bar = render_dimension_bar(dim_value)
        lines.append(f"  {label} {bar}")

    lines.append("")
    lines.append(f"  Assessments   [ainfera.muted]{trust_data.get('assessment_count', 0)}[/]")
    lines.append(f"  Public        [ainfera.muted]{'yes' if trust_data.get('public', True) else 'no'}[/]")
    if trust_data.get("computed_at"):
        lines.append(f"  Last computed  [ainfera.muted]{trust_data['computed_at']}[/]")
    lines.append("")
    lines.append(f"  Anomalies     [ainfera.muted]{trust_data.get('anomaly_count', 0)} active[/]")

    ks = trust_data.get("kill_switch_status", "armed")
    threshold = trust_data.get("quarantine_threshold", 400)
    lines.append(f"  Kill switch   {format_kill_switch_status(ks)} (threshold: {threshold})")

    content = "\n".join(lines)
    return Panel(
        content,
        title="[bold]Trust Score[/bold]",
        border_style="ainfera.muted",
        padding=(1, 2),
    )


def format_trust_history_table(history: list[dict]) -> Table:
    """Format trust score history as a Rich table."""
    table = Table(title="Trust Score History", border_style="ainfera.muted")
    table.add_column("Date", style="ainfera.muted")
    table.add_column("Score", justify="center")
    table.add_column("Grade", justify="center")
    table.add_column("Change", justify="center")
    for entry in history:
        change_val = entry.get("change", 0)
        if change_val > 0:
            change = f"[ainfera.success]\u2191 +{change_val}[/]"
        elif change_val < 0:
            change = f"[ainfera.error]\u2193 {change_val}[/]"
        else:
            change = "[ainfera.muted]\u2192 0[/]"
        table.add_row(
            entry.get("date", ""),
            str(entry.get("score", 0)),
            entry.get("grade", "\u2014"),
            change,
        )
    return table


def format_anomalies_table(anomalies: list[dict]) -> Table:
    """Format anomalies as a Rich table."""
    table = Table(title="Detected Anomalies", border_style="ainfera.muted")
    table.add_column("Type", style="bold")
    table.add_column("Severity", justify="center")
    table.add_column("Description")
    table.add_column("Detected", style="ainfera.muted")

    severity_styles = {
        "critical": "ainfera.error",
        "high": "ainfera.highlight",
        "medium": "ainfera.warning",
        "low": "ainfera.muted",
    }
    for anomaly in anomalies:
        sev = anomaly.get("severity", "low")
        style = severity_styles.get(sev, "ainfera.muted")
        table.add_row(
            anomaly.get("type", ""),
            f"[{style}]{sev}[/{style}]",
            anomaly.get("description", ""),
            anomaly.get("detected_at", ""),
        )
    return table
