# Changelog

## 0.2.0 (2026-04-13)

### Added
- `ainfera auth login` / `ainfera auth status` — authenticate with an API key and inspect the current session
- `ainfera agents list` / `get` / `create` / `delete` — manage agents from the CLI
- `ainfera trust score` (also `history`, `anomalies`) — view trust scores and breakdown in the terminal
- `ainfera health` — unauthenticated health check against `api.ainfera.ai`
- `ainfera init` — interactive scaffolding of `ainfera.yaml` (name, framework, description, compute tier)
- `ainfera deploy` — reads `ainfera.yaml` and creates or updates the agent via the platform API (supports `--dry-run` and `--from-config`)

### Changed
- CLI now talks to the live API at `https://api.ainfera.ai` by default
- Top-level `login` has moved to `auth login`; `trust` is now a command group

## 0.1.0 (2026-04-20)

Initial release.

### Features
- `ainfera login` — authenticate with API key
- `ainfera init` — detect framework, generate ainfera.yaml
- `ainfera deploy` — deploy agent with trust scoring
- `ainfera status` — view agent status
- `ainfera trust` — trust score breakdown
- `ainfera kill` — kill switch control
- `ainfera logs` — execution log streaming
- `--json` flag on all commands
- Rich terminal output with Ainfera brand colors
