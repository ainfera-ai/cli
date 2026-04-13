---
description: Verify the CLI connects to the live API
---

Test the CLI against the live production API:

```bash
ainfera health
ainfera agents list
```

If not authenticated:
```bash
ainfera auth login
```

Report the connection status and any errors.
