# CLAUDE.md — Ainfera CLI (nested)

## What is this

CLI for Ainfera. Python + Click + Rich. Published on PyPI as `ainfera`.
Also ships GitHub Actions under `actions/` and a small internal SDK
helper under `src/ainfera/sdk/` (external callers use the separate
`ainfera-sdk` package).

## Commands

`ainfera init` · `deploy [--demo]` · `status` · `trust [--history|--anomalies]` ·
`logs [--follow]` · `kill` · `billing` · `agents list|get|create|delete` ·
`login` · `auth login` · `auth status` · `health` · `trust-check` ·
`skill-scan` · `register` · `discover` · `gate`.

## Structure

`src/ainfera/` — `cli.py`, `commands/` (one module per command), `api/`
(`client.py`), `ui/` (console, formatters, theme), `config/` (settings,
yaml parser), `sdk/` (internal helper), `utils/` (detection).

`actions/` — `deploy-agent`, `trust-check`, `sandbox-test`.

## Rich theme

Brand identity color is navy `#2878B5` (`ainfera.brand`).

Status (`success`, `warning`, `error`, `info`) carries no hue —
weight and intensity only. See `../docs/DESIGN-SYSTEM.md` §6 for
the full rule and the exact Rich attribute mapping.

## Brand-words enforcement

Every push to a user-facing file must pass the §3 grep battery in
`../docs/BRAND-WORDS.md`. The `../CLAUDE.md` "Brand enforcement"
section points at both reference files.

## Git author identity

This repo's git config carries the founder's identity per
`../docs/BRAND-WORDS.md` §6:

```
user.name  = Hizrian Raz
user.email = hizrian@ainfera.ai
```

Public package metadata (`pyproject.toml` `authors`/`maintainers`)
stays as `Ainfera <hello@ainfera.ai>` (§5).
