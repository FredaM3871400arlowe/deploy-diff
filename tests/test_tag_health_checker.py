"""Tests for tag_health_checker and health_report_renderer."""
import pytest

from deploy_diff.tag_health_checker import (
    TagHealthReport,
    HealthIssue,
    check_tag_health,
    _check_duplicates,
    _check_empty,
    _check_single_tag,
)
from deploy_diff.health_report_renderer import render_health_markdown, render_health_plain
from deploy_diff.tag_sorter import SortConfig


# ---------------------------------------------------------------------------
# Unit tests – individual checks
# ---------------------------------------------------------------------------

def test_check_empty_returns_warning_for_empty_list():
    issues = _check_empty([])
    assert len(issues) == 1
    assert issues[0].level == "warning"


def test_check_empty_returns_nothing_for_non_empty():
    assert _check_empty(["v1.0"]) == []


def test_check_duplicates_detects_duplicate():
    issues = _check_duplicates(["v1.0", "v2.0", "v1.0"])
    assert len(issues) == 1
    assert issues[0].level == "error"
    assert "v1.0" in issues[0].message


def test_check_duplicates_no_issue_for_unique_tags():
    assert _check_duplicates(["v1.0", "v2.0", "v3.0"]) == []


def test_check_single_tag_warns():
    issues = _check_single_tag(["v1.0"])
    assert len(issues) == 1
    assert issues[0].level == "warning"


def test_check_single_tag_no_issue_for_multiple():
    assert _check_single_tag(["v1.0", "v2.0"]) == []


# ---------------------------------------------------------------------------
# Integration tests – check_tag_health
# ---------------------------------------------------------------------------

def test_check_tag_health_empty_list():
    report = check_tag_health([])
    assert not report.healthy  # empty is not an error but healthy checks errors only
    # actually empty → only warning, so healthy should be True
    assert report.healthy
    assert report.warning_count == 1


def test_check_tag_health_clean_sorted_tags():
    tags = ["v1.0.0", "v1.1.0", "v2.0.0"]
    cfg = SortConfig(strategy="semver")
    report = check_tag_health(tags, sort_config=cfg)
    assert report.healthy
    assert report.error_count == 0
    assert report.warning_count == 0


def test_check_tag_health_unsorted_tags_warns():
    tags = ["v2.0.0", "v1.0.0", "v1.1.0"]
    cfg = SortConfig(strategy="semver")
    report = check_tag_health(tags, sort_config=cfg)
    assert report.healthy  # warning only
    assert report.warning_count >= 1


def test_check_tag_health_duplicate_is_error():
    tags = ["v1.0", "v1.0", "v2.0"]
    report = check_tag_health(tags)
    assert not report.healthy
    assert report.error_count == 1


# ---------------------------------------------------------------------------
# Renderer tests
# ---------------------------------------------------------------------------

def _healthy_report() -> TagHealthReport:
    return TagHealthReport(tags=["v1.0", "v2.0"], issues=[])


def _unhealthy_report() -> TagHealthReport:
    return TagHealthReport(
        tags=["v1.0"],
        issues=[
            HealthIssue(level="warning", message="Only one tag present"),
            HealthIssue(level="error", message="Duplicate tag detected: 'v1.0'"),
        ],
    )


def test_render_health_markdown_healthy():
    md = render_health_markdown(_healthy_report())
    assert "Healthy" in md
    assert "No issues found" in md


def test_render_health_markdown_unhealthy_shows_issues():
    md = render_health_markdown(_unhealthy_report())
    assert "Unhealthy" in md
    assert "Only one tag present" in md
    assert "Duplicate tag detected" in md


def test_render_health_plain_healthy():
    plain = render_health_plain(_healthy_report())
    assert "HEALTHY" in plain
    assert "No issues found" in plain


def test_render_health_plain_shows_labels():
    plain = render_health_plain(_unhealthy_report())
    assert "[WARN]" in plain
    assert "[ERROR]" in plain
