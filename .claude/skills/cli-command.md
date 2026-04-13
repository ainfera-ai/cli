---
name: cli-command
description: Create CLI commands following Ainfera CLI patterns. Auto-invoked when adding new commands, subcommands, or CLI features.
---

# CLI Command Patterns

## Stack
- **Click** for command definitions (decorators, groups, arguments, options)
- **Rich** for terminal output (tables, panels, progress bars, syntax highlighting)
- **httpx** for async API calls (via `src/ainfera/client.py`)

## Command Structure
```python
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def agents():
    """Manage AI agents on the Ainfera platform."""
    pass

@agents.command()
@click.argument('agent_id')
def get(agent_id: str):
    """Get details for a specific agent."""
    from ainfera.client import get_client
    client = get_client()
    
    try:
        agent = client.get_agent(agent_id)
        # Display with Rich panel
        console.print(Panel(
            f"Name: {agent['name']}\n"
            f"Framework: {agent['framework']}\n"
            f"Status: {agent['status']}",
            title=f"Agent {agent_id}",
            border_style="yellow"
        ))
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
```

## Patterns
1. All commands use Click decorators
2. Output uses Rich — tables for lists, panels for details, progress for long ops
3. API calls go through `src/ainfera/client.py` — never inline HTTP calls
4. Error handling: catch API errors, print friendly messages, exit with code 1
5. Auth errors (401): prompt "Run 'ainfera auth login' to authenticate"
6. Colors: yellow/amber for Ainfera brand, green for success, red for errors
7. Always show the command used in --help with examples

## File Organization
- `src/ainfera/cli.py` — Main CLI entry point, registers all groups
- `src/ainfera/commands/agents.py` — Agent commands
- `src/ainfera/commands/trust.py` — Trust score commands
- `src/ainfera/commands/auth.py` — Authentication commands
- `src/ainfera/client.py` — HTTP client for API calls
- `src/ainfera/config.py` — Config loading (~/.ainfera/config.yaml)
