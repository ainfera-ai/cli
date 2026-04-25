# CLAUDE.md — Ainfera CLI

## Project

Ainfera is infrastructure for the AI agent economy. This repo is the
official CLI — the primary interface developers use to deploy agents,
check trust scores, and manage their agents from the terminal.

The CLI is a thin client: it calls the Ainfera API for everything and
renders the result with Rich.

## Design philosophy

- Thin client — all logic lives in the API
- Beautiful terminal output via Rich (tables, spinners, panels)
- `--json` on every command for scripting and CI/CD
- `--verbose` / `-v` for debug logging
- Helpful error messages that tell the reader exactly what to do next

## Tech stack

- Python 3.10+
- Click (CLI framework)
- Rich (terminal formatting)
- httpx (HTTP client)
- PyYAML (`ainfera.yaml` parsing)
- pydantic >= 2.0 (config validation)
- keyring (optional secure credential storage)

## Commands

1. `ainfera login`        — authenticate with API key
2. `ainfera init`         — detect framework, generate `ainfera.yaml`
3. `ainfera deploy`       — deploy agent to Ainfera
4. `ainfera status`       — agent status + trust score
5. `ainfera trust`        — detailed trust score breakdown
6. `ainfera kill`         — trigger kill switch
7. `ainfera logs`         — stream execution logs
8. `ainfera agents`       — list/get/create/delete agents
9. `ainfera billing`      — usage and cost breakdown
10. `ainfera trust-check` — CI/CD gate (exits non-zero below threshold)
11. `ainfera skill-scan`  — scan a skill definition for trust
12. `ainfera register`    — register agent in marketplace
13. `ainfera discover`    — search marketplace for trusted agents
14. `ainfera gate`        — auto-block untrusted skill installs
15. `ainfera health`      — unauthenticated API health check

## Project structure

```
ainfera-cli/
├── src/ainfera/
│   ├── __init__.py
│   ├── cli.py              # Click group + top-level commands
│   ├── commands/           # one module per command
│   ├── api/client.py       # httpx client for the Ainfera API
│   ├── config/settings.py  # ~/.ainfera/config.yaml loader
│   ├── ui/                 # Rich console, formatters, theme
│   └── utils/              # detection, error handling
├── actions/                # composite GitHub Actions wrappers
├── tests/
├── .github/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── docs/BRAND-WORDS.md
└── LICENSE
```

## API endpoints the CLI calls

- `POST /v1/agents` — create agent
- `POST /v1/agents/{id}/deploy` — deploy agent
- `GET  /v1/agents/{id}` — agent status
- `GET  /v1/trust/{id}` — trust score
- `GET  /v1/trust/{id}/history` — trust score history
- `GET  /v1/trust/{id}/anomalies` — anomaly list
- `POST /v1/agents/{id}/kill` — trigger kill switch
- `DELETE /v1/agents/{id}/kill` — clear kill switch
- `WS   /v1/stream/{execution_id}` — live execution logs
- `POST /v1/skills/scan` — scan a skill for trust
- `POST /v1/agents/register` — register agent in marketplace
- `GET  /v1/agents/discover` — search marketplace

## Conventions

- All API calls go through `src/ainfera/api/client.py`
- All terminal output goes through `src/ainfera/ui/console.py`
- Errors raise `click.ClickException` with Rich-formatted messages
- Config stored at `~/.ainfera/config.yaml`
- `AINFERA_*` env prefix for all overrides

## Revenue split

`85 / 5 / 10` — creator / platform / compute. Surface this split in
`ainfera billing` output and in the README revenue section.

## URLs

- `https://ainfera.ai` — marketing
- `https://app.ainfera.ai` — logged-in product
- `https://api.ainfera.ai` — API (default `AINFERA_API_URL`)

## Trust grade boundaries

`AAA ≥ 900 · AA ≥ 800 · A ≥ 700 · BBB ≥ 600 · BB ≥ 500 · B ≥ 400`.
`CCC < 400` auto-quarantines.

## ATS dimensions

`Safety · Reliability · Quality · Performance · Reputation` — five
dimensions. The `skill-scan` and `trust` command renderings use this
exact set.

## Agent DID format

`did:web:ainfera.ai:agents:{id}` — the canonical `did:web` form.
Never `did:ainfera:agent:{id}`.

## `ainfera.yaml` canonical schema

One form across README, `ainfera init` scaffold, and the yaml parser:

- `agent.trust` uses `min_score` + `auto_kill_below`
- `agent.compute` uses `tier` + `timeout` (seconds)
- Legacy keys (`anomaly_detection`, `quarantine_threshold`, `sandbox`,
  `memory`, `cpu`) are accepted by the parser for compatibility

## Brand enforcement

- `docs/BRAND-WORDS.md` — copy rules (entity, ATS canon, DID format,
  revenue split, retired phrasing, grep battery)
- `docs/DESIGN-SYSTEM.md` — visual spec (terminal output style,
  §6 hue rule for status semantics)

Run the `BRAND-WORDS.md` §3 grep battery before every push that
touches a user-facing file (`README.md`, `CLAUDE.md`, `docs/**`,
`src/**`, `tests/**`, `*.py`, `*.toml`, `*.cfg`, `*.md`).

The `.claude/commands/brand-check.md` slash command runs the full
battery and reports each hit with file/line/suggested replacement.

## Git author identity

Per `docs/BRAND-WORDS.md` §6:

```bash
git config user.name  "Hizrian Raz"
git config user.email "hizrian@ainfera.ai"
```

Note: `pyproject.toml`'s `authors` and `maintainers` fields stay as
`Ainfera <hello@ainfera.ai>`. That field is **public PyPI metadata**,
not git config. The git author exception at §6 does NOT extend to
PyPI metadata.

## Framework language

When describing what agent frameworks the CLI works with, use generic
phrasing ("works with major agent frameworks"). Framework values that
appear as CLI flag values (`--framework <value>`) are functional and
may remain as flag values with generic help-text.
