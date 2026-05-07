"""Compares two tag ranges and highlights what changed between deployments."""

from dataclasses import dataclass, field
from typing import List, Optional

from deploy_diff.diff_stats import DiffStats, aggregate_stats, compute_stats
from deploy_diff.changelog_formatter import ChangelogEntry


@dataclass
class ComparisonResult:
    """Result of comparing two deployment ranges."""

    baseline_tag: str
    candidate_tag: str
    baseline_stats: DiffStats
    candidate_stats: DiffStats
    new_commits: int
    dropped_commits: int
    new_config_files: List[str] = field(default_factory=list)
    dropped_config_files: List[str] = field(default_factory=list)
    common_config_files: List[str] = field(default_factory=list)

    @property
    def net_commit_delta(self) -> int:
        return self.new_commits - self.dropped_commits

    @property
    def has_config_drift(self) -> bool:
        return bool(self.new_config_files or self.dropped_config_files)


def _config_file_set(entries: List[ChangelogEntry]) -> set:
    """Return the set of config file paths touched across all entries."""
    files: set = set()
    for entry in entries:
        for change in entry.config_changes:
            files.add(change.path)
    return files


def _commit_hashes(entries: List[ChangelogEntry]) -> set:
    """Return the set of short commit messages (used as proxy for identity)."""
    hashes: set = set()
    for entry in entries:
        hashes.update(entry.commits)
    return hashes


def compare_deployments(
    baseline_tag: str,
    candidate_tag: str,
    baseline_entries: List[ChangelogEntry],
    candidate_entries: List[ChangelogEntry],
) -> ComparisonResult:
    """Compare two sets of changelog entries and produce a ComparisonResult."""
    baseline_stats = aggregate_stats(baseline_entries)
    candidate_stats = aggregate_stats(candidate_entries)

    baseline_commits = _commit_hashes(baseline_entries)
    candidate_commits = _commit_hashes(candidate_entries)

    new_commits = len(candidate_commits - baseline_commits)
    dropped_commits = len(baseline_commits - candidate_commits)

    baseline_files = _config_file_set(baseline_entries)
    candidate_files = _config_file_set(candidate_entries)

    new_config_files = sorted(candidate_files - baseline_files)
    dropped_config_files = sorted(baseline_files - candidate_files)
    common_config_files = sorted(baseline_files & candidate_files)

    return ComparisonResult(
        baseline_tag=baseline_tag,
        candidate_tag=candidate_tag,
        baseline_stats=baseline_stats,
        candidate_stats=candidate_stats,
        new_commits=new_commits,
        dropped_commits=dropped_commits,
        new_config_files=new_config_files,
        dropped_config_files=dropped_config_files,
        common_config_files=common_config_files,
    )
