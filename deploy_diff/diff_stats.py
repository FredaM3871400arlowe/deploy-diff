"""Compute and format statistics about a deployment diff."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from deploy_diff.changelog_formatter import ChangelogEntry
from deploy_diff.config_differ import ConfigChange


@dataclass
class DiffStats:
    """Aggregate statistics for a changelog entry or a collection of entries."""

    total_commits: int = 0
    total_config_changes: int = 0
    config_files_changed: List[str] = field(default_factory=list)
    added: int = 0
    modified: int = 0
    deleted: int = 0

    @property
    def has_changes(self) -> bool:
        return self.total_commits > 0 or self.total_config_changes > 0


def _tally_config_changes(changes: List[ConfigChange]) -> tuple[int, int, int, List[str]]:
    """Return (added, modified, deleted, unique_files) counts."""
    added = modified = deleted = 0
    files: List[str] = []
    for change in changes:
        if change.path not in files:
            files.append(change.path)
        status = change.status.upper()
        if status == "A":
            added += 1
        elif status == "D":
            deleted += 1
        else:
            modified += 1
    return added, modified, deleted, files


def compute_stats(entry: ChangelogEntry) -> DiffStats:
    """Compute a :class:`DiffStats` for a single :class:`ChangelogEntry`."""
    added, modified, deleted, files = _tally_config_changes(entry.config_changes)
    return DiffStats(
        total_commits=len(entry.commits),
        total_config_changes=len(entry.config_changes),
        config_files_changed=files,
        added=added,
        modified=modified,
        deleted=deleted,
    )


def aggregate_stats(entries: List[ChangelogEntry]) -> DiffStats:
    """Aggregate :class:`DiffStats` across multiple changelog entries."""
    totals = DiffStats()
    seen_files: List[str] = []
    for entry in entries:
        s = compute_stats(entry)
        totals.total_commits += s.total_commits
        totals.total_config_changes += s.total_config_changes
        totals.added += s.added
        totals.modified += s.modified
        totals.deleted += s.deleted
        for f in s.config_files_changed:
            if f not in seen_files:
                seen_files.append(f)
    totals.config_files_changed = seen_files
    return totals


def format_stats(stats: DiffStats) -> str:
    """Return a compact human-readable summary line for *stats*."""
    parts = [f"{stats.total_commits} commit(s)"]
    if stats.total_config_changes:
        detail = f"+{stats.added}/-{stats.deleted}/~{stats.modified}"
        parts.append(f"{stats.total_config_changes} config change(s) ({detail})")
    else:
        parts.append("no config changes")
    return ", ".join(parts)
