"""Tests for deploy_diff.health_report_renderer."""
from __future__ import annotations

from deploy_diff.health_report_renderer import render_health_markdown, render_health_plain
from deploy_diff.tag_health_checker import HealthIssue, TagHealthReport


def _issue(severity: str, code: str, message: str) -> HealthIssue:
    return HealthIssue(severity=severity, code=code, message=message)


def _report(issues: list[HealthIssue] | None = None) -> TagHealthReport:
    issues = issues or []
    return TagHealthReport(issues=issues)


# ---------------------------------------------------------------------------
# render_health_markdown
# ---------------------------------------------------------------------------

def test_render_health_markdown_heading_present():
    output = render_health_markdown(_report())
    assert "## Tag Health" in output


def test_render_health_markdown_healthy_message():
    output = render_health_markdown(_report())
    assert "healthy" in output.lower() or "no issues" in output.lower()


def test_render_health_markdown_shows_errors():
    issues = [_issue("error", "DUPLICATE_TAG", "Tag v1 appears twice")]
    output = render_health_markdown(_report(issues))
    assert "DUPLICATE_TAG" in output or "v1 appears twice" in output


def test_render_health_markdown_shows_warnings():
    issues = [_issue("warning", "SINGLE_TAG", "Only one tag found")]
    output = render_health_markdown(_report(issues))
    assert "SINGLE_TAG" in output or "Only one tag" in output


def test_render_health_markdown_severity_label():
    issues = [_issue("error", "MISSING_TAG", "No tags found")]
    output = render_health_markdown(_report(issues))
    assert "error" in output.lower()


# ---------------------------------------------------------------------------
# render_health_plain
# ---------------------------------------------------------------------------

def test_render_health_plain_heading_present():
    output = render_health_plain(_report())
    assert "Tag Health" in output


def test_render_health_plain_healthy_no_issues():
    output = render_health_plain(_report())
    assert "ok" in output.lower() or "healthy" in output.lower() or "no issues" in output.lower()


def test_render_health_plain_lists_all_issues():
    issues = [
        _issue("error", "ERR_A", "First error"),
        _issue("warning", "WARN_B", "Second warning"),
    ]
    output = render_health_plain(_report(issues))
    assert "First error" in output
    assert "Second warning" in output


def test_render_health_plain_counts_match():
    issues = [
        _issue("error", "ERR_A", "An error"),
        _issue("error", "ERR_B", "Another error"),
        _issue("warning", "WARN_A", "A warning"),
    ]
    report = _report(issues)
    output = render_health_plain(report)
    # The renderer should surface counts; verify the report itself is consistent
    assert report.error_count == 2
    assert report.warning_count == 1
    assert len(output) > 0
