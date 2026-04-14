# Changelog

## 0.4.0 (2026-04-14)

### Added
- `ainfera deploy --demo` — mock-data stage showcase: Panel header, five 400ms progress steps, success banner, and trust dimension table. No API calls.
- Top-level `ainfera login` (alongside `ainfera auth login`) for a flatter entry point.
- `ainfera trust` is now a single flat command accepting `--history`, `--anomalies`, and `--days`. Subcommand form (`trust score|history|anomalies`) removed.
- `actions/` — three composite GitHub Actions bundled in this repo: `deploy-agent`, `trust-check`, `sandbox-test`.
- `src/ainfera/sdk/` — typed synchronous SDK (`AinferaSDK`) for programmatic access. Ships in the same `ainfera` package.
- `python -m ainfera` now works (added `__main__.py`).

### Changed
- `ainfera deploy` JSON output now includes `agent_id`, `name`, `framework`, `trust_score`, and `trust_grade` at the top level for easier scripting (the full `agent` object is still nested).
- `ainfera init` auto-detects framework from `requirements.txt` / `package.json` when run non-interactively (e.g. CI, `--json`, piped stdin) and now emits JSON under a nested `config` key.
- `generate_yaml()` / `parse_yaml()` now wrap config under `agent:` to match the schema `ainfera deploy` expects end-to-end.

### Fixed
- `ainfera deploy` tests pass — previous mismatch between generated YAML (flat) and the deploy parser (expected `agent:` wrapper) is resolved.
- Unicode escape sequences removed from f-string expressions so the package imports cleanly on Python 3.10 and 3.11.

## 0.3.0 (2026-04-14)

### Added
- `ainfera status` now surfaces agent counts (total / published / draft) and average trust score when authenticated — derived from `GET /v1/agents` instead of relying on `/health` stats
- `ainfera init --non-interactive` for scripts and CI (skips prompts, uses sensible defaults; pairs well with `--force`)
- `scripts/demo.sh` — end-to-end investor-pitch demo (status → list → create → init → deploy → trust → list) driven entirely by the CLI

### Changed
- `ainfera status` auth indicator is now verified against an authenticated endpoint, so invalid keys correctly show as unauthenticated
- Error messages: `404` now echoes the missing id ("Agent not found: {id}"), `422` surfaces the API's validation `detail`, and JSON/`message` response bodies are handled uniformly

## 0.2.1 (2026-04-13)

### Fixed
- `ainfera health` now reads `services.db` / `services.redis` from the live response shape
- `ainfera trust score` / `history` / `anomalies` now parse the live API field names (`overall_score`, `reliability_score`, `is_public`, `anomaly_type`, …)
- `AinferaClient.create_agent_from_config` now sends `{"config": ...}` (was `config_yaml`, which the API rejects)
- `AinferaClient.create_agent` / `update_agent` no longer send `compute_tier` (not in the API schema); compute tier is now embedded in `config_yaml`
- `ainfera kill` no longer sends an unaccepted `reason` body to the API
- "Not authenticated" error now points to `ainfera auth login` (the actual command), not the missing top-level `ainfera login`

### Added
- `ainfera status` — full platform overview (API/DB/Redis/CLI/auth/config) in one panel
- Global `--api-url` flag to override the configured API URL per-command
- Network-error messaging for connection refused / timeout / SSL failures
- Examples in `--help` for every command (`ainfera <cmd> --help`)
- `--framework` and `--tier` on `ainfera agents create` are now `Choice`-validated

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
