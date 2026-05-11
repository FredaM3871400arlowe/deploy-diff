"""Tests for deploy_diff.tag_diff_summary."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest

from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.config_differ import ConfigChange
from deploy_diff.diff_stats import DiffStats
from deploy_diff.tag_comparator import ComparisonResult
from deploy_diff.tag_diff_summary import (
    TagDiffSummary,
    build_tag_diff_summary,
    format_tag_diff_summary,
)


def _change(path: str = "config/app.yaml", status: str = "M") -> ConfigChange:
    return ConfigChange(path=path, status=status, diff="-old\n+new")


def _entry(commits=None, changes=None) -> ChangelogEntry:
    return ChangelogEntry(
        from_tag="v1.0",
        to_tag="v1.1",
        commits=commits or ["abc123 feat: add thing"],
        config_changes=changes or [],
    )


def _stats(commits=2, config=1) -> DiffStats:
    return DiffStats(total_commits=commits, total_config_changes=config, by_status={})


def _comparison(delta=2, drift=True) -> ComparisonResult:
    cr = MagicMock(spec=ComparisonResult)
    cr.net_commit_delta.return_value = delta
    cr.has_config_drift.return_value = drift
    return cr


def test_tag_diff_summary_properties():
    summary = TagDiffSummary(
        from_tag="v1.0",
        to_tag="v1.1",
        stats=_stats(commits=3, config=2),
        comparison=_comparison(delta=1, drift=True),
        entries=[_entry()],
    )
    assert summary.commit_count == 3
    assert summary.config_change_count == 2
    assert summary.net_delta == 1
    assert summary.has_drift is True


def test_tag_diff_summary_no_drift():
    summary = TagDiffSummary(
        from_tag="v1.0",
        to_tag="v1.1",
        stats=_stats(commits=0, config=0),
        comparison=_comparison(delta=0, drift=False),
    )
    assert summary.has_drift is False
    assert summary.net_delta == 0


def test_format_tag_diff_summary_contains_tags():
    summary = TagDiffSummary(
        from_tag="v1.0",
        to_tag="v1.1",
        stats=_stats(commits=5, config=3),
        comparison=_comparison(delta=2, drift=True),
    )
    result = format_tag_diff_summary(summary)
    assert "v1.0" in result
    assert "v1.1" in result
    assert "5" in result
    assert "3" in result
    assert "+2" in result
    assert "yes" in result


def test_format_tag_diff_summary_no_drift_label():
    summary = TagDiffSummary(
        from_tag="v2.0",
        to_tag="v2.1",
        stats=_stats(commits=1, config=0),
        comparison=_comparison(delta=-1, drift=False),
    )
    result = format_tag_diff_summary(summary)
    assert "no" in result
    assert "-1" in result


@patch("deploy_diff.tag_diff_summary.compare_tags")
@patch("deploy_diff.tag_diff_summary.compute_stats")
def test_build_tag_diff_summary(mock_stats, mock_compare):
    entries = [_entry()]
    mock_stats.return_value = _stats()
    mock_compare.return_value = _comparison()

    result = build_tag_diff_summary("v1.0", "v1.1", entries, repo_path="/repo")

    assert result.from_tag == "v1.0"
    assert result.to_tag == "v1.1"
    assert result.entries == entries
    mock_stats.assert_called_once_with(entries)
    mock_compare.assert_called_once_with("v1.0", "v1.1", entries, repo_path="/repo")
