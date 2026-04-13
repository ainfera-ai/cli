---
description: Run linting and formatting
---

```bash
ruff check src/ --fix
ruff format src/
mypy src/ --ignore-missing-imports
```

Fix all issues found.
