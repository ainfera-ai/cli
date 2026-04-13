---
description: Build and verify package
---

```bash
python -m build
pip install dist/ainfera-*.whl --force-reinstall
ainfera --version
ainfera --help
```
