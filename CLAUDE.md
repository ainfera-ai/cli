# CLAUDE.md — Ainfera CLI

## Project
Ainfera is the unified infrastructure platform for the AI agent economy.
This repo is the official CLI — the primary interface developers use to deploy agents,
check trust scores, and manage their agents from the terminal.

The CLI is the star of every demo. When the founder types `ainfera deploy` on stage
and a trust score appears 5 seconds later, that's this repo.

Company: Ainfera. Pre-funding stage.

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

## Commands (v0.6.1)
1. ainfera login          — authenticate with API key
2. ainfera init           — detect framework, generate ainfera.yaml
3. ainfera deploy         — deploy agent to Ainfera platform
4. ainfera status         — show agent status + trust score
5. ainfera trust          — detailed trust score breakdown
6. ainfera kill           — trigger kill switch immediately
7. ainfera logs           — stream execution logs
8. ainfera agents         — list/get/create/delete agents
9. ainfera billing        — usage and cost breakdown
10. ainfera trust-check   — CI/CD gate (exits non-zero below threshold)
11. ainfera skill-scan    — scan OpenClaw SKILL.md for trust
12. ainfera register      — register agent in marketplace
13. ainfera discover      — search marketplace for trusted agents
14. ainfera gate          — auto-block untrusted skill installs
15. ainfera health        — unauthenticated API health check

## Project Structure
```
ainfera-cli/
├── src/
│   └── ainfera/
│       ├── __init__.py         # Package version
│       ├── cli.py              # Click group + top-level commands
│       ├── commands/           # One module per command
│       ├── api/
│       │   └── client.py       # httpx client for platform-api
│       ├── config/
│       │   └── settings.py     # CLI config (~/.ainfera/config.yaml)
│       ├── ui/
│       │   ├── console.py      # Rich console singleton
│       │   ├── formatters.py   # Trust score, agent status formatters
│       │   └── themes.py       # Ainfera color theme for Rich
│       └── utils/
│           ├── detect.py       # Framework detection
│           └── errors.py       # Error handling + friendly messages
├── actions/                    # GitHub Actions composite workflows
├── tests/
├── .github/                    # CI, issue templates, PR template
├── pyproject.toml
├── CLAUDE.md
├── README.md
├── CHANGELOG.md
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
- POST /v1/openclaw/skill-scan      — scan SKILL.md for trust
- POST /v1/openclaw/agents/register — register agent in marketplace
- GET  /v1/openclaw/agents/discover — search marketplace

## Conventions
- All API calls go through src/ainfera/api/client.py
- All terminal output goes through src/ainfera/ui/console.py
- Errors use click.ClickException with Rich-formatted messages
- Config stored in ~/.ainfera/config.yaml (API key, default project, API URL)
- --json flag on every command for machine-readable output
- --verbose / -v flag for debug logging

## Seed-stage integration scope (cli)

The `ainfera` CLI at seed supports **3 agent frameworks and 4 model providers**:

| Category | Partners |
|---|---|
| Compute & Inference | NVIDIA (NIM, Guardrails) |
| Model Providers | Anthropic (Claude, MCP), OpenAI (GPT), Hugging Face (open weights) |
| Agent Frameworks | LangChain (+LangGraph), CrewAI, OpenClaw |
| Settlement | Stripe Connect (built-in, not optional) |

The `--framework` Click option is restricted to `langchain`, `crewai`, `openclaw`.

**Do not add framework support for AutoGen, LlamaIndex, Google ADK, Semantic
Kernel, Haystack, or Pydantic-AI at seed.** They ship in Q4 2026.

## Lockstep rule

When adding a new framework, update three places in one PR:
1. `console/lib/integrations.ts` SEED_INTEGRATIONS
2. `platform-api/app/config/integrations.py` SEED_INTEGRATIONS
3. `cli/src/ainfera/commands/init.py` framework Click option
4. `cli/pyproject.toml` optional-dependencies (if adding extras)

## Revenue split (locked April 17, 2026)

**85% creator · 5% platform · 10% compute.** Supersedes the pre-April split.

Surface in `ainfera billing` output and in README Revenue split section.

## URL convention (post-apex-cutover Apr 17, 2026)

- `https://ainfera.ai` — marketing site
- `https://app.ainfera.ai` — logged-in product (linked from CLI output when prompting user to view in browser)
- `https://api.ainfera.ai` — API endpoint (default `AINFERA_API_URL`)
- `https://console.ainfera.ai` — legacy, 308-redirected to apex

## Canonical values (do not drift)

- PyPI package: `ainfera` (pip install ainfera). SDK is a separate package: `ainfera-sdk`.
- PyPI version: **0.6.1** (do not bump without explicit release plan).
- License: Apache 2.0.
- Maintainer: Hizrian Raz `<hizrian@ainfera.ai>` — all commits authored under this identity.
- API default: `https://api.ainfera.ai`.
- Config path: `~/.ainfera/config.yaml`.
- Env prefix: `AINFERA_*`.

## Trust grade boundaries (canonical across site, CLI, SDK, API)

- AAA ≥ 900 · AA ≥ 800 · A ≥ 700 · BBB ≥ 600 · BB ≥ 500 · B ≥ 400
- CCC < 400 → auto-quarantine

## ainfera.yaml canonical schema

Use ONE form across README, `ainfera init` scaffold, and yaml_parser validation:
`agent.trust` uses `min_score` + `auto_kill_below`. `agent.compute` uses
`tier` + `timeout` (seconds). Legacy keys (`anomaly_detection`,
`quarantine_threshold`, `sandbox`, `memory`, `cpu`) are still accepted by
the parser during Alpha.

## Contributor policy

Solo-maintained by Hizrian. Do not introduce commits authored under bot
identities (no `claude` account, no CI-bot committers). Local
`git config user.email` must match `hizrian@ainfera.ai`.

## NVIDIA Inception compliance

Forbidden vocabulary in the CLI's `--help` text, README, changelog, error
messages, and any printed output:

- `blockchain`, `stablecoin`, `web3`, `mainnet`, `decentralized`, `wallet`
- `smart contract`, `x402`, `coin`, `mining`
- `merkle`, `tamper-evident`, `hash-chain`

The CLI doesn't currently use any of these. Keep it that way.
