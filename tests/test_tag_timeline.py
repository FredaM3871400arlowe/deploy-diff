"""Tests for deploy_diff.tag_timeline."""

from unittest.mock import patch, MagicMock

from deploy_diff.tag_timeline import (
    TimelineEntry,
    TagTimeline,
    _get_commit_info,
    _count_commits_since_previous,
    build_timeline,
    render_timeline_plain,
)
from deploy_diff.tag_annotator import TagAnnotation


def _make_annotation(message: str = "") -> TagAnnotation:
    return TagAnnotation(tag="v1.0", is_annotated=True, tagger="bot", date="2024-01-01", message=message)


@patch("deploy_diff.tag_timeline.run_git", return_value="abc123\x1fAlice\x1f2024-06-01 10:00:00 +0000")
def test_get_commit_info_parses_fields(mock_git):
    commit, author, date = _get_commit_info("v1.0")
    assert commit == "abc123"
    assert author == "Alice"
    assert date == "2024-06-01 10:00:00 +0000"
    mock_git.assert_called_once_with(["log", "-1", "--format=%H%x1f%an%x1f%ai", "v1.0"])


@patch("deploy_diff.tag_timeline.run_git", return_value="bad output")
def test_get_commit_info_malformed_returns_empty(mock_git):
    commit, author, date = _get_commit_info("v1.0")
    assert commit == ""
    assert author == ""
    assert date == ""


@patch("deploy_diff.tag_timeline.run_git", return_value="5\n")
def test_count_commits_since_previous(mock_git):
    count = _count_commits_since_previous("v2.0", "v1.0")
    assert count == 5
    mock_git.assert_called_once_with(["rev-list", "--count", "v1.0..v2.0"])


def test_count_commits_no_previous_returns_zero():
    count = _count_commits_since_previous("v1.0", None)
    assert count == 0


@patch("deploy_diff.tag_timeline.run_git", return_value="not-a-number")
def test_count_commits_invalid_output_returns_zero(mock_git):
    count = _count_commits_since_previous("v2.0", "v1.0")
    assert count == 0


@patch("deploy_diff.tag_timeline.get_tag_annotation")
@patch("deploy_diff.tag_timeline.run_git")
def test_build_timeline_creates_entries(mock_git, mock_annotation):
    mock_git.side_effect = [
        "aaa\x1fAlice\x1f2024-01-01",
        "bbb\x1fBob\x1f2024-02-01",
        "3",
    ]
    mock_annotation.return_value = _make_annotation("release note")

    timeline = build_timeline(["v1.0", "v2.0"])

    assert len(timeline) == 2
    assert timeline.entries[0].tag == "v1.0"
    assert timeline.entries[1].tag == "v2.0"
    assert timeline.entries[1].commit_count == 3


@patch("deploy_diff.tag_timeline.get_tag_annotation")
@patch("deploy_diff.tag_timeline.run_git", return_value="abc\x1fDev\x1f2024-03-01")
def test_build_timeline_no_annotations(mock_git, mock_annotation):
    timeline = build_timeline(["v1.0"], include_annotations=False)
    assert timeline.entries[0].annotation is None
    mock_annotation.assert_not_called()


def test_render_timeline_plain_contains_tag():
    entry = TimelineEntry(
        tag="v3.1",
        commit="deadbeef1234",
        author="Carol",
        date="2024-05-01",
        annotation=_make_annotation("hotfix"),
        commit_count=7,
    )
    timeline = TagTimeline(entries=[entry])
    output = render_timeline_plain(timeline)

    assert "v3.1" in output
    assert "deadbeef" in output
    assert "Carol" in output
    assert "+7 since previous" in output
    assert "hotfix" in output


def test_render_timeline_plain_no_commits_hides_count():
    entry = TimelineEntry(tag="v1.0", commit="abc", author="Dev", date="2024-01-01", commit_count=0)
    timeline = TagTimeline(entries=[entry])
    output = render_timeline_plain(timeline)
    assert "commits" not in output
