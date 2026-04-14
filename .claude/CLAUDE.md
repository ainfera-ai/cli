# CLAUDE.md — Ainfera CLI

## What is this

The Ainfera CLI is a command-line tool for deploying and managing AI agents on the Ainfera platform. Python with Rich for terminal output. Distributed via PyPI as `ainfera`. Connects to `api.ainfera.ai`.

The `ainfera deploy` command is a stage demo artifact — its Rich terminal output is designed for investor pitches and conference demos.

## Core commands

```
ainfera init <name>        # Scaffold new agent project
ainfera deploy             # Deploy agent to platform
ainfera status             # Agent status + trust score
ainfera trust              # Trust score breakdown (5 dimensions)
ainfera logs               # Stream execution logs
ainfera kill <agent-id>    # Trigger kill switch
ainfera billing            # Billing summary
ainfera config             # Manage configuration
ainfera login              # Auth via GitHub OAuth or API key
ainfera whoami             # Current user info
```

## Tech stack

Python 3.10+, Click (CLI framework), Rich (terminal formatting), httpx (async HTTP), Pydantic v2 (config/models), keyring (credential storage), tomli/tomli-w (TOML config).

## File structure

```
src/ainfera/
├── __init__.py, __main__.py
├── cli.py                     # Click group + command registration
├── commands/
│   ├── init.py, deploy.py, status.py, trust.py
│   ├── logs.py, kill.py, billing.py
│   ├── config.py, login.py, whoami.py
├── api/
│   ├── client.py              # httpx async client to api.ainfera.ai
│   ├── models.py              # Pydantic response models
│   └── auth.py                # Keyring token management
├── output/
│   ├── console.py             # Rich console singleton
│   ├── formatters.py          # Trust table, deploy header, agent table
│   └── themes.py              # Ainfera DS v2 Rich theme
└── config/
    ├── settings.py            # Pydantic Settings
    └── project.py             # ainfera.yaml parser + framework auto-detect
```

## The deploy command — showcase sequence

`ainfera deploy` terminal output is designed for stage demos:

```
╭─ Ainfera Deploy ──────────────────────────────────╮
│  Agent: my-agent                                   │
│  Framework: LangChain (auto-detected)              │
│  DID: did:ainfera:agent:a7f3                        │
╰────────────────────────────────────────────────────╯

▸ Provisioning sandbox...          Docker (512MB, 1 CPU)  ✓
▸ Computing trust score...         AAA (942)              ✓
▸ Activating billing...            $0.003/invocation      ✓
▸ Arming kill switch...            floor: 400             ✓
▸ Registering protocols...         MCP + A2A              ✓

✓ Agent live → https://api.ainfera.ai/agent/a7f3

┌───────────────┬───────┬────────────────────────┐
│ Dimension     │ Score │ Bar                    │
├───────────────┼───────┼────────────────────────┤
│ Safety        │ 0.96  │ ██████████████████████ │
│ Reliability   │ 0.94  │ ████████████████████░░ │
│ Quality       │ 0.93  │ ███████████████████░░░ │
│ Performance   │ 0.95  │ █████████████████████░ │
│ Reputation    │ 0.94  │ ████████████████████░░ │
└───────────────┴───────┴────────────────────────┘
```

Each step has 300-500ms spinner delay for dramatic effect in demos. `--demo` flag runs with mock data (no API calls).

## Rich theme — DS v2

```python
AINFERA_THEME = Theme({
    "ainfera.brand": "#2878B5",
    "ainfera.hover": "#4A9FD9",
    "ainfera.highlight": "#7EC4EF",
    "ainfera.success": "#5B8C6A",
    "ainfera.warning": "#D4A43A",
    "ainfera.error": "#C4453A",
    "ainfera.muted": "#64748B",
    "ainfera.surface": "#001E41",
    "ainfera.text": "#F7F5F0",
})
```

## ainfera.yaml project config

```yaml
name: my-agent
framework: langchain
version: 0.1.0
trust:
  floor: 400
  dimensions: [safety, reliability, quality, performance, reputation]
sandbox:
  memory_mb: 512
  cpu_cores: 1
  timeout_s: 300
  network: isolated
billing:
  model: per_call
  rate_usd: 0.003
protocols: [mcp, a2a]
```

## API integration

Base URL from AINFERA_API_URL env or ~/.ainfera/config.toml. Token in system keyring via `keyring` library. httpx async with 30s timeout (120s for deploy), 3 retries with exponential backoff on 5xx.

## Output conventions

Success: sage green. Error: vermillion. Data: Rich tables with Ainfera theme. Progress: spinner in Azure. Trust scores: grade + score + colored bar. Costs: USD with 4 decimals ($0.0034). Timestamps: relative < 24h, absolute otherwise. Agent IDs: short form (agent:a7f3).

## NVIDIA compliance — CRITICAL

NEVER use: blockchain, crypto, decentralized, stablecoin, web3, x402, ledger, hash chain, tamper, mining, wallet, smart contract, token (financial context).

## Commands

`python -m ainfera` (run), `pip install -e .` (dev install), `pytest -xvs` (test), `ruff check . && black .` (lint), `python -m build` (build dist).
