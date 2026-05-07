"""Tests for deploy_diff.diff_stats."""
from __future__ import annotations

import pytest

from deploy_diff.config_differ import ConfigChange
from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.diff_stats import (
    DiffStats,
    compute_stats,
    aggregate_stats,
    format_stats,
)


def _change(path: str, status: str) -> ConfigChange:
    return ConfigChange(path=path, status=status, diff="")


def _entry(commits=None, config_changes=None) -> ChangelogEntry:
    return ChangelogEntry(
        from_tag="v1.0",
        to_tag="v1.1",
        commits=commits or [],
        config_changes=config_changes or [],
    )


# ---------------------------------------------------------------------------
# DiffStats.has_changes
# ---------------------------------------------------------------------------

def test_has_changes_false_when_empty():
    assert DiffStats().has_changes is False


def test_has_changes_true_with_commits():
    assert DiffStats(total_commits=1).has_changes is True


def test_has_changes_true_with_config():
    assert DiffStats(total_config_changes=2).has_changes is True


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_compute_stats_empty_entry():
    stats = compute_stats(_entry())
    assert stats.total_commits == 0
    assert stats.total_config_changes == 0
    assert stats.added == stats.modified == stats.deleted == 0
    assert stats.config_files_changed == []


def test_compute_stats_counts_commits():
    entry = _entry(commits=["abc def", "123 ghi"])
    stats = compute_stats(entry)
    assert stats.total_commits == 2


def test_compute_stats_tallies_statuses():
    changes = [
        _change("config/a.yaml", "A"),
        _change("config/b.yaml", "M"),
        _change("config/c.yaml", "D"),
        _change("config/d.yaml", "M"),
    ]
    stats = compute_stats(_entry(config_changes=changes))
    assert stats.added == 1
    assert stats.modified == 2
    assert stats.deleted == 1
    assert stats.total_config_changes == 4


def test_compute_stats_unique_files():
    changes = [
        _change("config/a.yaml", "M"),
        _change("config/a.yaml", "M"),
        _change("config/b.yaml", "A"),
    ]
    stats = compute_stats(_entry(config_changes=changes))
    assert stats.config_files_changed == ["config/a.yaml", "config/b.yaml"]


# ---------------------------------------------------------------------------
# aggregate_stats
# ---------------------------------------------------------------------------

def test_aggregate_stats_sums_entries():
    e1 = _entry(commits=["a"], config_changes=[_change("x.yaml", "A")])
    e2 = _entry(commits=["b", "c"], config_changes=[_change("y.yaml", "D")])
    stats = aggregate_stats([e1, e2])
    assert stats.total_commits == 3
    assert stats.total_config_changes == 2
    assert stats.added == 1
    assert stats.deleted == 1
    assert set(stats.config_files_changed) == {"x.yaml", "y.yaml"}


def test_aggregate_stats_deduplicates_files():
    shared = _change("shared.yaml", "M")
    e1 = _entry(config_changes=[shared])
    e2 = _entry(config_changes=[shared])
    stats = aggregate_stats([e1, e2])
    assert stats.config_files_changed == ["shared.yaml"]


# ---------------------------------------------------------------------------
# format_stats
# ---------------------------------------------------------------------------

def test_format_stats_no_config_changes():
    s = DiffStats(total_commits=5)
    assert format_stats(s) == "5 commit(s), no config changes"


def test_format_stats_with_config_changes():
    s = DiffStats(total_commits=3, total_config_changes=4, added=1, modified=2, deleted=1)
    result = format_stats(s)
    assert "3 commit(s)" in result
    assert "4 config change(s)" in result
    assert "+1/-1/~2" in result
