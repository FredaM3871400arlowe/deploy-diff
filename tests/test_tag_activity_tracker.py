"""Tests for deploy_diff.tag_activity_tracker."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from deploy_diff.tag_activity_tracker import (
    TagActivity,
    format_activity_table,
    get_tag_activity,
    track_activity,
)


def _result(stdout: str = "", returncode: int = 0) -> SimpleNamespace:
    return SimpleNamespace(stdout=stdout, returncode=returncode)


# ---------------------------------------------------------------------------
# TagActivity helpers
# ---------------------------------------------------------------------------

def test_unique_authors_deduplicates():
    a = TagActivity(tag="v2", commit_count=3, authors=["alice", "bob", "alice"])
    assert a.unique_authors == ["alice", "bob"]


def test_author_count_reflects_unique():
    a = TagActivity(tag="v2", commit_count=4, authors=["alice", "alice", "bob", "carol"])
    assert a.author_count == 3


# ---------------------------------------------------------------------------
# get_tag_activity
# ---------------------------------------------------------------------------

def _make_log_side_effect(authors_out: str, dates_out: str):
    """Return a side_effect callable that alternates author / date responses."""
    calls = [_result(authors_out), _result(dates_out)]
    it = iter(calls)
    return lambda _args: next(it)


def test_get_tag_activity_populates_fields():
    authors_out = "alice\nbob\nalice"
    dates_out = "2024-06-01 10:00:00 +0000\n2024-05-30 08:00:00 +0000\n2024-05-29 07:00:00 +0000"
    with patch(
        "deploy_diff.tag_activity_tracker.run_git",
        side_effect=_make_log_side_effect(authors_out, dates_out),
    ):
        activity = get_tag_activity("v1", "v2")

    assert activity.tag == "v2"
    assert activity.commit_count == 3
    assert activity.authors == ["alice", "bob", "alice"]
    assert activity.first_commit == "2024-05-29 07:00:00 +0000"
    assert activity.last_commit == "2024-06-01 10:00:00 +0000"


def test_get_tag_activity_empty_range():
    with patch(
        "deploy_diff.tag_activity_tracker.run_git", return_value=_result("")
    ):
        activity = get_tag_activity("v1", "v1")

    assert activity.commit_count == 0
    assert activity.authors == []
    assert activity.first_commit is None
    assert activity.last_commit is None


def test_get_tag_activity_git_failure():
    with patch(
        "deploy_diff.tag_activity_tracker.run_git", return_value=_result("", returncode=1)
    ):
        activity = get_tag_activity("v1", "v2")

    assert activity.commit_count == 0


# ---------------------------------------------------------------------------
# track_activity
# ---------------------------------------------------------------------------

def test_track_activity_requires_at_least_two_tags():
    assert track_activity([]) == []
    assert track_activity(["v1"]) == []


def test_track_activity_returns_one_per_pair():
    fake_activity = TagActivity(tag="v2", commit_count=1, authors=["alice"])
    with patch(
        "deploy_diff.tag_activity_tracker.get_tag_activity", return_value=fake_activity
    ) as mock_fn:
        results = track_activity(["v1", "v2", "v3"])

    assert len(results) == 2
    assert mock_fn.call_count == 2


# ---------------------------------------------------------------------------
# format_activity_table
# ---------------------------------------------------------------------------

def test_format_activity_table_empty():
    assert "No activity" in format_activity_table([])


def test_format_activity_table_contains_tag_name():
    activities = [
        TagActivity(
            tag="v1.2.3",
            commit_count=5,
            authors=["alice", "bob"],
            last_commit="2024-06-01 10:00:00 +0000",
        )
    ]
    table = format_activity_table(activities)
    assert "v1.2.3" in table
    assert "5" in table
    assert "2" in table  # unique author count
