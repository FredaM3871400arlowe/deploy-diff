"""Tests for deploy_diff.cli (including --output / --append / --quiet flags)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from deploy_diff.cli import parse_args, run
from deploy_diff.git_tagger import TagRange
from deploy_diff.changelog_formatter import ChangelogEntry


def _make_tag_range(from_tag: str = "v1.0", to_tag: str = "v1.1") -> TagRange:
    return TagRange(from_tag=from_tag, to_tag=to_tag)


def _make_entry(from_tag: str = "v1.0", to_tag: str = "v1.1") -> ChangelogEntry:
    return ChangelogEntry(from_tag=from_tag, to_tag=to_tag, commits=[], config_changes=[])


def test_parse_args_defaults() -> None:
    args = parse_args(["v1.0"])
    assert args.from_tag == "v1.0"
    assert args.to_tag == "HEAD"
    assert args.repo == "."
    assert args.output is None
    assert args.append is False
    assert args.quiet is False
    assert args.no_config is False


def test_parse_args_explicit_to_tag() -> None:
    args = parse_args(["v1.0", "v1.1"])
    assert args.to_tag == "v1.1"


def test_parse_args_with_flags() -> None:
    args = parse_args(["v1.0", "v1.1", "--output", "out.md", "--append", "--quiet", "--no-config"])
    assert args.output == "out.md"
    assert args.append is True
    assert args.quiet is True
    assert args.no_config is True


def test_run_writes_to_stdout(capsys: pytest.CaptureFixture) -> None:
    entry = _make_entry()
    with patch("deploy_diff.cli.get_tag_range", return_value=_make_tag_range()), \
         patch("deploy_diff.cli.collect_config_changes", return_value=[]), \
         patch("deploy_diff.cli.build_changelog_entry", return_value=entry), \
         patch("deploy_diff.cli.format_changelog", return_value="## changelog\n"):
        result = run(["v1.0", "v1.1"])
    assert result == 0
    captured = capsys.readouterr()
    assert "## changelog" in captured.out


def test_run_writes_to_file(tmp_path: Path) -> None:
    out_file = tmp_path / "out.md"
    entry = _make_entry()
    with patch("deploy_diff.cli.get_tag_range", return_value=_make_tag_range()), \
         patch("deploy_diff.cli.collect_config_changes", return_value=[]), \
         patch("deploy_diff.cli.build_changelog_entry", return_value=entry), \
         patch("deploy_diff.cli.format_changelog", return_value="## changelog\n"):
        result = run(["v1.0", "v1.1", "--output", str(out_file), "--quiet"])
    assert result == 0
    assert out_file.read_text(encoding="utf-8") == "## changelog\n"


def test_run_returns_1_on_git_error(capsys: pytest.CaptureFixture) -> None:
    with patch("deploy_diff.cli.get_tag_range", side_effect=RuntimeError("bad tag")):
        result = run(["bad", "tags"])
    assert result == 1
    assert "bad tag" in capsys.readouterr().err


def test_run_skips_config_with_no_config_flag() -> None:
    entry = _make_entry()
    with patch("deploy_diff.cli.get_tag_range", return_value=_make_tag_range()), \
         patch("deploy_diff.cli.collect_config_changes") as mock_cc, \
         patch("deploy_diff.cli.build_changelog_entry", return_value=entry), \
         patch("deploy_diff.cli.format_changelog", return_value=""), \
         patch("deploy_diff.cli.write_output"):
        run(["v1.0", "v1.1", "--no-config"])
    mock_cc.assert_not_called()
