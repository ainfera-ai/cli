# Ainfera Sandbox Test Action

Validate `ainfera.yaml` with a dry run and execute your own test command.

## Usage

```yaml
name: Sandbox test
on: pull_request

jobs:
  sandbox:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ainfera-ai/cli/actions/sandbox-test@v0
        with:
          api-key: ${{ secrets.AINFERA_API_KEY }}
          test-command: pytest -xvs
```

## Inputs

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `api-key` | yes | — | API key starting with `ainf_`. |
| `config` | no | `ainfera.yaml` | Path to the agent config file. |
| `test-command` | no | empty | Shell command to run after validation. |
| `api-url` | no | `https://api.ainfera.ai` | Override the Ainfera API URL. |
