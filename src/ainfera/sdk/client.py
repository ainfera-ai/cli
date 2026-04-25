"""Synchronous Python SDK for the Ainfera platform API."""

from __future__ import annotations

import os
from typing import Any

from ainfera.api.client import AinferaClient


class AinferaSDK:
    """High-level SDK for programmatic access to the Ainfera platform.

    Wraps :class:`ainfera.api.client.AinferaClient` with friendlier
    method names and sensible defaults. Credentials resolve in this
    order: explicit ``api_key`` argument, then ``AINFERA_API_KEY``
    environment variable.
    """

    def __init__(
        self,
        api_key: str | None = None,
        api_url: str | None = None,
    ) -> None:
        key = api_key or os.environ.get("AINFERA_API_KEY")
        if not key:
            raise ValueError(
                "AinferaSDK requires an API key. "
                "Pass api_key= or set AINFERA_API_KEY."
            )
        url = api_url or os.environ.get("AINFERA_API_URL", "https://api.ainfera.ai")
        self._client = AinferaClient(api_key=key, api_url=url)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "AinferaSDK":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    # ── Health ──────────────────────────────────────────────────────────

    def health(self) -> dict:
        return self._client.health()

    # ── Agents ──────────────────────────────────────────────────────────

    def create_agent(
        self,
        name: str,
        framework: str = "custom",
        *,
        repo_url: str | None = None,
        branch: str = "main",
        config_yaml: str | None = None,
        description: str | None = None,
        is_public: bool | None = None,
    ) -> dict:
        return self._client.create_agent(
            name=name,
            framework=framework,
            repo_url=repo_url,
            branch=branch,
            config_yaml=config_yaml,
            description=description,
            is_public=is_public,
        )

    def get_agent(self, agent_id: str) -> dict:
        return self._client.get_agent(agent_id)

    def list_agents(self, page: int = 1, per_page: int = 20) -> dict:
        return self._client.list_agents(page=page, per_page=per_page)

    def update_agent(self, agent_id: str, **fields: Any) -> dict:
        return self._client.update_agent(agent_id, **fields)

    def delete_agent(self, agent_id: str) -> None:
        self._client.delete_agent(agent_id)

    def deploy_agent(self, agent_id: str) -> dict:
        return self._client.deploy_agent(agent_id)

    # ── Kill switch ─────────────────────────────────────────────────────

    def kill_agent(self, agent_id: str, reason: str = "manual_kill") -> dict:
        return self._client.kill_agent(agent_id, reason=reason)

    def unkill_agent(self, agent_id: str) -> dict:
        return self._client.unkill_agent(agent_id)

    # ── Trust ───────────────────────────────────────────────────────────

    def get_trust_score(self, agent_id: str) -> dict:
        return self._client.get_trust_score(agent_id)

    def get_trust_history(self, agent_id: str, page: int = 1) -> dict:
        return self._client.get_trust_history(agent_id, page=page)

    def get_anomalies(self, agent_id: str) -> dict:
        return self._client.get_anomalies(agent_id)

    # ── Billing ─────────────────────────────────────────────────────────

    def get_usage(self, agent_id: str) -> dict:
        return self._client.get_usage(agent_id)
