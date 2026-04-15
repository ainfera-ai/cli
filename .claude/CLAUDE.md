# CLAUDE.md — Ainfera CLI

## What is this
CLI for the Ainfera platform. 10 commands. Python + Click + Rich. Published on PyPI as `ainfera` (v0.3.0). Also contains GitHub Actions under actions/ and Python SDK foundations. The `ainfera deploy` command is a stage demo artifact.

## Commands
ainfera init <n> | deploy [--demo] | status [id] | trust [id] [--history] | logs [id] [--follow] | kill <id> [--force] | billing [--period] | config [show|set|init] | login [--github|--api-key] | whoami

## Structure
src/ainfera/ — cli.py, commands/ (10 modules), api/ (client, models, auth), output/ (console, formatters, themes), config/ (settings, project parser)
actions/ — deploy-agent/, trust-check/, sandbox-test/ (GitHub Actions)
scripts/ — demo.sh, seed helpers

## Rich theme (DS v2)
brand=#2878B5, success=#5B8C6A, warning=#D4A43A, error=#C4453A, muted=#64748B, surface=#001E41, text=#F7F5F0

## NVIDIA compliance
NEVER: blockchain, crypto, decentralized, stablecoin, web3, x402, ledger, hash chain, tamper, mining, wallet, smart contract.
