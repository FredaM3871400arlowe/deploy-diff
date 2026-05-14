"""Tests for deploy_diff.export_renderer."""
from deploy_diff.export_renderer import (
    _render_pair_markdown,
    _render_pair_plain,
    render_export_markdown,
    render_export_plain,
)
from deploy_diff.tag_changelog_exporter import TagPairExport, ChangelogExport
from deploy_diff.config_differ import ConfigChange
from deploy_diff.changelog_formatter import ChangelogEntry


def _change(path="config/app.yml", status="M", diff="-old\n+new"):
    return ConfigChange(path=path, status=status, diff=diff)


def _entry(from_tag="v1.0", to_tag="v2.0", commits=None, changes=None):
    return ChangelogEntry(
        from_tag=from_tag,
        to_tag=to_tag,
        commits=commits or ["abc1234 feat: add thing"],
        config_changes=changes or [],
    )


def _pair(from_tag="v1.0", to_tag="v2.0", entry=None, error=None):
    return TagPairExport(
        from_tag=from_tag,
        to_tag=to_tag,
        entry=entry or _entry(from_tag, to_tag),
        error=error,
    )


def _export(pairs=None):
    p = pairs or [_pair()]
    return ChangelogExport(pairs=p)


# ---------------------------------------------------------------------------
# _render_pair_markdown
# ---------------------------------------------------------------------------

def test_render_pair_markdown_contains_tags():
    out = _render_pair_markdown(_pair(from_tag="v1.0", to_tag="v2.0"))
    assert "v1.0" in out
    assert "v2.0" in out


def test_render_pair_markdown_shows_error():
    p = _pair(error="git failed", entry=None)
    p = TagPairExport(from_tag="v1.0", to_tag="v2.0", entry=None, error="git failed")
    out = _render_pair_markdown(p)
    assert "git failed" in out


def test_render_pair_markdown_shows_commits():
    entry = _entry(commits=["aaa1111 fix: something"])
    out = _render_pair_markdown(_pair(entry=entry))
    assert "fix: something" in out


# ---------------------------------------------------------------------------
# _render_pair_plain
# ---------------------------------------------------------------------------

def test_render_pair_plain_contains_tags():
    out = _render_pair_plain(_pair(from_tag="v3.0", to_tag="v4.0"))
    assert "v3.0" in out
    assert "v4.0" in out


def test_render_pair_plain_shows_error():
    p = TagPairExport(from_tag="v1.0", to_tag="v2.0", entry=None, error="oops")
    out = _render_pair_plain(p)
    assert "oops" in out


# ---------------------------------------------------------------------------
# render_export_markdown / render_export_plain
# ---------------------------------------------------------------------------

def test_render_export_markdown_joins_pairs():
    pairs = [_pair("v1.0", "v2.0"), _pair("v2.0", "v3.0")]
    out = render_export_markdown(_export(pairs))
    assert "v1.0" in out
    assert "v3.0" in out


def test_render_export_plain_joins_pairs():
    pairs = [_pair("v1.0", "v2.0"), _pair("v2.0", "v3.0")]
    out = render_export_plain(_export(pairs))
    assert "v1.0" in out
    assert "v3.0" in out


def test_render_export_markdown_empty_pairs():
    out = render_export_markdown(_export([]))
    assert isinstance(out, str)


def test_render_export_plain_empty_pairs():
    out = render_export_plain(_export([]))
    assert isinstance(out, str)
