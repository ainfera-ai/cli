---
description: Tag a new release and trigger PyPI publish
---

Ask me what version to release (e.g., 0.2.0, 0.3.0).

Then:
1. Update version in pyproject.toml
2. Update CHANGELOG.md with the new version and changes
3. Commit: "release: v{version}"
4. Tag: git tag v{version}
5. Push: git push origin main --tags

The GitHub Actions workflow (.github/workflows/publish.yml) will automatically
build and publish to PyPI when the v* tag is pushed.

Verify after ~2 minutes:
```bash
pip install ainfera=={version}
ainfera --version
```
