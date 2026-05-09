"""Groups tags by environment prefix or naming convention."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class GroupConfig:
    """Configuration for grouping tags into environments."""
    patterns: Dict[str, str] = field(default_factory=dict)  # env -> regex
    default_group: str = "other"


@dataclass
class TagGroup:
    """A named group of tags."""
    name: str
    tags: List[str]

    def latest(self) -> Optional[str]:
        """Return the last tag in the group (assumed sorted)."""
        return self.tags[-1] if self.tags else None

    def previous(self) -> Optional[str]:
        """Return the second-to-last tag, or None."""
        return self.tags[-2] if len(self.tags) >= 2 else None


def group_tags(tags: List[str], config: GroupConfig) -> Dict[str, TagGroup]:
    """Partition *tags* into named groups based on *config* patterns.

    Tags are tested against each pattern in insertion order; the first match
    wins.  Unmatched tags fall into ``config.default_group``.
    """
    buckets: Dict[str, List[str]] = {name: [] for name in config.patterns}
    buckets.setdefault(config.default_group, [])

    compiled = {name: re.compile(pat) for name, pat in config.patterns.items()}

    for tag in tags:
        matched = False
        for name, rx in compiled.items():
            if rx.search(tag):
                buckets[name].append(tag)
                matched = True
                break
        if not matched:
            buckets[config.default_group].append(tag)

    return {name: TagGroup(name=name, tags=tag_list) for name, tag_list in buckets.items()}


def environment_pairs(groups: Dict[str, TagGroup]) -> Dict[str, tuple]:
    """Return ``{env: (previous_tag, latest_tag)}`` for each group with >= 1 tag.

    Groups with no tags are omitted.  Groups with exactly one tag have
    ``previous_tag`` set to ``None``.
    """
    result: Dict[str, tuple] = {}
    for name, group in groups.items():
        if group.tags:
            result[name] = (group.previous(), group.latest())
    return result
