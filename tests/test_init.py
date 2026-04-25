"""Tests for ainfera init command."""

from __future__ import annotations

import json
import os


from ainfera.cli import main
from ainfera.config.yaml_parser import AinferaConfig, generate_yaml, parse_yaml
from ainfera.utils.detect import detect_framework


def test_detect_langchain(tmp_path):
    """Detect the langchain framework from requirements.txt."""
    (tmp_path / "requirements.txt").write_text("langchain==0.3.1\nopenai>=1.0\n")
    fw, details = detect_framework(str(tmp_path))
    assert fw == "langchain"
    assert details["version"] == "0.3.1"
    assert details["confidence"] == "high"


def test_detect_crewai(tmp_path):
    """Detect the crewai framework from requirements.txt."""
    (tmp_path / "requirements.txt").write_text("crewai>=0.28\n")
    fw, details = detect_framework(str(tmp_path))
    assert fw == "crewai"


def test_detect_openai_sdk(tmp_path):
    """Detect the openai_sdk framework when no other is present."""
    (tmp_path / "requirements.txt").write_text("openai>=1.0\nfastapi\n")
    fw, details = detect_framework(str(tmp_path))
    assert fw == "openai_sdk"


def test_detect_custom(tmp_path):
    """Return custom when no framework detected."""
    (tmp_path / "requirements.txt").write_text("flask\ncelery\n")
    fw, details = detect_framework(str(tmp_path))
    assert fw == "custom"
    assert details["confidence"] == "low"


def test_detect_from_package_json(tmp_path):
    """Detect framework from package.json."""
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"langchain": "^0.2.0"}})
    )
    fw, details = detect_framework(str(tmp_path))
    assert fw == "langchain"
    assert details["source_file"] == "package.json"


def test_generate_yaml_produces_valid_output():
    """Generated YAML should be parseable back."""
    config = AinferaConfig(name="test-agent", framework="langchain")
    yaml_str = generate_yaml(config)
    parsed = parse_yaml(yaml_str)
    assert parsed.name == "test-agent"
    assert parsed.framework == "langchain"
    assert parsed.compute.tier == "standard"
    assert parsed.compute.timeout == 30
    assert parsed.trust.min_score == 700
    assert parsed.trust.auto_kill_below == 400


def test_init_creates_yaml(tmp_path, runner):
    """ainfera init should create ainfera.yaml."""
    os.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("langchain==0.3.1\n")
    result = runner.invoke(main, ["init", "--name", "test-agent"])
    assert result.exit_code == 0
    assert (tmp_path / "ainfera.yaml").exists()


def test_init_refuses_overwrite(tmp_path, runner):
    """ainfera init should refuse to overwrite existing config."""
    os.chdir(tmp_path)
    (tmp_path / "ainfera.yaml").write_text("name: existing\n")
    result = runner.invoke(main, ["init"])
    assert result.exit_code != 0


def test_init_force_overwrite(tmp_path, runner):
    """ainfera init --force should overwrite existing config."""
    os.chdir(tmp_path)
    (tmp_path / "ainfera.yaml").write_text("name: existing\n")
    (tmp_path / "requirements.txt").write_text("langchain>=0.3\n")
    result = runner.invoke(main, ["init", "--force", "--name", "new-agent"])
    assert result.exit_code == 0
    content = (tmp_path / "ainfera.yaml").read_text()
    assert "new-agent" in content


def test_init_json_output(tmp_path, runner):
    """ainfera --json init should produce valid JSON."""
    os.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("crewai>=0.28\n")
    result = runner.invoke(main, ["--json", "init", "--name", "json-test"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["framework"] == "crewai"
    assert data["config"]["name"] == "json-test"
