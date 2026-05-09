"""Renders a ChangelogExport to Markdown or plain text."""

from __future__ import annotations

from typing import List

from deploy_diff.tag_changelog_exporter import ChangelogExport, TagPairExport
from deploy_diff.summary_renderer import render_markdown, render_plain


def _render_pair_markdown(pair: TagPairExport) -> str:
    lines: List[str] = []
    lines.append(f"## {pair.from_tag} → {pair.to_tag}")
    lines.append("")
    lines.append(render_markdown(pair.entry))
    return "\n".join(lines)


def _render_pair_plain(pair: TagPairExport) -> str:
    lines: List[str] = []
    lines.append(f"{pair.from_tag} -> {pair.to_tag}")
    lines.append("-" * 40)
    lines.append(render_plain(pair.entry))
    return "\n".join(lines)


def render_export_markdown(export: ChangelogExport, title: str = "Deployment Changelog") -> str:
    """Render a full multi-pair export as a Markdown document."""
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(
        f"_Total: {export.total_commits} commit(s), "
        f"{export.total_config_changes} config change(s) across {len(export.pairs)} deployment(s)._"
    )
    lines.append("")

    if not export.pairs:
        lines.append("_No deployment pairs found._")
        return "\n".join(lines)

    for pair in export.pairs:
        lines.append(_render_pair_markdown(pair))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_export_plain(export: ChangelogExport, title: str = "Deployment Changelog") -> str:
    """Render a full multi-pair export as plain text."""
    lines: List[str] = []
    lines.append(title.upper())
    lines.append("=" * len(title))
    lines.append(
        f"Total: {export.total_commits} commit(s), "
        f"{export.total_config_changes} config change(s) across {len(export.pairs)} deployment(s)."
    )
    lines.append("")

    if not export.pairs:
        lines.append("No deployment pairs found.")
        return "\n".join(lines)

    for pair in export.pairs:
        lines.append(_render_pair_plain(pair))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
