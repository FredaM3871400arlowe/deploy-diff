"""Checks the health of a tag sequence, surfacing gaps, duplicates, and ordering anomalies."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from deploy_diff.tag_sorter import SortConfig, sort_tags


@dataclass
class HealthIssue:
    level: str  # "warning" | "error"
    message: str


@dataclass
class TagHealthReport:
    tags: List[str]
    issues: List[HealthIssue] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return not any(i.level == "error" for i in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.level == "error")


def _check_duplicates(tags: List[str]) -> List[HealthIssue]:
    seen: set = set()
    issues: List[HealthIssue] = []
    for tag in tags:
        if tag in seen:
            issues.append(HealthIssue(level="error", message=f"Duplicate tag detected: '{tag}'"))
        seen.add(tag)
    return issues


def _check_empty(tags: List[str]) -> List[HealthIssue]:
    if not tags:
        return [HealthIssue(level="warning", message="Tag list is empty; nothing to analyse")]
    return []


def _check_single_tag(tags: List[str]) -> List[HealthIssue]:
    if len(tags) == 1:
        return [HealthIssue(level="warning", message="Only one tag present; no diff range available")]
    return []


def _check_sort_consistency(tags: List[str], sort_config: SortConfig) -> List[HealthIssue]:
    """Warn when the provided tag order differs from the expected sort order."""
    sorted_tags = sort_tags(tags, sort_config)
    if tags != sorted_tags:
        return [
            HealthIssue(
                level="warning",
                message="Tag order does not match expected sort order; consider re-sorting",
            )
        ]
    return []


def check_tag_health(
    tags: List[str],
    sort_config: SortConfig | None = None,
) -> TagHealthReport:
    """Run all health checks and return a consolidated report."""
    if sort_config is None:
        sort_config = SortConfig()

    issues: List[HealthIssue] = []
    issues.extend(_check_empty(tags))
    issues.extend(_check_duplicates(tags))
    issues.extend(_check_single_tag(tags))
    if len(tags) > 1:
        issues.extend(_check_sort_consistency(tags, sort_config))

    return TagHealthReport(tags=list(tags), issues=issues)
