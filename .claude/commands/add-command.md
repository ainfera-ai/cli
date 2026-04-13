---
description: Add a new CLI command
---

I need a new CLI command. Ask me:
1. Command group? (e.g., agents, trust, billing, auth, or top-level)
2. Command name? (e.g., list, get, create, status)
3. What does it do?
4. What arguments/options does it need?
5. Which API endpoint does it call?

Then:
- Add the command to the appropriate file in src/ainfera/
- Use Click decorators (@click.command, @click.argument, @click.option)
- Use Rich for output formatting (tables, panels, progress bars)
- Add error handling (401 → auth prompt, 404 → not found, 500 → API error)
- Register the command in the CLI group in src/ainfera/cli.py
- Add a test in tests/

Follow the existing command patterns. All API calls go through src/ainfera/client.py.
Output uses Rich for tables/panels. Errors use click.echo with Rich markup.
