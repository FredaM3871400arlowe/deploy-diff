"""Tests for deploy_diff.changelog_formatter."""

from unittest.mock import patch, MagicMock

from deploy_diff.changelog_formatter import (
    ChangelogEntry,
    build_changelog_entry,
    format_changelog,
    get_commits_between,
)
from deploy_diff.config_differ import ConfigChange
from deploy_diff.git_tagger import TagRange


def make_run_result(stdout: str) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    return result


TAG_RANGE = TagRange(start="v1.0.0", end="v1.1.0")


@patch("deploy_diff.changelog_formatter.run_git")
def test_get_commits_between_returns_lines(mock_run_git):
    mock_run_git.return_value = make_run_result(
        "abc1234 Fix login bug\ndef5678 Add feature flag\n"
    )
    commits = get_commits_between(TAG_RANGE)
    assert commits == ["abc1234 Fix login bug", "def5678 Add feature flag"]
    mock_run_git.assert_called_once_with(
        ["log", "--oneline", "--no-merges", "v1.0.0..v1.1.0"], cwd="."
    )


@patch("deploy_diff.changelog_formatter.run_git")
def test_get_commits_between_empty(mock_run_git):
    mock_run_git.return_value = make_run_result("")
    commits = get_commits_between(TAG_RANGE)
    assert commits == []


@patch("deploy_diff.changelog_formatter.run_git")
def test_get_commits_between_strips_trailing_whitespace(mock_run_git):
    """Ensure lines with extra whitespace are stripped cleanly."""
    mock_run_git.return_value = make_run_result(
        "abc1234 Fix login bug  \ndef5678 Add feature flag\t\n"
    )
    commits = get_commits_between(TAG_RANGE)
    assert commits == ["abc1234 Fix login bug", "def5678 Add feature flag"]


def test_format_changelog_with_changes():
    entry = ChangelogEntry(
        tag_range=TAG_RANGE,
        commits=["abc1234 Fix login bug"],
        config_changes=[
            ConfigChange(path="config/settings.yaml", status="M", diff="-old\n+new"),
            ConfigChange(path="config/feature.env", status="A", diff=""),
        ],
    )
    output = format_changelog(entry)
    assert "v1.0.0 → v1.1.0" in output
    assert "abc1234 Fix login bug" in output
    assert "Modified" in output
    assert "config/settings.yaml" in output
    assert "Added" in output
    assert "config/feature.env" in output


def test_format_changelog_no_commits_no_changes():
    entry = ChangelogEntry(
        tag_range=TAG_RANGE,
        commits=[],
        config_changes=[],
    )
    output = format_changelog(entry)
    assert "_No commits found._" in output
    assert "_No config file changes detected._" in output


def test_format_changelog_includes_diff_when_requested():
    entry = ChangelogEntry(
        tag_range=TAG_RANGE,
        commits=[],
        config_changes=[
            ConfigChange(path="config/app.yaml", status="M", diff="-foo\n+bar"),
        ],
    )
    output = format_changelog(entry, include_diff=True)
    assert "```diff" in output
    assert "-foo" in output
    assert "+bar" in output


def test_format_changelog_excludes_diff_by_default():
    """Verify that diff blocks are not shown unless include_diff=True."""
    entry = ChangelogEntry(
        tag_range=TAG_RANGE,
        commits=[],
        config_changes=[
            ConfigChange(path="config/app.yaml", status="M", diff="-foo\n+bar"),
        ],
    )
    output = format_changelog(entry)
    assert "```diff" not in output


@patch("deploy_diff.changelog_formatter.run_git")
def test_build_changelog_entry(mock_run_git):
    mock_run_git.return_value = make_run_result("abc Fix thing\n")
    changes = [ConfigChange(path="config/db.yaml", status="M", diff="")]
    entry = build_changelog_entry(TAG_RANGE, changes, repo_path="/repo")
    assert entry.tag_range == TAG_RANGE
    assert entry.commits == ["abc Fix thing"]
    assert entry.config_changes == changes
