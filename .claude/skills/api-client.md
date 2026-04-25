---
name: api-client
description: Work with the Ainfera API client. Use when adding new API methods, fixing HTTP issues, or changing auth flow.
---

# API Client

## Config Location
`~/.ainfera/config.yaml`:
```yaml
api_url: https://api.ainfera.ai
api_key: ainf_xxxxxxxxxxxx
```

Override with env vars: `AINFERA_API_URL`, `AINFERA_API_KEY`

## Client Pattern
```python
import httpx
from ainfera.config import load_config

class AinferaClient:
    def __init__(self, api_url: str, api_key: str):
        self.client = httpx.Client(
            base_url=api_url,
            headers={"X-Ainfera-Key": api_key},
            timeout=30.0
        )
    
    def list_agents(self) -> list[dict]:
        r = self.client.get("/v1/agents")
        r.raise_for_status()
        return r.json()

def get_client() -> AinferaClient:
    config = load_config()
    if not config.api_key:
        raise click.ClickException("Not authenticated. Run 'ainfera auth login'")
    return AinferaClient(config.api_url, config.api_key)
```

## Error Handling
- 401 → "Authentication failed. Run 'ainfera auth login'"
- 404 → "Agent not found: {id}"
- 422 → "Invalid request: {detail}"
- 500 → "API error. Check https://api.ainfera.ai/health"
- Connection error → "Cannot reach API at {url}. Is it running?"
