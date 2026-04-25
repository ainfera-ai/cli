# Ainfera Deploy Agent Action

Deploy an Ainfera agent from `ainfera.yaml` on every push.

## Usage

```yaml
name: Deploy agent
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ainfera-ai/cli/actions/deploy-agent@v0
        with:
          api-key: ${{ secrets.AINFERA_API_KEY }}
```

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `api-key` | yes | — | API key starting with `ainf_`. Store as a repository secret. |
| `config` | no | `ainfera.yaml` | Path to the agent config file. |
| `api-url` | no | `https://api.ainfera.ai` | Override the Ainfera API URL. |
| `python-version` | no | `3.11` | Python version to install. |
| `cli-version` | no | latest | Pin a specific `ainfera` CLI version. |

## Outputs

| Name | Description |
| --- | --- |
| `agent-id` | The ID of the deployed agent. |
| `trust-score` | The agent's current trust score. |
