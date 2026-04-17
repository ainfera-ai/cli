# Changelog

All notable changes to the `ainfera` CLI are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Breaking (schema):** `ainfera.yaml` canonical `agent.trust` block replaces
  `anomaly_detection` / `quarantine_threshold` with `min_score` and
  `auto_kill_below`. Legacy keys are still accepted during Alpha — loaders
  migrate `quarantine_threshold` → `auto_kill_below` transparently.
- `ainfera.yaml` canonical `agent.compute` block uses `tier`
  (`basic` | `standard` | `gpu`) and integer `timeout` (seconds). Legacy
  `sandbox` / `memory` / `cpu` fields still parse.
- README documents canonical trust grade boundaries
  (AAA≥900 · AA≥800 · A≥700 · BBB≥600 · BB≥500 · B≥400 · CCC<400).

### Added
- `pyproject.toml` per-framework optional extras (`langchain`, `crewai`,
  `openclaw`, `anthropic`, `openai`, `huggingface`, `nvidia`, `all`).

## [0.6.1] — 2026-04-17

### Changed
- Align framework support documentation to canonical seed-stage set (LangChain, CrewAI, OpenClaw)
- Update homepage and repository URLs to `ainfera.ai` apex (DNS cutover Apr 17)
- Reference `app.ainfera.ai` for logged-in console surfaces
- README hero rework — badges, Who-is-this-for section, seed integration table

### Added
- `CHANGELOG.md` with full release history
- GitHub Actions CI workflow (ruff + pytest across Python 3.10/3.11/3.12)
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- Issue templates + PR template under `.github/`

## [0.6.0] — 2026-04-16

### Added
- `ainfera skill-scan` command — scan OpenClaw SKILL.md files for trust before installing
- `ainfera register` command — publish agent to the Ainfera marketplace
- `ainfera discover` command — search marketplace for trusted agents
- `ainfera gate` command — auto-block skill installs below a trust threshold

## [0.5.0] — 2026-04-15

### Added
- `ainfera deploy --demo` flag for stage-ready showcase with zero network calls
- `--json` global flag for machine-readable output across all subcommands
- `--api-url` global flag to point at staging or local dev environments
- `ainfera status` consolidates API/DB/Redis/auth/CLI health into a single panel
- `ainfera trust-check` CI gate with `comment_markdown` output for PR comments

### Changed
- Streamlined `ainfera init` interactive flow when all flags provided

## [0.3.0] — 2026-04-14

### Added
- Three GitHub Actions composite workflows: `deploy-agent`, `trust-check`, `sandbox-test`
- `actions/` directory with individual READMEs

## [0.2.1] — 2026-04-13

### Fixed
- Config file permissions on Linux installs

## [0.2.0] — 2026-04-13

### Added
- `ainfera logs --follow` streaming log tail
- `ainfera kill` emergency agent termination

## [0.1.0] — 2026-04-13

### Added
- Initial release
- `ainfera auth login`, `agents list/get/create/delete`, `trust`, `billing`

[0.6.1]: https://github.com/ainfera-ai/cli/releases/tag/v0.6.1
[0.6.0]: https://github.com/ainfera-ai/cli/releases/tag/v0.6.0
[0.5.0]: https://github.com/ainfera-ai/cli/releases/tag/v0.5.0
[0.3.0]: https://github.com/ainfera-ai/cli/releases/tag/v0.3.0
[0.2.1]: https://github.com/ainfera-ai/cli/releases/tag/v0.2.1
[0.2.0]: https://github.com/ainfera-ai/cli/releases/tag/v0.2.0
[0.1.0]: https://github.com/ainfera-ai/cli/releases/tag/v0.1.0
