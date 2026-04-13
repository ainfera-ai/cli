---
description: Build the package and verify it
---

Build the package locally and verify.

```bash
python -m build
ls -la dist/
pip install dist/ainfera-*.whl --force-reinstall
ainfera --version
ainfera --help
```
