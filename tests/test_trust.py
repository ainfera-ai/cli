"""Tests for ainfera trust and related commands."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from ainfera.cli import main
from ainfera.ui.formatters import (
    format_agent_status,
    format_trust_score,
    render_dimension_bar,
)


def test_format_trust_score():
    """Trust score should include grade."""
    result = format_trust_score(847, "AA")
    assert "847" in result
    assert "AA" in result


def test_format_agent_status():
    """Agent status should be styled."""
    result = format_agent_status("running")
    assert "running" in result


def test_render_dimension_bar():
    """Dimension bar should show value."""
    result = render_dimension_bar(0.91)
    assert "0.91" in result


def test_render_dimension_bar_low():
    """Low dimension should use error color."""
    result = render_dimension_bar(0.3)
    assert "0.30" in result
    assert "ainfera.error" in result


def test_trust_json_output(mock_api_key):
    """ainfera trust --json should produce valid JSON."""
    runner = CliRunner()
    mock_client = MagicMock()
    mock_client.get_trust_score.return_value = {
        "score": 847,
        "grade": "AA",
        "dimensions": {"reliability": 0.91, "security": 0.95, "quality": 0.78},
        "assessment_count": 47,
    }

    with (
        patch("ainfera.commands.trust.AinferaClient", return_value=mock_client),
        patch("ainfera.commands.trust.ensure_authenticated", return_value="ainf_test"),
        patch("ainfera.commands.trust.get_default_agent", return_value="agent-123"),
    ):
        result = runner.invoke(main, ["--json", "trust"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["score"] == 847
        assert data["grade"] == "AA"


def test_kill_prompts_for_confirmation(mock_api_key):
    """ainfera kill should prompt for confirmation."""
    runner = CliRunner()
    mock_client = MagicMock()

    with (
        patch("ainfera.commands.kill.AinferaClient", return_value=mock_client),
        patch("ainfera.commands.kill.ensure_authenticated", return_value="ainf_test"),
        patch("ainfera.commands.kill.get_default_agent", return_value="agent-123"),
    ):
        result = runner.invoke(main, ["kill"], input="n\n")
        assert result.exit_code == 0
        mock_client.kill_agent.assert_not_called()


def test_kill_yes_skips_confirmation(mock_api_key):
    """ainfera kill --yes should skip confirmation."""
    runner = CliRunner()
    mock_client = MagicMock()
    mock_client.kill_agent.return_value = {
        "name": "test-agent",
        "status": "quarantined",
        "killed_at": "2026-04-15T14:23:01Z",
    }

    with (
        patch("ainfera.commands.kill.AinferaClient", return_value=mock_client),
        patch("ainfera.commands.kill.ensure_authenticated", return_value="ainf_test"),
        patch("ainfera.commands.kill.get_default_agent", return_value="agent-123"),
    ):
        result = runner.invoke(main, ["kill", "--yes"])
        assert result.exit_code == 0
        mock_client.kill_agent.assert_called_once()


def test_kill_unkill(mock_api_key):
    """ainfera kill --unkill should clear the kill switch."""
    runner = CliRunner()
    mock_client = MagicMock()
    mock_client.unkill_agent.return_value = {"status": "stopped"}

    with (
        patch("ainfera.commands.kill.AinferaClient", return_value=mock_client),
        patch("ainfera.commands.kill.ensure_authenticated", return_value="ainf_test"),
        patch("ainfera.commands.kill.get_default_agent", return_value="agent-123"),
    ):
        result = runner.invoke(main, ["kill", "--unkill"])
        assert result.exit_code == 0
        mock_client.unkill_agent.assert_called_once()


def test_status_overview(mock_api_key):
    """ainfera status should render the platform overview panel."""
    runner = CliRunner()

    fake_health = MagicMock()
    fake_health.status_code = 200
    fake_health.json.return_value = {
        "status": "ok",
        "version": "0.1.0",
        "services": {"db": "ok", "redis": "ok"},
        "stats": None,
    }
    fake_httpx_client = MagicMock()
    fake_httpx_client.__enter__.return_value = fake_httpx_client
    fake_httpx_client.__exit__.return_value = False
    fake_httpx_client.get.return_value = fake_health

    mock_client = MagicMock()
    mock_client.list_agents.return_value = {
        "agents": [
            {"id": "a1", "status": "published", "current_trust_score": 80},
            {"id": "a2", "status": "draft"},
        ],
        "total": 2,
    }

    with (
        patch("ainfera.commands.status.httpx.Client", return_value=fake_httpx_client),
        patch("ainfera.commands.status.AinferaClient", return_value=mock_client),
    ):
        result = runner.invoke(main, ["--json", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["api_online"] is True
        assert data["authenticated"] is True
        assert data["services"]["db"] == "ok"
        assert data["stats"]["total_agents"] == 2
        assert data["stats"]["published_agents"] == 1
        assert data["stats"]["draft_agents"] == 1


def test_login_validates_key_format():
    """ainfera login should reject keys without ainf_ prefix."""
    runner = CliRunner()
    result = runner.invoke(main, ["login", "--key", "invalid_key"])
    assert result.exit_code != 0
