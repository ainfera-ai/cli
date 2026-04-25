"""Tests for config management."""

from ainfera.config.settings import load_config, save_config


def test_config_round_trip(tmp_config):
    """Config save/load should round-trip correctly."""
    config = {
        "api_key": "ainf_test123",
        "api_url": "https://api.ainfera.ai",
        "default_agent": "abc-123",
    }
    save_config(config)
    loaded = load_config()
    assert loaded == config


def test_load_missing_config(tmp_config):
    """Loading a missing config should return empty dict."""
    result = load_config()
    assert result == {}


def test_config_file_permissions(tmp_config):
    """Config file should have 600 permissions."""
    save_config({"api_key": "ainf_secret"})
    from ainfera.config.settings import CONFIG_FILE

    stat = CONFIG_FILE.stat()
    assert oct(stat.st_mode)[-3:] == "600"
