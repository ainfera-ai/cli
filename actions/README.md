# Ainfera GitHub Actions

Trust-gate your agent CI/CD pipeline. Three composite actions you can drop into
any workflow. All of them install the
[`ainfera`](https://pypi.org/project/ainfera/) CLI on the runner and call the
Ainfera platform API.

Trust evaluation is powered by **NVIDIA NeMo Guardrails** (safety dimension) and
**NVIDIA NIM** inference (reliability, quality, performance, reputation).

```
actions/
├── deploy-agent/    Deploy an agent from ainfera.yaml
├── trust-check/     Compare trust score before/after a commit, comment on PR
└── sandbox-test/    Validate ainfera.yaml and run your test suite
```

## Prerequisites

Add your Ainfera API key as a repository secret named `AINFERA_API_KEY`.
Get a key at <https://console.ainfera.ai/settings/api-keys>.

---

## deploy-agent

Deploys your agent from `ainfera.yaml`. Creates the agent on the first run,
updates it on every subsequent run.

```yaml
name: Deploy Agent
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ainfera-ai/cli/actions/deploy-agent@v0.4.0
        with:
          api-key: ${{ secrets.AINFERA_API_KEY }}
```

**Inputs:** `api-key` (required), `config` (default `ainfera.yaml`),
`api-url`, `python-version`, `cli-version`.
**Outputs:** `agent-id`, `trust-score`.

---

## trust-check

Fetches the agent's trust score, diffs it against the pre-commit baseline,
posts a PR comment with a dimension breakdown, and fails the check if the
score drops below a threshold.

```yaml
name: Trust Check
on:
  pull_request:
    branches: [main]

jobs:
  trust:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: ainfera-ai/cli/actions/trust-check@v0.4.0
        with:
          api-key: ${{ secrets.AINFERA_API_KEY }}
          agent-id: ${{ vars.AINFERA_AGENT_ID }}
          threshold: 800
```

The PR comment looks like:

```
## Ainfera Trust Check

| Dimension | Before | After | Change |
|-----------|--------|-------|--------|
| Safety      | 0.94 | 0.71 | -0.23 ⚠️ |
| Reliability | 0.92 | 0.89 | -0.03 |
...

Score: AA 847 → A 792 (-55)
Status: ❌ FAILED (threshold: 800)
```

**Inputs:** `api-key` (required), `agent-id` (required),
`threshold` (default `0`, no gate), `comment-on-pr`, `api-url`.
**Outputs:** `score`, `grade`, `delta`.

---

## sandbox-test

Validates `ainfera.yaml` with `ainfera deploy --dry-run`, then runs your test
command.

```yaml
name: Sandbox Test
on:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - uses: ainfera-ai/cli/actions/sandbox-test@v0.4.0
        with:
          api-key: ${{ secrets.AINFERA_API_KEY }}
          test-command: pytest -xvs
```

**Inputs:** `api-key` (required), `config` (default `ainfera.yaml`),
`test-command` (default `pytest`), `api-url`, `python-version`.

---

## Versioning

Pin to a release tag (e.g. `@v0.4.0`) in production. Using `@main` will pick up
breaking changes whenever they land.
