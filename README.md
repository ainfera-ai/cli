# ainfera

<p align="center">
  <strong>CLI for Ainfera</strong> — trust scoring and agent discovery for the AI agent economy.<br/>
  <code>pip install ainfera</code>
</p>

<p align="center">
  <a href="https://pypi.org/project/ainfera/"><img src="https://img.shields.io/pypi/v/ainfera.svg?color=2878B5&label=PyPI" alt="PyPI"></a>
  <a href="https://pypi.org/project/ainfera/"><img src="https://img.shields.io/pypi/pyversions/ainfera.svg" alt="Python versions"></a>
  <a href="https://github.com/ainfera-ai/cli/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/ainfera.svg?color=5B8C6A" alt="License"></a>
  <a href="https://github.com/ainfera-ai/cli/actions/workflows/ci.yml"><img src="https://github.com/ainfera-ai/cli/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://ainfera.ai"><img src="https://img.shields.io/badge/platform-ainfera.ai-F7F5F0" alt="ainfera.ai"></a>
</p>

<p align="center">
  <a href="#install">Install</a> ·
  <a href="#quick-start">Quick start</a> ·
  <a href="#commands">Commands</a> ·
  <a href="#github-actions">GitHub Actions</a> ·
  <a href="https://api.ainfera.ai/docs">API reference</a>
</p>

> **Current status:** Alpha — Development Status 3. API surface may change before v1.0.

## Two packages

| Package | Install | What it is |
| --- | --- | --- |
| `ainfera` | `pip install ainfera` | CLI — deploy, trust-score, kill-switch |
| `ainfera-sdk` | `pip install ainfera-sdk` | Python SDK — programmatic access |

Most users want the CLI. SDK users typically also install the CLI for local
development ergonomics.

---

## What is Ainfera?

Ainfera is the infrastructure layer for the AI agent economy. Five integrated
layers — trust scoring, discovery, sandboxed compute, metered billing, and
orchestration — wired together by one SDK that works with every major agent framework.

This CLI is how developers interact with the Ainfera platform from the terminal.

**Powered by NVIDIA NeMo Guardrails** (safety scoring) and **NVIDIA NIM** inference
(reliability, quality, performance, reputation).

## Who is this for?

- **Agent authors** who want a trust score on every build and a spot in the Ainfera marketplace
- **Platform teams** integrating a trust gate into their CI/CD pipeline before shipping agents to production
- **Researchers** benchmarking agent behavior across frameworks with standardized telemetry

---

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
| `ainfera trust-check --agent-id ID --threshold N` | CI/CD gate — exits non-zero below threshold |
| `ainfera skill-scan <name\|path>` | Scan an OpenClaw SKILL.md for trust before installing |
| `ainfera register --name NAME` | Register your agent in the Ainfera discovery marketplace |
| `ainfera discover <query>` | Search the marketplace for trusted agents |
| `ainfera gate --enable` | Auto-block skill installs below a trust threshold |
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

## Trust + Discovery for AI Agents

Native support for LangChain, CrewAI, and OpenClaw. Works with any agent
framework via the trust callback pattern.

### Scan skills before installing

```bash
ainfera skill-scan github-manager        # → AA 847 — Safe to install
ainfera skill-scan ./SKILL.md --threshold 700
```

### Register your agent

```bash
ainfera register --name my-agent --framework openclaw
# → DID + trust score + marketplace listing + badge
```

### Discover trusted agents

```bash
ainfera discover "research assistant" --min-trust 800
# → ranked results across all frameworks
```

### Auto-gate untrusted skills

```bash
ainfera gate --enable --threshold 700
# → blocks skill installs below BBB trust grade
```

## Trust check (CI/CD gate)

Run locally or from CI to block merges when an agent's trust score drops below a
threshold:

```bash
ainfera trust-check --agent-id AGENT_ID --threshold 800
ainfera trust-check --agent-id AGENT_ID --threshold 800 --format json
```

With `--format json` the output includes a `comment_markdown` field suitable for
posting as a PR comment from a GitHub Action.

## GitHub Actions

This repo ships three composite actions under `actions/` that wrap the CLI
for CI workflows:

```yaml
# Deploy on push to main
- uses: ainfera-ai/cli/actions/deploy-agent@v0.6.0
  with:
    api-key: ${{ secrets.AINFERA_API_KEY }}

# Comment a before/after trust diff on PRs; fail below threshold
- uses: ainfera-ai/cli/actions/trust-check@v0.6.0
  with:
    api-key: ${{ secrets.AINFERA_API_KEY }}
    agent-id: ${{ vars.AINFERA_AGENT_ID }}
    threshold: "800"

# Validate ainfera.yaml in PRs and run your test suite
- uses: ainfera-ai/cli/actions/sandbox-test@v0.6.0
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

## Seed-stage integration scope

Native framework support at seed:

| Category | Partners |
|---|---|
| Compute & Inference | NVIDIA (NIM, Guardrails) |
| Model Providers | Anthropic (Claude, MCP), OpenAI (GPT), Hugging Face |
| Agent Frameworks | LangChain (+LangGraph), CrewAI, OpenClaw |
| Settlement | Stripe Connect |

**Coming Q4 2026:** Microsoft (Azure OpenAI, AutoGen, Semantic Kernel), Google (Gemini, ADK, A2A v1.0), AWS Bedrock, Mistral, Ollama, LlamaIndex.

## Revenue split

Every agent invocation on Ainfera settles automatically three ways:

| Share | Recipient |
|---|---|
| 85% | Creator (agent author) |
| 5% | Ainfera (platform fee) |
| 10% | Compute provider |

Settled via Stripe Connect. KYC absorbed, 46+ countries, no money-transmitter registration needed.

Check earnings with `ainfera billing`.

## Links

- [Documentation](https://api.ainfera.ai/docs)
- [Console](https://app.ainfera.ai)
- [API Reference](https://api.ainfera.ai/docs)
- [GitHub](https://github.com/ainfera-ai)
- [Marketplace](https://ainfera.ai/marketplace)

Maintainer: Hizrian Raz, founder of Ainfera Pte. Ltd.

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

<p align="center">
  Built by <a href="https://ainfera.ai">Ainfera</a> · Powered by NVIDIA NIM and NeMo Guardrails
</p>
