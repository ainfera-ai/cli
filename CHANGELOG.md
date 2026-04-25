# Changelog

All notable changes to the `ainfera` CLI are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.1] — 2026-04-17

Current release.

### Commands

- `ainfera login` / `auth login` — API-key authentication
- `ainfera status` / `health` — platform health and auth overview
- `ainfera init` — scaffold `ainfera.yaml`
- `ainfera deploy [--demo]` — deploy agent; showcase sequence with mock data
- `ainfera agents list|get|create|delete` — manage agents
- `ainfera trust [--history|--anomalies]` — trust score views
- `ainfera trust-check --agent-id ID --threshold N [--format json]` — CI/CD gate
- `ainfera skill-scan <name|path>` — scan a skill definition for trust
- `ainfera register --name NAME` — publish agent to the marketplace
- `ainfera discover <query>` — search the marketplace
- `ainfera gate --enable` — auto-block untrusted skill installs
- `ainfera billing` — usage and cost breakdown
- `ainfera kill` — trigger or clear kill switch
- `ainfera logs [--follow]` — view or stream execution logs

### Canonical surfaces

- `ainfera.yaml` schema: `agent.trust` with `min_score` + `auto_kill_below`;
  `agent.compute` with `tier` + `timeout` (seconds). Legacy keys
  (`anomaly_detection`, `quarantine_threshold`, `sandbox`, `memory`, `cpu`)
  still parse.
- Trust grade boundaries: `AAA ≥ 900 · AA ≥ 800 · A ≥ 700 · BBB ≥ 600 · BB ≥ 500 · B ≥ 400 · CCC < 400`.
- Agent DID format: `did:web:ainfera.ai:agents:{id}`.
- Revenue split: `85 / 5 / 10` (creator / platform / compute).
- Global flags: `--json`, `--verbose`/`-v`, `--api-url`.

### GitHub Actions

Three composite actions under `actions/`:

- `deploy-agent`
- `trust-check`
- `sandbox-test`

[0.6.1]: https://github.com/ainfera-ai/cli/releases/tag/v0.6.1
