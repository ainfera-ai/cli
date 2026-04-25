"""Shared test fixtures for Ainfera CLI tests."""

from __future__ import annotations

import pytest
from click.testing import CliRunner


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def tmp_config(tmp_path, monkeypatch):
    """Redirect config to a temporary directory."""
    config_dir = tmp_path / ".ainfera"
    config_dir.mkdir()
    monkeypatch.setattr("ainfera.config.settings.CONFIG_DIR", config_dir)
    monkeypatch.setattr("ainfera.config.settings.CONFIG_FILE", config_dir / "config.yaml")
    return config_dir


@pytest.fixture
def mock_api_key(monkeypatch):
    """Set a fake API key in the environment."""
    monkeypatch.setenv("AINFERA_API_KEY", "ainf_test_key_12345")


@pytest.fixture
def sample_agent():
    """Sample agent API response."""
    return {
        "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "name": "research-agent",
        "framework": "langchain",
        "status": "running",
        "current_trust_score": 847,
        "trust_grade": "AA",
        "kill_switch_status": "armed",
        "repo_url": "https://github.com/user/research-agent",
        "branch": "main",
        "last_deployed_at": "2026-04-15T14:23:01Z",
    }


@pytest.fixture
def sample_trust():
    """Sample trust score API response."""
    return {
        "score": 847,
        "grade": "AA",
        "dimensions": {
            "safety": 0.91,
            "reliability": 0.88,
            "quality": 0.85,
            "performance": 0.87,
            "reputation": 0.82,
        },
        "assessment_count": 47,
        "public": True,
        "computed_at": "3 minutes ago",
        "anomaly_count": 0,
        "kill_switch_status": "armed",
        "quarantine_threshold": 400,
    }
