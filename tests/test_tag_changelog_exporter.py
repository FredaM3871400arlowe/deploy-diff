"""Tests for tag_changelog_exporter and export_renderer."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from deploy_diff.tag_changelog_exporter import (
    ChangelogExport,
    ExportConfig,
    TagPairExport,
    _make_consecutive_pairs,
    build_changelog_export,
)
from deploy_diff.export_renderer import render_export_markdown, render_export_plain
from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.config_differ import ConfigChange


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _entry(commits=None, changes=None):
    return ChangelogEntry(
        commits=commits or [],
        config_changes=changes or [],
    )


def _pair(from_tag="v1.0", to_tag="v1.1", commits=None, changes=None):
    return TagPairExport(
        from_tag=from_tag,
        to_tag=to_tag,
        entry=_entry(commits=commits, changes=changes),
    )


# ---------------------------------------------------------------------------
# _make_consecutive_pairs
# ---------------------------------------------------------------------------

def test_make_consecutive_pairs_empty():
    assert _make_consecutive_pairs([]) == []


def test_make_consecutive_pairs_single():
    assert _make_consecutive_pairs(["v1"]) == []


def test_make_consecutive_pairs_multiple():
    result = _make_consecutive_pairs(["v1", "v2", "v3"])
    assert result == [("v1", "v2"), ("v2", "v3")]


# ---------------------------------------------------------------------------
# ChangelogExport totals
# ---------------------------------------------------------------------------

def test_changelog_export_totals():
    change = ConfigChange(path="app.yaml", status="M", diff="-a\n+b")
    export = ChangelogExport(
        pairs=[
            _pair(commits=["abc def", "123 ghi"], changes=[change]),
            _pair(commits=["fff msg"], changes=[]),
        ]
    )
    assert export.total_commits == 3
    assert export.total_config_changes == 1


def test_changelog_export_empty_totals():
    export = ChangelogExport()
    assert export.total_commits == 0
    assert export.total_config_changes == 0


# ---------------------------------------------------------------------------
# build_changelog_export (integration-style with mocks)
# ---------------------------------------------------------------------------

@patch("deploy_diff.tag_changelog_exporter.build_changelog_entry")
@patch("deploy_diff.tag_changelog_exporter.validate_tags")
def test_build_changelog_export_skips_invalid(mock_validate, mock_build):
    mock_validate.return_value = MagicMock(__bool__=lambda s: False)
    export = build_changelog_export(["v1", "v2"])
    mock_build.assert_not_called()
    assert export.pairs == []


@patch("deploy_diff.tag_changelog_exporter.build_changelog_entry")
@patch("deploy_diff.tag_changelog_exporter.validate_tags")
def test_build_changelog_export_max_pairs(mock_validate, mock_build):
    mock_validate.return_value = MagicMock(__bool__=lambda s: True)
    mock_build.return_value = _entry(commits=["a b"])
    cfg = ExportConfig(max_pairs=1)
    export = build_changelog_export(["v1", "v2", "v3"], config=cfg)
    assert len(export.pairs) == 1
    assert export.pairs[0].from_tag == "v2"
    assert export.pairs[0].to_tag == "v3"


# ---------------------------------------------------------------------------
# render_export_markdown / render_export_plain
# ---------------------------------------------------------------------------

def test_render_export_markdown_no_pairs():
    export = ChangelogExport()
    result = render_export_markdown(export)
    assert "# Deployment Changelog" in result
    assert "No deployment pairs found" in result


def test_render_export_markdown_includes_tags():
    export = ChangelogExport(pairs=[_pair("v1.0", "v1.1")])
    result = render_export_markdown(export)
    assert "v1.0" in result
    assert "v1.1" in result


def test_render_export_plain_no_pairs():
    export = ChangelogExport()
    result = render_export_plain(export)
    assert "DEPLOYMENT CHANGELOG" in result
    assert "No deployment pairs found" in result


def test_render_export_plain_includes_separator():
    export = ChangelogExport(pairs=[_pair("v2.0", "v2.1")])
    result = render_export_plain(export)
    assert "v2.0 -> v2.1" in result
    assert "-" * 10 in result
