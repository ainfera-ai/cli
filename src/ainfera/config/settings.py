"""CLI configuration management — ~/.ainfera/config.yaml."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".ainfera"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

DEFAULT_API_URL = "https://api.ainfera.ai"


def _ensure_config_dir() -> None:
    """Create config directory with secure permissions."""
    CONFIG_DIR.mkdir(mode=0o700, exist_ok=True)


def load_config() -> dict:
    """Load config from ~/.ainfera/config.yaml. Returns empty dict if missing."""
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def save_config(config: dict) -> None:
    """Write config to ~/.ainfera/config.yaml with secure permissions."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    CONFIG_FILE.chmod(0o600)


def get_api_key() -> str | None:
    """Get API key from env var or config file."""
    key = os.environ.get("AINFERA_API_KEY")
    if key:
        return key
    return load_config().get("api_key")


def get_api_url() -> str:
    """Get API URL from env var or config file."""
    url = os.environ.get("AINFERA_API_URL")
    if url:
        return url
    return load_config().get("api_url", DEFAULT_API_URL)


def ensure_authenticated() -> str:
    """Return API key or exit with login instructions."""
    import click

    key = get_api_key()
    if not key:
        raise click.ClickException(
            "Not authenticated. Run 'ainfera auth login' to authenticate, "
            "or set the AINFERA_API_KEY environment variable."
        )
    return key


def get_default_agent() -> str | None:
    """Get the default agent ID from config."""
    return load_config().get("default_agent")


def set_default_agent(agent_id: str) -> None:
    """Set the default agent ID in config."""
    config = load_config()
    config["default_agent"] = agent_id
    save_config(config)
