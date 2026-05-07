"""Utilities for filtering and validating deployment tags."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TagFilterConfig:
    """Configuration for tag filtering."""

    pattern: Optional[str] = None
    prefix: Optional[str] = None
    exclude_patterns: List[str] = field(default_factory=list)
    limit: Optional[int] = None


def matches_pattern(tag: str, pattern: str) -> bool:
    """Return True if tag matches the given regex pattern."""
    return bool(re.search(pattern, tag))


def filter_tags(
    tags: List[str],
    config: TagFilterConfig,
) -> List[str]:
    """Filter a list of tags according to the given config.

    Applies prefix filter, include pattern, exclude patterns, and limit
    in that order.
    """
    result = list(tags)

    if config.prefix:
        result = [t for t in result if t.startswith(config.prefix)]

    if config.pattern:
        result = [t for t in result if matches_pattern(t, config.pattern)]

    for excl in config.exclude_patterns:
        result = [t for t in result if not matches_pattern(t, excl)]

    if config.limit is not None:
        result = result[: config.limit]

    return result


def latest_tag(tags: List[str]) -> Optional[str]:
    """Return the last tag in the list, or None if empty."""
    return tags[-1] if tags else None


def previous_tag(tags: List[str], current: str) -> Optional[str]:
    """Return the tag immediately before *current* in the list, or None."""
    try:
        idx = tags.index(current)
    except ValueError:
        return None
    if idx == 0:
        return None
    return tags[idx - 1]
