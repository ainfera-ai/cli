"""Error handling and friendly error messages."""

from __future__ import annotations

import click
import httpx


def handle_api_error(response: httpx.Response) -> None:
    """Raise a click.ClickException with a friendly message for API errors."""
    status = response.status_code

    messages = {
        401: "API key invalid. Run `ainfera login` to re-authenticate.",
        403: "Insufficient permissions for this action.",
        404: "Agent not found. Run `ainfera status --all` to list your agents.",
        429: f"Rate limit exceeded. Try again in {response.headers.get('retry-after', '30')} seconds.",
    }

    if status in messages:
        raise click.ClickException(messages[status])

    if status >= 500:
        raise click.ClickException(
            "Ainfera API error. Try again or check https://status.ainfera.ai"
        )

    if status >= 400:
        detail = ""
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        raise click.ClickException(f"API error ({status}): {detail}")
