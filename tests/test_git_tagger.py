"""Tests for deploy_diff.git_tagger module."""

import pytest
from unittest.mock import patch, MagicMock

from deploy_diff.git_tagger import (
    list_tags,
    resolve_commit,
    get_tag_range,
    get_commits_in_range,
    TagRange,
)


def make_run_result(stdout: str):
    m = MagicMock()
    m.stdout = stdout
    return m


@patch("deploy_diff.git_tagger.subprocess.run")
def test_list_tags_returns_sorted_list(mock_run):
    mock_run.return_value = make_run_result("v1.2.0\nv1.1.0\nv1.0.0\n")
    tags = list_tags("/repo")
    assert tags == ["v1.2.0", "v1.1.0", "v1.0.0"]
    mock_run.assert_called_once()


@patch("deploy_diff.git_tagger.subprocess.run")
def test_list_tags_empty(mock_run):
    mock_run.return_value = make_run_result("")
    assert list_tags("/repo") == []


@patch("deploy_diff.git_tagger.subprocess.run")
def test_resolve_commit(mock_run):
    sha = "abc123def456" * 3
    mock_run.return_value = make_run_result(sha)
    result = resolve_commit("v1.0.0", "/repo")
    assert result == sha


@patch("deploy_diff.git_tagger.resolve_commit")
def test_get_tag_range(mock_resolve):
    mock_resolve.side_effect = ["aaa111", "bbb222"]
    tr = get_tag_range("v1.0.0", "v1.1.0", "/repo")
    assert tr.from_tag == "v1.0.0"
    assert tr.to_tag == "v1.1.0"
    assert tr.from_commit == "aaa111"
    assert tr.to_commit == "bbb222"


@patch("deploy_diff.git_tagger.subprocess.run")
def test_get_commits_in_range(mock_run):
    log_output = (
        "abc123|feat: add login|Alice|2024-01-10\n"
        "def456|fix: crash on startup|Bob|2024-01-09\n"
    )
    mock_run.return_value = make_run_result(log_output)
    tr = TagRange("v1.0.0", "v1.1.0", "aaa", "bbb")
    commits = get_commits_in_range(tr, "/repo")
    assert len(commits) == 2
    assert commits[0]["sha"] == "abc123"
    assert commits[0]["subject"] == "feat: add login"
    assert commits[1]["author"] == "Bob"
