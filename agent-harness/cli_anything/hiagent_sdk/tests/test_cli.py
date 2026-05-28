from click.testing import CliRunner

from cli_anything.hiagent_sdk.hiagent_cli import cli


def test_root_help_does_not_advertise_project_option():
    result = CliRunner().invoke(cli, ["--help"])

    assert result.exit_code == 0, result.output
    assert "--project" not in result.output
    assert "-p" not in result.output


def test_project_option_is_rejected():
    result = CliRunner().invoke(cli, ["--project", "/tmp", "--version"])

    assert result.exit_code != 0
    assert "No such option" in result.output


def test_project_short_option_is_rejected():
    result = CliRunner().invoke(cli, ["-p", "/tmp", "--version"])

    assert result.exit_code != 0
    assert "No such option" in result.output
