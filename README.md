# ainfera

The CLI for the [Ainfera](https://ainfera.ai) AI agent infrastructure platform.

Deploy AI agents with trust scores, kill switches, and metered billing.
One command.

## Install

```bash
pip install ainfera
```

## Quick Start

```bash
# Authenticate
ainfera auth login --key ainf_your_api_key

# Check the platform + your auth in one panel
ainfera status

# Initialize in your agent repo (interactive, or pass --non-interactive for CI)
cd my-agent
ainfera init --name my-agent --framework langchain --tier standard

# Deploy
ainfera deploy

# List your agents
ainfera agents list

# Check trust score for an agent
ainfera trust score <agent-id>

# Stream live logs
ainfera logs <agent-id> --follow

# Emergency stop
ainfera kill <agent-id>
```

## Commands

| Command | Description |
|---------|-------------|
| `ainfera auth login` | Authenticate with your API key |
| `ainfera auth status` | Show current auth + API health |
| `ainfera status` | Full platform overview (API/DB/Redis/auth/CLI) |
| `ainfera health` | Unauthenticated API health check |
| `ainfera init` | Scaffold an `ainfera.yaml` |
| `ainfera deploy` | Deploy from `ainfera.yaml` |
| `ainfera agents list/get/create/delete` | Manage agents |
| `ainfera trust score/history/anomalies` | Trust score views |
| `ainfera kill` | Trigger or clear kill switch |
| `ainfera logs` | View or stream execution logs |

Pass `--help` to any subcommand for examples (e.g. `ainfera agents create --help`).

## Configuration

The CLI stores config in `~/.ainfera/config.yaml`:

```yaml
api_key: ainf_your_key
api_url: https://api.ainfera.ai
default_agent: a1b2c3d4-...
```

Or use environment variables:
- `AINFERA_API_KEY` — API key (overrides config file)
- `AINFERA_API_URL` — API endpoint (default: https://api.ainfera.ai)

## JSON Output

Pass `--json` (a global flag) for machine-readable output, useful for
scripting and CI/CD pipelines:

```bash
ainfera --json status                       | jq '.api_version'
ainfera --json agents list                  | jq '.items[].name'
ainfera --json trust score <agent-id>       | jq '.overall_score'
```

## Overriding the API URL

Use the global `--api-url` flag to point the CLI at a different
environment (e.g. staging or a local dev server) without editing
`~/.ainfera/config.yaml`:

```bash
ainfera --api-url https://api.staging.ainfera.ai agents list
```

## ainfera.yaml

Configuration for your agent lives in `ainfera.yaml` at the repo root.
Run `ainfera init` (interactive) or `ainfera init --non-interactive --name my-agent
--framework langchain --tier standard` to scaffold one:

```yaml
version: "1"
agent:
  name: research-agent
  framework: langchain
  description: ""
  compute:
    tier: standard       # basic | standard | gpu
    timeout: 30
  trust:
    min_score: 50
    auto_kill_below: 20
  billing:
    model: per-call
    price_per_call: 0.003
```

## Links

- [Documentation](https://docs.ainfera.ai)
- [Console](https://console.ainfera.ai)
- [API Reference](https://api.ainfera.ai/docs)
- [GitHub](https://github.com/ainfera-ai)

## License

Apache 2.0 — see [LICENSE](LICENSE)
