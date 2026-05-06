"""Tests for the deploy_diff.cli module."""

from unittest.mock import patch, MagicMock
import pytest

from deploy_diff.cli import parse_args, run
from deploy_diff.git_tagger import TagRange
from deploy_diff.changelog_formatter import ChangelogEntry


def _make_tag_range(from_tag="v1.0", to_tag="v1.1"):
    return TagRange(from_tag=from_tag, to_tag=to_tag)


def _make_entry():
    return ChangelogEntry(
        from_tag="v1.0",
        to_tag="v1.1",
        commits=["abc1234 Fix bug"],
        config_changes=[],
    )


def test_parse_args_defaults():
    args = parse_args(["v1.0"])
    assert args.from_tag == "v1.0"
    assert args.to_tag == "HEAD"
    assert args.repo == "."
    assert args.output is None
    assert args.no_config is False


def test_parse_args_explicit_to_tag():
    args = parse_args(["v1.0", "v1.1"])
    assert args.from_tag == "v1.0"
    assert args.to_tag == "v1.1"


def test_parse_args_with_flags():
    args = parse_args(["v1.0", "v1.1", "--repo", "/tmp/repo", "--no-config", "-o", "out.md"])
    assert args.repo == "/tmp/repo"
    assert args.no_config is True
    assert args.output == "out.md"


@patch("deploy_diff.cli.format_changelog", return_value="## Changelog\n")
@patch("deploy_diff.cli.build_changelog_entry")
@patch("deploy_diff.cli.collect_config_changes", return_value=[])
@patch("deploy_diff.cli.get_tag_range")
def test_run_prints_to_stdout(mock_get_tag_range, mock_collect, mock_build, mock_format, capsys):
    mock_get_tag_range.return_value = _make_tag_range()
    mock_build.return_value = _make_entry()

    result = run(["v1.0", "v1.1"])

    assert result == 0
    captured = capsys.readouterr()
    assert "Changelog" in captured.out


@patch("deploy_diff.cli.get_tag_range", side_effect=ValueError("unknown tag"))
def test_run_returns_1_on_value_error(mock_get_tag_range, capsys):
    result = run(["bad-tag"])
    assert result == 1
    captured = capsys.readouterr()
    assert "error" in captured.err


@patch("deploy_diff.cli.format_changelog", return_value="## Changelog\n")
@patch("deploy_diff.cli.build_changelog_entry")
@patch("deploy_diff.cli.collect_config_changes", return_value=[])
@patch("deploy_diff.cli.get_tag_range")
def test_run_no_config_skips_collect(mock_get_tag_range, mock_collect, mock_build, mock_format):
    mock_get_tag_range.return_value = _make_tag_range()
    mock_build.return_value = _make_entry()

    run(["v1.0", "v1.1", "--no-config"])

    mock_collect.assert_not_called()


@patch("deploy_diff.cli.format_changelog", return_value="output content\n")
@patch("deploy_diff.cli.build_changelog_entry")
@patch("deploy_diff.cli.collect_config_changes", return_value=[])
@patch("deploy_diff.cli.get_tag_range")
def test_run_writes_to_file(mock_get_tag_range, mock_collect, mock_build, mock_format, tmp_path):
    mock_get_tag_range.return_value = _make_tag_range()
    mock_build.return_value = _make_entry()
    out_file = tmp_path / "changelog.md"

    result = run(["v1.0", "v1.1", "--output", str(out_file)])

    assert result == 0
    assert out_file.read_text(encoding="utf-8") == "output content\n"
