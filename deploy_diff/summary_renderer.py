"""Renders a plain-text or Markdown summary of a changelog entry."""

from __future__ import annotations

from typing import List

from deploy_diff.changelog_formatter import ChangelogEntry


def _section(title: str, items: List[str], bullet: str = "- ") -> List[str]:
    """Build a titled bullet-list section; returns [] when items is empty."""
    if not items:
        return []
    lines = [f"### {title}"]
    lines.extend(f"{bullet}{item}" for item in items)
    lines.append("")
    return lines


def render_markdown(entry: ChangelogEntry) -> str:
    """Return a Markdown-formatted summary for a single ChangelogEntry."""
    lines: List[str] = []

    lines.append(f"## {entry.from_tag} → {entry.to_tag}")
    lines.append("")

    commit_items = [c.strip() for c in entry.commits if c.strip()]
    lines.extend(_section("Commits", commit_items))

    if entry.config_changes:
        config_items = [
            f"`{c.path}` ({c.status})"
            + (f" — {c.diff_summary}" if c.diff_summary else "")
            for c in entry.config_changes
        ]
        lines.extend(_section("Config Changes", config_items))
    else:
        lines.append("_No config changes._")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_plain(entry: ChangelogEntry) -> str:
    """Return a plain-text summary for a single ChangelogEntry."""
    lines: List[str] = []

    lines.append(f"[{entry.from_tag} -> {entry.to_tag}]")

    commit_items = [c.strip() for c in entry.commits if c.strip()]
    if commit_items:
        lines.append("Commits:")
        lines.extend(f"  * {c}" for c in commit_items)

    if entry.config_changes:
        lines.append("Config Changes:")
        for c in entry.config_changes:
            suffix = f" ({c.diff_summary})" if c.diff_summary else ""
            lines.append(f"  * {c.path} [{c.status}]{suffix}")
    else:
        lines.append("No config changes.")

    return "\n".join(lines) + "\n"
