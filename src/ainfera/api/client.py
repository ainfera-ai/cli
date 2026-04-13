"""HTTP client for the Ainfera platform-api."""

from __future__ import annotations

import click
import httpx

from ainfera import __version__
from ainfera.utils.errors import handle_api_error


class AinferaClient:
    """Thin HTTP client wrapping the Ainfera platform API."""

    def __init__(self, api_key: str, api_url: str = "https://api.ainfera.ai"):
        self.api_url = api_url
        self.client = httpx.Client(
            base_url=api_url,
            headers={
                "X-Ainfera-Key": api_key,
                "User-Agent": f"ainfera-cli/{__version__}",
            },
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an API request and handle errors."""
        try:
            response = self.client.request(method, path, **kwargs)
        except httpx.ConnectError:
            raise click.ClickException(
                f"Cannot reach API at {self.api_url}. Is the server running?"
            )
        except httpx.TimeoutException:
            raise click.ClickException(
                "Request timed out after 30s. The API might be overloaded."
            )
        except httpx.HTTPError as e:
            msg = str(e).lower()
            if "ssl" in msg or "certificate" in msg:
                raise click.ClickException(
                    "SSL certificate error. Check your network configuration."
                )
            raise click.ClickException(f"Network error: {e}")

        if response.status_code >= 400:
            handle_api_error(response)

        if response.status_code == 204:
            return {}
        return response.json()

    def close(self) -> None:
        self.client.close()

    # ── Health ──────────────────────────────────────────────────────────

    def health(self) -> dict:
        return self._request("GET", "/health")

    # ── Agent operations ────────────────────────────────────────────────

    def create_agent(
        self,
        name: str,
        framework: str = "custom",
        repo_url: str | None = None,
        branch: str = "main",
        config_yaml: str | None = None,
        description: str | None = None,
        is_public: bool | None = None,
    ) -> dict:
        payload: dict = {"name": name, "framework": framework, "branch": branch}
        if repo_url is not None:
            payload["repo_url"] = repo_url
        if config_yaml is not None:
            payload["config_yaml"] = config_yaml
        if description is not None:
            payload["description"] = description
        if is_public is not None:
            payload["is_public"] = is_public
        return self._request("POST", "/v1/agents", json=payload)

    def update_agent(self, agent_id: str, **fields) -> dict:
        allowed = {
            "name", "description", "framework", "repo_url",
            "branch", "config_yaml", "status", "is_public",
        }
        payload = {k: v for k, v in fields.items() if k in allowed and v is not None}
        return self._request("PATCH", f"/v1/agents/{agent_id}", json=payload)

    def create_agent_from_config(self, config_yaml: str) -> dict:
        return self._request(
            "POST", "/v1/agents/from-config", json={"config": config_yaml}
        )

    def delete_agent(self, agent_id: str) -> None:
        self._request("DELETE", f"/v1/agents/{agent_id}")

    def get_agent(self, agent_id: str) -> dict:
        return self._request("GET", f"/v1/agents/{agent_id}")

    def list_agents(self, page: int = 1, per_page: int = 20, name: str | None = None) -> dict:
        params: dict = {"page": page, "per_page": per_page}
        if name is not None:
            params["name"] = name
        return self._request("GET", "/v1/agents", params=params)

    def deploy_agent(self, agent_id: str) -> dict:
        return self._request("POST", f"/v1/agents/{agent_id}/deploy")

    def kill_agent(self, agent_id: str, reason: str = "manual_kill") -> dict:
        return self._request("POST", f"/v1/agents/{agent_id}/kill")

    def unkill_agent(self, agent_id: str) -> dict:
        return self._request("DELETE", f"/v1/agents/{agent_id}/kill")

    # ── Trust operations ────────────────────────────────────────────────

    def get_trust_score(self, agent_id: str) -> dict:
        return self._request("GET", f"/v1/trust/{agent_id}")

    def get_trust_history(self, agent_id: str, page: int = 1) -> dict:
        return self._request(
            "GET", f"/v1/trust/{agent_id}/history", params={"page": page}
        )

    def get_anomalies(self, agent_id: str) -> dict:
        return self._request("GET", f"/v1/trust/{agent_id}/anomalies")

    # ── Billing ─────────────────────────────────────────────────────────

    def get_usage(self, agent_id: str) -> dict:
        return self._request("GET", f"/v1/agents/{agent_id}/usage")

    # ── GitHub ──────────────────────────────────────────────────────────

    def detect_framework(self, owner: str, repo: str) -> dict:
        return self._request("GET", f"/v1/github/repos/{owner}/{repo}/detect")

    # ── Logs ────────────────────────────────────────────────────────────

    def get_logs(self, agent_id: str, tail: int = 50) -> str:
        """Get recent log lines (returns raw text)."""
        try:
            response = self.client.get(
                f"/v1/agents/{agent_id}/logs", params={"tail": tail}
            )
        except httpx.ConnectError:
            raise click.ClickException(
                f"Cannot reach API at {self.api_url}. Is the server running?"
            )
        except httpx.TimeoutException:
            raise click.ClickException(
                "Request timed out after 30s. The API might be overloaded."
            )
        if response.status_code >= 400:
            handle_api_error(response)
        return response.text

    def get_stream_url(self, execution_id: str) -> str:
        """Build the WebSocket URL for log streaming."""
        ws_url = self.api_url.replace("https://", "wss://").replace(
            "http://", "ws://"
        )
        return f"{ws_url}/v1/stream/{execution_id}"
