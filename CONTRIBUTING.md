# Contributing

Thanks for considering a contribution to the Ainfera CLI.

## Local development

Requires Python 3.10+.

```bash
git clone https://github.com/ainfera-ai/cli.git
cd cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
pytest -q
```

Run the linter:

```bash
ruff check .
ruff format .
```

## Pull requests

1. Open an issue first for any non-trivial change — helps us align on approach before code
2. Fork and branch from `main`
3. Keep PRs small and focused — one concern per PR
4. Update `CHANGELOG.md` under `## [Unreleased]`
5. Ensure `pytest` and `ruff check` pass locally before pushing

## Code style

- Type hints on all public functions (strict mypy is aspirational)
- Docstrings on every public function (Google style)
- No `print()` — use the Rich console from `ainfera.ui.console`
- Error messages tell the user what to do next
