"""Tests for ainfera deploy command."""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from ainfera.cli import main
from ainfera.config.yaml_parser import AinferaConfig, generate_yaml


def _write_ainfera_yaml(tmp_path, name="test-agent"):
    """Write a valid ainfera.yaml to tmp_path."""
    config = AinferaConfig(name=name, framework="langchain")
    (tmp_path / "ainfera.yaml").write_text(generate_yaml(config))


def test_deploy_missing_yaml(tmp_path):
    """Deploy should error if ainfera.yaml is missing."""
    os.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["deploy"])
    assert result.exit_code != 0


def test_deploy_reads_config(tmp_path):
    """Deploy should parse ainfera.yaml correctly."""
    os.chdir(tmp_path)
    _write_ainfera_yaml(tmp_path)
    runner = CliRunner()

    # Mock the API client to avoid real HTTP calls
    mock_client = MagicMock()
    mock_client.create_agent.return_value = {
        "id": "test-id-123",
        "name": "test-agent",
        "status": "deploying",
    }
    mock_client.deploy_agent.return_value = {
        "status": "running",
        "container_id": "ainfera-test123",
        "execution_id": "exec-123",
    }
    mock_client.get_trust_score.return_value = {
        "score": 847,
        "grade": "AA",
    }

    with (
        patch("ainfera.commands.deploy.AinferaClient", return_value=mock_client),
        patch("ainfera.commands.deploy.ensure_authenticated", return_value="ainf_test"),
        patch("ainfera.commands.deploy.set_default_agent"),
    ):
        result = runner.invoke(main, ["deploy"])
        assert result.exit_code == 0
        mock_client.create_agent.assert_called_once()


def test_deploy_json_output(tmp_path):
    """Deploy --json should produce valid JSON output."""
    os.chdir(tmp_path)
    _write_ainfera_yaml(tmp_path)
    runner = CliRunner()

    mock_client = MagicMock()
    mock_client.create_agent.return_value = {
        "id": "test-id-456",
        "name": "test-agent",
    }
    mock_client.deploy_agent.return_value = {
        "status": "running",
        "execution_id": "exec-456",
    }
    mock_client.get_trust_score.return_value = {
        "score": 750,
        "grade": "A",
    }

    with (
        patch("ainfera.commands.deploy.AinferaClient", return_value=mock_client),
        patch("ainfera.commands.deploy.ensure_authenticated", return_value="ainf_test"),
        patch("ainfera.commands.deploy.set_default_agent"),
    ):
        result = runner.invoke(main, ["--json", "deploy"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["agent_id"] == "test-id-456"
        assert data["trust_score"] == 750


def test_deploy_without_login(tmp_path, monkeypatch):
    """Deploy without authentication should show error."""
    os.chdir(tmp_path)
    _write_ainfera_yaml(tmp_path)
    monkeypatch.delenv("AINFERA_API_KEY", raising=False)

    # Redirect config to empty temp dir
    config_dir = tmp_path / ".ainfera"
    config_dir.mkdir()
    monkeypatch.setattr("ainfera.config.settings.CONFIG_DIR", config_dir)
    monkeypatch.setattr("ainfera.config.settings.CONFIG_FILE", config_dir / "config.yaml")

    runner = CliRunner()
    result = runner.invoke(main, ["deploy"])
    assert result.exit_code != 0
