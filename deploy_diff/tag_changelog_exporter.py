"""Exports changelogs for a sequence of tag pairs to a structured format."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from deploy_diff.changelog_formatter import ChangelogEntry, build_changelog_entry
from deploy_diff.tag_filter import TagFilterConfig, filter_tags
from deploy_diff.tag_sorter import SortConfig, sort_tags
from deploy_diff.tag_validator import validate_tags


@dataclass
class ExportConfig:
    repo_path: str = "."
    filter: Optional[TagFilterConfig] = None
    sort: Optional[SortConfig] = None
    max_pairs: Optional[int] = None


@dataclass
class TagPairExport:
    from_tag: str
    to_tag: str
    entry: ChangelogEntry


@dataclass
class ChangelogExport:
    pairs: List[TagPairExport] = field(default_factory=list)

    @property
    def total_commits(self) -> int:
        return sum(len(p.entry.commits) for p in self.pairs)

    @property
    def total_config_changes(self) -> int:
        return sum(len(p.entry.config_changes) for p in self.pairs)


def _make_consecutive_pairs(tags: List[str]) -> List[tuple]:
    """Return consecutive (from, to) tag pairs from a sorted list."""
    if len(tags) < 2:
        return []
    return [(tags[i], tags[i + 1]) for i in range(len(tags) - 1)]


def build_changelog_export(
    tags: List[str],
    config: Optional[ExportConfig] = None,
) -> ChangelogExport:
    """Build a ChangelogExport from a list of tags using consecutive pairs."""
    cfg = config or ExportConfig()

    filtered = filter_tags(tags, cfg.filter)
    sorted_tags = sort_tags(filtered, cfg.sort)

    pairs = _make_consecutive_pairs(sorted_tags)
    if cfg.max_pairs is not None:
        pairs = pairs[-cfg.max_pairs :]

    export = ChangelogExport()
    for from_tag, to_tag in pairs:
        result = validate_tags(from_tag, to_tag, repo_path=cfg.repo_path)
        if not result:
            continue
        entry = build_changelog_entry(from_tag, to_tag, repo_path=cfg.repo_path)
        export.pairs.append(TagPairExport(from_tag=from_tag, to_tag=to_tag, entry=entry))

    return export
