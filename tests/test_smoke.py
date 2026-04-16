"""Smoke test — package imports cleanly and CLI entry point works."""
from click.testing import CliRunner


def test_import() -> None:
    import ainfera
    assert ainfera.__version__


def test_cli_help() -> None:
    from ainfera.cli import main
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "ainfera" in result.output.lower()


def test_cli_version() -> None:
    from ainfera.cli import main
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
