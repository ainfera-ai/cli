# CLAUDE.md — Ainfera CLI

## Project
Ainfera is the unified infrastructure platform for the AI agent economy.
This repo is the official CLI — the primary interface developers use to deploy agents,
check trust scores, and manage their agents from the terminal.

The CLI is the star of every demo. When the founder types `ainfera deploy` on stage
and a trust score appears 5 seconds later, that's this repo.

Company: Ainfera Pte. Ltd., Singapore. Pre-funding stage.

## Design Philosophy
- The CLI is a thin client — it calls the platform-api for everything
- Beautiful terminal output using Rich (colors, tables, spinners, progress bars)
- Ainfera brand colors in terminal: gold/amber for accents, green for success, red for errors
- Every command should feel like a premium developer tool (think Vercel CLI, Railway CLI)
- JSON output mode (--json) for scripting and CI/CD pipelines
- Helpful error messages that tell you exactly what to do next

## Tech Stack
- Python 3.10+ (wide compatibility)
- Click (CLI framework — more mature than Typer for our needs)
- Rich (terminal formatting, tables, spinners, panels)
- httpx (async HTTP client for API calls)
- PyYAML (ainfera.yaml parsing)
- pydantic >= 2.0 (config validation)
- keyring (secure credential storage, optional)

## Commands (v0.1 — 1-week blitz)
1. ainfera login          — authenticate with API key
2. ainfera init           — detect framework, generate ainfera.yaml
3. ainfera deploy         — deploy agent to Ainfera platform
4. ainfera status         — show agent status + trust score
5. ainfera trust          — detailed trust score breakdown
6. ainfera kill           — trigger kill switch immediately
7. ainfera logs           — stream execution logs

## Project Structure
```
ainfera-cli/
├── src/
│   └── ainfera/
│       ├── __init__.py         # Package version
│       ├── cli.py              # Click group + top-level commands
│       ├── commands/
│       │   ├── __init__.py
│       │   ├── login.py        # ainfera login
│       │   ├── init.py         # ainfera init
│       │   ├── deploy.py       # ainfera deploy
│       │   ├── status.py       # ainfera status
│       │   ├── trust.py        # ainfera trust
│       │   ├── kill.py         # ainfera kill
│       │   └── logs.py         # ainfera logs
│       ├── api/
│       │   ├── __init__.py
│       │   └── client.py       # httpx client for platform-api
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py     # CLI config (~/.ainfera/config.yaml)
│       │   └── yaml_parser.py  # ainfera.yaml parser
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── console.py      # Rich console singleton
│       │   ├── formatters.py   # Trust score, agent status formatters
│       │   └── themes.py       # Ainfera color theme for Rich
│       └── utils/
│           ├── __init__.py
│           ├── detect.py       # Framework detection
│           └── errors.py       # Error handling + friendly messages
├── tests/
│   ├── test_init.py
│   ├── test_deploy.py
│   ├── test_trust.py
│   └── conftest.py
├── pyproject.toml
├── CLAUDE.md
├── README.md
└── LICENSE
```

## API Endpoint Reference
The CLI calls these platform-api endpoints:
- POST /v1/agents                    — create agent
- POST /v1/agents/{id}/deploy       — deploy agent
- GET  /v1/agents/{id}              — get agent status
- GET  /v1/trust/{id}               — get trust score
- GET  /v1/trust/{id}/history       — trust score history
- GET  /v1/trust/{id}/anomalies     — anomaly list
- POST /v1/agents/{id}/kill         — trigger kill switch
- DELETE /v1/agents/{id}/kill       — clear kill switch
- WS   /v1/stream/{execution_id}    — live execution logs
- GET  /v1/github/repos/{o}/{r}/detect — framework detection

## Conventions
- All API calls go through src/ainfera/api/client.py
- All terminal output goes through src/ainfera/ui/console.py
- Errors use click.ClickException with Rich-formatted messages
- Config stored in ~/.ainfera/config.yaml (API key, default project, API URL)
- --json flag on every command for machine-readable output
- --verbose / -v flag for debug logging
