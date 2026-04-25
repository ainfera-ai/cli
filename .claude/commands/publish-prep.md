Prepare for PyPI publication without actually publishing. Steps:
1. pytest -xvs (100% pass)
2. ruff check . (clean)
3. mypy src/ainfera/ --ignore-missing-imports
4. Brand-words grep battery (see /brand-check)
5. Version in __init__.py matches pyproject.toml
6. CHANGELOG.md has current version entry
7. README.md up to date
8. python -m build
9. twine check dist/*
10. Report: "Ready. Run 'twine upload dist/*' manually."

NEVER run twine upload — requires manual execution.
