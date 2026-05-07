"""Render a stats summary block in Markdown or plain text."""
from __future__ import annotations

from typing import List

from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.diff_stats import DiffStats, aggregate_stats, compute_stats, format_stats


def _bullet(label: str, value: object) -> str:
    return f"- **{label}:** {value}"


def render_stats_markdown(entries: List[ChangelogEntry]) -> str:
    """Return a Markdown stats block for *entries*."""
    if not entries:
        return "## Stats\n\nNo entries.\n"

    lines: List[str] = ["## Stats\n"]

    if len(entries) == 1:
        stats = compute_stats(entries[0])
        lines.append(_bullet("Commits", stats.total_commits))
        lines.append(_bullet("Config changes", stats.total_config_changes))
        if stats.config_files_changed:
            files = ", ".join(f"`{f}`" for f in stats.config_files_changed)
            lines.append(_bullet("Files touched", files))
        lines.append(_bullet("Added / Modified / Deleted", f"{stats.added} / {stats.modified} / {stats.deleted}"))
    else:
        agg = aggregate_stats(entries)
        lines.append(_bullet("Total commits", agg.total_commits))
        lines.append(_bullet("Total config changes", agg.total_config_changes))
        if agg.config_files_changed:
            files = ", ".join(f"`{f}`" for f in agg.config_files_changed)
            lines.append(_bullet("Unique files touched", files))
        lines.append(_bullet("Added / Modified / Deleted", f"{agg.added} / {agg.modified} / {agg.deleted}"))
        lines.append("")
        lines.append("### Per-deployment")
        for entry in entries:
            s = compute_stats(entry)
            lines.append(f"- `{entry.from_tag}` → `{entry.to_tag}`: {format_stats(s)}")

    return "\n".join(lines) + "\n"


def render_stats_plain(entries: List[ChangelogEntry]) -> str:
    """Return a plain-text stats block for *entries*."""
    if not entries:
        return "Stats: no entries.\n"

    if len(entries) == 1:
        stats = compute_stats(entries[0])
        return (
            f"Stats: {format_stats(stats)}\n"
            f"  Files: {', '.join(stats.config_files_changed) or 'none'}\n"
        )

    agg = aggregate_stats(entries)
    lines: List[str] = [
        f"Aggregate stats: {format_stats(agg)}",
        f"  Unique files: {', '.join(agg.config_files_changed) or 'none'}",
        "  Per-deployment:",
    ]
    for entry in entries:
        s = compute_stats(entry)
        lines.append(f"    {entry.from_tag} -> {entry.to_tag}: {format_stats(s)}")
    return "\n".join(lines) + "\n"
