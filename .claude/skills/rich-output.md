---
name: rich-output
description: Format CLI output using Rich library. Use when displaying data in the terminal — tables, panels, progress bars, trees.
---

# Rich Output Patterns

## Tables (for lists)
```python
from rich.table import Table
from rich.console import Console

console = Console()
table = Table(title="Your Agents", border_style="dim")
table.add_column("Name", style="white")
table.add_column("Framework", style="cyan")
table.add_column("Trust", justify="center")
table.add_column("Status", style="green")

for agent in agents:
    grade_color = {"AAA": "green", "AA": "green", "A": "green",
                   "BBB": "yellow", "BB": "yellow", "B": "yellow",
                   "CCC": "red"}.get(agent.grade, "white")
    table.add_row(
        agent.name,
        agent.framework,
        f"[{grade_color}]{agent.grade} ({agent.score})[/{grade_color}]",
        agent.status
    )
console.print(table)
```

## Panels (for details)
```python
from rich.panel import Panel
console.print(Panel(content, title="Agent Details", border_style="yellow"))
```

## Progress (for long operations)
```python
from rich.progress import Progress
with Progress() as progress:
    task = progress.add_task("Deploying...", total=100)
    # ... work ...
    progress.update(task, advance=50)
```

## Status indicators
```python
console.print("[green]✓[/green] Agent created successfully")
console.print("[red]✗[/red] Deployment failed")
console.print("[yellow]![/yellow] Warning: trust score below threshold")
```
