"""Summarises the diff between two tags at a high level."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.diff_stats import DiffStats, compute_stats
from deploy_diff.tag_comparator import ComparisonResult, compare_tags


@dataclass
class TagDiffSummary:
    """High-level summary of what changed between two tags."""

    from_tag: str
    to_tag: str
    stats: DiffStats
    comparison: ComparisonResult
    entries: List[ChangelogEntry] = field(default_factory=list)

    @property
    def commit_count(self) -> int:
        return self.stats.total_commits

    @property
    def config_change_count(self) -> int:
        return self.stats.total_config_changes

    @property
    def has_drift(self) -> bool:
        return self.comparison.has_config_drift()

    @property
    def net_delta(self) -> int:
        return self.comparison.net_commit_delta()


def build_tag_diff_summary(
    from_tag: str,
    to_tag: str,
    entries: List[ChangelogEntry],
    repo_path: str = ".",
) -> TagDiffSummary:
    """Build a :class:`TagDiffSummary` from a list of changelog entries."""
    stats = compute_stats(entries)
    comparison = compare_tags(from_tag, to_tag, entries, repo_path=repo_path)
    return TagDiffSummary(
        from_tag=from_tag,
        to_tag=to_tag,
        stats=stats,
        comparison=comparison,
        entries=entries,
    )


def format_tag_diff_summary(summary: TagDiffSummary) -> str:
    """Return a concise human-readable string for the summary."""
    lines = [
        f"Tag diff: {summary.from_tag} → {summary.to_tag}",
        f"  Commits      : {summary.commit_count}",
        f"  Config changes: {summary.config_change_count}",
        f"  Net delta    : {summary.net_delta:+d}",
        f"  Config drift : {'yes' if summary.has_drift else 'no'}",
    ]
    return "\n".join(lines)
