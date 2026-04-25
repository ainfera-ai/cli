# Ainfera Trust Check Action

Fetch an agent's trust score and optionally comment on the PR or fail the build below a floor.

## Usage

```yaml
name: Trust check
on: pull_request

jobs:
  trust:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: ainfera-ai/cli/actions/trust-check@v0
        with:
          api-key: ${{ secrets.AINFERA_API_KEY }}
          agent-id: ${{ vars.AINFERA_AGENT_ID }}
          min-score: "700"
```

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `api-key` | yes | — | API key starting with `ainf_`. |
| `agent-id` | no | default | Explicit agent ID. Falls back to the CLI's configured default. |
| `min-score` | no | `0` | Fail the job if the score falls below this (0 disables the gate). |
| `api-url` | no | `https://api.ainfera.ai` | Override the Ainfera API URL. |
| `comment-on-pr` | no | `true` | Post the score as a PR comment. |

## Outputs

| Name | Description |
| --- | --- |
| `score` | Current trust score (0-1000). |
| `grade` | Trust grade (AAA, AA, A, B, C, D). |
