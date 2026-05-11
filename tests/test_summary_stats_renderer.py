"""Tests for deploy_diff.summary_stats_renderer."""
from __future__ import annotations

import pytest

from deploy_diff.diff_stats import DiffStats
from deploy_diff.summary_stats_renderer import render_stats_markdown, render_stats_plain


def _stats(
    commits: int = 0,
    config: int = 0,
    by_status: dict | None = None,
) -> DiffStats:
    return DiffStats(
        total_commits=commits,
        total_config_changes=config,
        by_status=by_status or {},
    )


def test_render_stats_markdown_contains_heading():
    result = render_stats_markdown(_stats())
    assert "##" in result or "**" in result or "Stats" in result


def test_render_stats_markdown_shows_commit_count():
    result = render_stats_markdown(_stats(commits=7))
    assert "7" in result


def test_render_stats_markdown_shows_config_count():
    result = render_stats_markdown(_stats(config=4))
    assert "4" in result


def test_render_stats_markdown_shows_by_status():
    result = render_stats_markdown(_stats(config=3, by_status={"M": 2, "A": 1}))
    assert "M" in result
    assert "A" in result
    assert "2" in result
    assert "1" in result


def test_render_stats_markdown_empty_by_status():
    result = render_stats_markdown(_stats(commits=1, config=0, by_status={}))
    assert isinstance(result, str)
    assert len(result) > 0


def test_render_stats_plain_contains_commit_count():
    result = render_stats_plain(_stats(commits=10))
    assert "10" in result


def test_render_stats_plain_contains_config_count():
    result = render_stats_plain(_stats(config=5))
    assert "5" in result


def test_render_stats_plain_shows_by_status():
    result = render_stats_plain(_stats(config=2, by_status={"D": 2}))
    assert "D" in result
    assert "2" in result


def test_render_stats_plain_no_markdown_symbols():
    result = render_stats_plain(_stats(commits=3, config=1))
    assert "##" not in result
    assert "**" not in result


def test_render_stats_plain_zero_values():
    result = render_stats_plain(_stats(commits=0, config=0))
    assert "0" in result
