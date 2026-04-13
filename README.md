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
ainfera login --key ainf_your_api_key

# Initialize in your agent repo
cd my-agent
ainfera init

# Deploy
ainfera deploy

# Check trust score
ainfera trust

# View live logs
ainfera logs --follow

# Emergency stop
ainfera kill
```

## Commands

| Command | Description |
|---------|-------------|
| `ainfera login` | Authenticate with your API key |
| `ainfera init` | Detect framework and generate ainfera.yaml |
| `ainfera deploy` | Deploy agent to sandboxed environment |
| `ainfera status` | View agent status and trust score |
| `ainfera trust` | Detailed trust score breakdown |
| `ainfera kill` | Trigger kill switch (emergency stop) |
| `ainfera logs` | View or stream execution logs |

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

Every command supports `--json` for scripting:

```bash
ainfera status --json | jq '.trust_grade'
ainfera trust --json | jq '.dimensions'
```

## ainfera.yaml

Configuration for your agent lives in `ainfera.yaml` at the repo root:

```yaml
name: research-agent
framework: langchain
version: 0.1.0

compute:
  sandbox: docker
  memory: 512mb
  cpu: 1
  timeout: 300s

trust:
  anomaly_detection: true
  quarantine_threshold: 400

billing:
  model: per_call
  price_per_call: 0.003
  creator_share: 0.80

inference:
  provider: openai
  model: gpt-4o-mini

kill_switch:
  enabled: true
  auto_quarantine: true
```

## Links

- [Documentation](https://docs.ainfera.ai)
- [Console](https://console.ainfera.ai)
- [API Reference](https://api.ainfera.ai/docs)
- [GitHub](https://github.com/ainfera-ai)

## License

Apache 2.0 — see [LICENSE](LICENSE)
