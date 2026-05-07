"""Tests for deploy_diff.summary_renderer."""

from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.config_differ import ConfigChange
from deploy_diff.summary_renderer import render_markdown, render_plain


def _entry(
    from_tag="v1.0.0",
    to_tag="v1.1.0",
    commits=None,
    config_changes=None,
) -> ChangelogEntry:
    return ChangelogEntry(
        from_tag=from_tag,
        to_tag=to_tag,
        commits=commits or [],
        config_changes=config_changes or [],
    )


def _change(path="config/app.yaml", status="M", diff_summary="+2 -1") -> ConfigChange:
    return ConfigChange(path=path, status=status, diff_summary=diff_summary)


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------

def test_render_markdown_heading():
    md = render_markdown(_entry())
    assert "## v1.0.0 → v1.1.0" in md


def test_render_markdown_commits():
    md = render_markdown(_entry(commits=["abc1234 Fix bug", "def5678 Add feature"]))
    assert "- abc1234 Fix bug" in md
    assert "- def5678 Add feature" in md


def test_render_markdown_no_config_changes():
    md = render_markdown(_entry())
    assert "_No config changes._" in md


def test_render_markdown_with_config_changes():
    md = render_markdown(_entry(config_changes=[_change()]))
    assert "`config/app.yaml` (M)" in md
    assert "+2 -1" in md


def test_render_markdown_config_no_diff_summary():
    change = ConfigChange(path="config/app.yaml", status="A", diff_summary="")
    md = render_markdown(_entry(config_changes=[change]))
    assert "`config/app.yaml` (A)" in md
    assert " — " not in md


def test_render_markdown_ends_with_newline():
    assert render_markdown(_entry()).endswith("\n")


# ---------------------------------------------------------------------------
# render_plain
# ---------------------------------------------------------------------------

def test_render_plain_heading():
    txt = render_plain(_entry())
    assert "[v1.0.0 -> v1.1.0]" in txt


def test_render_plain_commits():
    txt = render_plain(_entry(commits=["abc1234 Fix bug"]))
    assert "  * abc1234 Fix bug" in txt


def test_render_plain_no_config():
    txt = render_plain(_entry())
    assert "No config changes." in txt


def test_render_plain_with_config():
    txt = render_plain(_entry(config_changes=[_change()]))
    assert "config/app.yaml [M]" in txt
    assert "(+2 -1)" in txt


def test_render_plain_ends_with_newline():
    assert render_plain(_entry()).endswith("\n")
