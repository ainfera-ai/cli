---
description: Test CLI against live API
---

```bash
ainfera health
ainfera agents list 2>/dev/null || echo "Auth needed: run 'ainfera auth login'"
```
