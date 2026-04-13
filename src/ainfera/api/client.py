"""HTTP client for the Ainfera platform-api."""

from __future__ import annotations

import click
import httpx

from ainfera.utils.errors import handle_api_error


class AinferaClient:
    """Thin HTTP client wrapping the Ainfera platform API."""

    def __init__(self, api_key: str, api_url: str = "https://api.ainfera.ai"):
        self.api_url = api_url
        self.client = httpx.Client(
            base_url=api_url,
            headers={
                "X-Ainfera-Key": api_key,
                "User-Agent": "ainfera-cli/0.1.0",
            },
            timeout=30.0,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an API request and handle errors."""
        try:
            response = self.client.request(method, path, **kwargs)
        except httpx.ConnectError:
            raise click.ClickException(
                f"Cannot connect to Ainfera API at {self.api_url}\n"
                "  Check your network connection or API URL."
            )
        except httpx.TimeoutException:
            raise click.ClickException(
                "Request timed out. The Ainfera API may be experiencing issues.\n"
                "  Try again or check https://status.ainfera.ai"
            )

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
        framework: str,
        repo_url: str | None = None,
        branch: str = "main",
        config_yaml: str = "",
    ) -> dict:
        return self._request(
            "POST",
            "/v1/agents",
            json={
                "name": name,
                "framework": framework,
                "repo_url": repo_url,
                "branch": branch,
                "config_yaml": config_yaml,
            },
        )

    def get_agent(self, agent_id: str) -> dict:
        return self._request("GET", f"/v1/agents/{agent_id}")

    def list_agents(self, page: int = 1, per_page: int = 20) -> dict:
        return self._request(
            "GET", "/v1/agents", params={"page": page, "per_page": per_page}
        )

    def deploy_agent(self, agent_id: str) -> dict:
        return self._request("POST", f"/v1/agents/{agent_id}/deploy")

    def kill_agent(self, agent_id: str, reason: str = "manual_kill") -> dict:
        return self._request(
            "POST", f"/v1/agents/{agent_id}/kill", json={"reason": reason}
        )

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
                f"Cannot connect to Ainfera API at {self.api_url}"
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
