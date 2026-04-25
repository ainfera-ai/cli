"""Error handling and friendly error messages."""

from __future__ import annotations

import click
import httpx


def handle_api_error(response: httpx.Response) -> None:
    """Raise a click.ClickException with a friendly message for API errors."""
    status = response.status_code

    def _detail() -> str:
        try:
            body = response.json()
        except Exception:
            return response.text or ""
        if isinstance(body, dict):
            return str(body.get("detail") or body.get("message") or body)
        return str(body)

    if status == 401:
        raise click.ClickException(
            "Authentication failed. Run 'ainfera auth login' to set your API key."
        )
    if status == 403:
        raise click.ClickException("Insufficient permissions for this action.")
    if status == 404:
        path = str(response.request.url.path) if response.request else ""
        tail = path.rstrip("/").rsplit("/", 1)[-1]
        if tail and tail not in {"agents", "trust", "v1"}:
            raise click.ClickException(f"Agent not found: {tail}")
        raise click.ClickException("Not found.")
    if status == 422:
        raise click.ClickException(f"Invalid request: {_detail()}")
    if status == 429:
        retry = response.headers.get("retry-after", "30")
        raise click.ClickException(
            f"Rate limit exceeded. Try again in {retry} seconds."
        )

    if status >= 500:
        raise click.ClickException(
            "API error. Check https://api.ainfera.ai/health"
        )

    if status >= 400:
        raise click.ClickException(f"API error ({status}): {_detail()}")
