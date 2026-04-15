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
ainfera trust <agent-id>

# Stream live logs
ainfera logs <agent-id> --follow

# Emergency stop
ainfera kill <agent-id>
```

Want to see what deploy looks like before you connect the real API? Run
`ainfera deploy --demo` — the stage-ready showcase with mock data, zero
network calls.

## Commands

| Command | Description |
|---------|-------------|
| `ainfera login` | Authenticate with your API key (alias for `auth login`) |
| `ainfera auth login` | Authenticate with your API key |
| `ainfera auth status` | Show current auth + API health |
| `ainfera status` | Full platform overview (API/DB/Redis/auth/CLI) |
| `ainfera health` | Unauthenticated API health check |
| `ainfera init` | Scaffold an `ainfera.yaml` |
| `ainfera deploy` | Deploy from `ainfera.yaml` (add `--demo` for the showcase) |
| `ainfera agents list/get/create/delete` | Manage agents |
| `ainfera trust [--history\|--anomalies]` | Trust score views |
| `ainfera billing` | Usage and cost breakdown |
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
ainfera --json trust <agent-id>             | jq '.score'
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
  compute:
    sandbox: docker        # docker | firecracker
    memory: 512mb
    cpu: 1
    timeout: 300s
  trust:
    anomaly_detection: true
    quarantine_threshold: 400
  billing:
    model: per_call        # per_call | per_token | per_minute
    price_per_call: 0.003
  kill_switch:
    enabled: true
    auto_quarantine: true
```

## GitHub Actions

This repo ships three composite actions under `actions/` that wrap the CLI
for CI workflows:

```yaml
# Deploy on push to main
- uses: ainfera-ai/cli/actions/deploy-agent@v0.4.0
  with:
    api-key: ${{ secrets.AINFERA_API_KEY }}

# Comment a before/after trust diff on PRs; fail below threshold
- uses: ainfera-ai/cli/actions/trust-check@v0.4.0
  with:
    api-key: ${{ secrets.AINFERA_API_KEY }}
    agent-id: ${{ vars.AINFERA_AGENT_ID }}
    threshold: "800"

# Validate ainfera.yaml in PRs and run your test suite
- uses: ainfera-ai/cli/actions/sandbox-test@v0.4.0
  with:
    api-key: ${{ secrets.AINFERA_API_KEY }}
    test-command: pytest -xvs
```

See [actions/README.md](actions/README.md) for full docs.

Each action has its own README in `actions/<name>/README.md`.

## Python SDK

The `ainfera` package also exposes a typed, synchronous SDK for
programmatic use — handy in agent servers, notebooks, or custom
automation:

```python
from ainfera.sdk import AinferaSDK

with AinferaSDK(api_key="ainf_...") as sdk:
    agent = sdk.create_agent(name="my-agent", framework="langchain")
    trust = sdk.get_trust_score(agent["id"])
    print(trust["score"], trust["grade"])
```

## Links

- [Documentation](https://docs.ainfera.ai)
- [Console](https://console.ainfera.ai)
- [API Reference](https://api.ainfera.ai/docs)
- [GitHub](https://github.com/ainfera-ai)

## License

Apache 2.0 — see [LICENSE](LICENSE)
