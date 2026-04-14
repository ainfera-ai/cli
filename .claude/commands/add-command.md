Create a new CLI command. $ARGUMENTS describes it (e.g. "ainfera agents list — table of all agents with trust scores").

Create ALL of:
1. src/ainfera/commands/{name}.py — Click command with --help, Rich console output
2. API client method in src/ainfera/api/client.py — async httpx with error handling
3. Pydantic model in src/ainfera/api/models.py if new response shape
4. Rich formatter in src/ainfera/output/formatters.py if new display format
5. Register in src/ainfera/cli.py Click group
6. Test in tests/test_commands/test_{name}.py using CliRunner

Output conventions: success=sage panel, error=vermillion panel, data=Rich table with Ainfera theme, progress=Azure spinner, trust=grade+score+colored bar, costs=4 decimal USD, timestamps=relative (<24h) or absolute, agent IDs=short form.
