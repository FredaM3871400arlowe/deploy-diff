"""Tests for deploy_diff.tag_annotator."""

from unittest.mock import patch, MagicMock

import pytest

from deploy_diff.tag_annotator import (
    TagAnnotation,
    _is_annotated_tag,
    get_tag_annotation,
    annotate_tags,
    format_annotation_summary,
)


def _make_result(stdout: str) -> MagicMock:
    r = MagicMock()
    r.stdout = stdout
    return r


_LOG_OUTPUT = "abc1234\nAlice\nalice@example.com\n2024-06-01 12:00:00 +0000\nDeploy v1.2.3\n"


@patch("deploy_diff.tag_annotator.run_git")
def test_is_annotated_tag_true(mock_run):
    mock_run.return_value = _make_result("tag\n")
    assert _is_annotated_tag("v1.0.0") is True
    mock_run.assert_called_once_with(["cat-file", "-t", "refs/tags/v1.0.0"])


@patch("deploy_diff.tag_annotator.run_git")
def test_is_annotated_tag_false_for_commit(mock_run):
    mock_run.return_value = _make_result("commit\n")
    assert _is_annotated_tag("v1.0.0") is False


@patch("deploy_diff.tag_annotator.run_git")
def test_get_tag_annotation_returns_dataclass(mock_run):
    mock_run.side_effect = [
        _make_result("tag\n"),        # cat-file call
        _make_result(_LOG_OUTPUT),    # git log call
    ]
    ann = get_tag_annotation("v1.2.3")
    assert ann.tag == "v1.2.3"
    assert ann.commit_hash == "abc1234"
    assert ann.author_name == "Alice"
    assert ann.author_email == "alice@example.com"
    assert ann.tag_date == "2024-06-01 12:00:00 +0000"
    assert ann.subject == "Deploy v1.2.3"
    assert ann.is_annotated is True


@patch("deploy_diff.tag_annotator.run_git")
def test_get_tag_annotation_lightweight(mock_run):
    mock_run.side_effect = [
        _make_result("commit\n"),
        _make_result(_LOG_OUTPUT),
    ]
    ann = get_tag_annotation("v1.2.3")
    assert ann.is_annotated is False


@patch("deploy_diff.tag_annotator.run_git")
def test_get_tag_annotation_raises_on_bad_output(mock_run):
    mock_run.side_effect = [
        _make_result("tag\n"),
        _make_result("only-one-line\n"),
    ]
    with pytest.raises(ValueError, match="Unexpected git log output"):
        get_tag_annotation("v1.2.3")


@patch("deploy_diff.tag_annotator.get_tag_annotation")
def test_annotate_tags_returns_list(mock_get):
    ann = TagAnnotation("v1", "abc", "Bob", "b@b.com", "2024-01-01", "init", False)
    mock_get.return_value = ann
    result = annotate_tags(["v1", "v2"])
    assert len(result) == 2
    assert mock_get.call_count == 2


def test_format_annotation_summary_annotated():
    ann = TagAnnotation("v2.0", "deadbeef", "Carol", "c@c.com", "2024-03-15", "Release", True)
    summary = format_annotation_summary(ann)
    assert "v2.0" in summary
    assert "annotated" in summary
    assert "Carol" in summary
    assert "Release" in summary


def test_format_annotation_summary_lightweight():
    ann = TagAnnotation("v1.0", "cafebabe", "Dave", "d@d.com", "2024-01-01", "Init", False)
    summary = format_annotation_summary(ann)
    assert "lightweight" in summary
