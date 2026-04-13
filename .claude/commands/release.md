---
description: Tag a release and publish to PyPI
---

Ask what version to release, then:
1. Update version in pyproject.toml
2. Update CHANGELOG.md
3. Commit: "release: v{version}"
4. Tag: `git tag v{version}`
5. Push: `git push origin main --tags`

GitHub Actions publishes to PyPI automatically on tag push.
Verify after ~2 min: `pip install ainfera=={version}`
