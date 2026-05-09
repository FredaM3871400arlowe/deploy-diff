"""Tests for deploy_diff.multi_env_report."""

from unittest.mock import patch, MagicMock

from deploy_diff.tag_grouper import GroupConfig
from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.config_differ import ConfigChange
from deploy_diff.multi_env_report import (
    EnvReport,
    build_env_reports,
    render_multi_env_markdown,
    render_multi_env_plain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _entry(commits=None, changes=None):
    return ChangelogEntry(
        from_tag="v1",
        to_tag="v2",
        commits=commits or ["abc1234 Add thing"],
        config_changes=changes or [],
    )


def _report(env="prod", from_tag="v1", to_tag="v2", entry=None):
    return EnvReport(env=env, from_tag=from_tag, to_tag=to_tag, entry=entry or _entry())


_SIMPLE_CONFIG = GroupConfig(
    patterns={"prod": r"^prod-", "staging": r"^staging-"},
    default_group="other",
)


# ---------------------------------------------------------------------------
# build_env_reports
# ---------------------------------------------------------------------------

@patch("deploy_diff.multi_env_report.build_changelog_entry")
def test_build_env_reports_skips_empty_groups(mock_build):
    mock_build.return_value = _entry()
    tags = ["prod-1.0", "prod-2.0"]  # no staging tags
    reports = build_env_reports(tags, _SIMPLE_CONFIG)
    envs = [r.env for r in reports]
    assert "prod" in envs
    assert "staging" not in envs
    assert "other" not in envs


@patch("deploy_diff.multi_env_report.build_changelog_entry")
def test_build_env_reports_no_previous_tag(mock_build):
    tags = ["prod-1.0"]  # single tag — no previous
    reports = build_env_reports(tags, _SIMPLE_CONFIG)
    assert len(reports) == 1
    assert reports[0].from_tag is None
    assert reports[0].entry is None
    mock_build.assert_not_called()


@patch("deploy_diff.multi_env_report.build_changelog_entry")
def test_build_env_reports_calls_build_for_each_pair(mock_build):
    mock_build.return_value = _entry()
    tags = ["prod-1.0", "prod-2.0", "staging-1.0", "staging-2.0"]
    reports = build_env_reports(tags, _SIMPLE_CONFIG)
    assert mock_build.call_count == 2
    envs = {r.env for r in reports}
    assert envs == {"prod", "staging"}


# ---------------------------------------------------------------------------
# render_multi_env_markdown
# ---------------------------------------------------------------------------

def test_render_multi_env_markdown_contains_env_name():
    reports = [_report(env="prod")]
    output = render_multi_env_markdown(reports)
    assert "Environment: prod" in output


def test_render_multi_env_markdown_baseline_note():
    report = EnvReport(env="staging", from_tag=None, to_tag="v1.0", entry=None)
    output = render_multi_env_markdown([report])
    assert "baseline" in output.lower()


def test_render_multi_env_markdown_separator_between_envs():
    reports = [_report(env="prod"), _report(env="staging")]
    output = render_multi_env_markdown(reports)
    assert "---" in output


# ---------------------------------------------------------------------------
# render_multi_env_plain
# ---------------------------------------------------------------------------

def test_render_multi_env_plain_contains_env_name():
    reports = [_report(env="prod")]
    output = render_multi_env_plain(reports)
    assert "prod" in output


def test_render_multi_env_plain_baseline_note():
    report = EnvReport(env="prod", from_tag=None, to_tag="v1.0", entry=None)
    output = render_multi_env_plain([report])
    assert "baseline" in output.lower()
