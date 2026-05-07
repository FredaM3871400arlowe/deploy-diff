"""Sorts tags by semantic version or date-based conventions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


_SEMVER_RE = re.compile(
    r"^(?P<prefix>[^\d]*)(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<rest>.*)$"
)
_DATE_RE = re.compile(
    r"^(?P<prefix>[^\d]*)(?P<year>\d{4})\.(?P<month>\d{2})\.(?P<day>\d{2})(?P<rest>.*)$"
)


@dataclass
class SortConfig:
    """Configuration for tag sorting behaviour."""

    reverse: bool = False
    ignore_prefixes: List[str] = field(default_factory=list)


def _strip_prefix(tag: str, prefixes: List[str]) -> str:
    for prefix in prefixes:
        if tag.startswith(prefix):
            return tag[len(prefix):]
    return tag


def _semver_key(tag: str) -> Optional[Tuple[int, int, int, str]]:
    m = _SEMVER_RE.match(tag)
    if m:
        return (int(m.group("major")), int(m.group("minor")), int(m.group("patch")), m.group("rest"))
    return None


def _date_key(tag: str) -> Optional[Tuple[int, int, int, str]]:
    m = _DATE_RE.match(tag)
    if m:
        return (int(m.group("year")), int(m.group("month")), int(m.group("day")), m.group("rest"))
    return None


def _sort_key(tag: str, config: SortConfig):
    """Return a sortable key for *tag*, preferring semver then date then lexicographic."""
    stripped = _strip_prefix(tag, config.ignore_prefixes)
    semver = _semver_key(stripped)
    if semver is not None:
        return (0, semver)
    date = _date_key(stripped)
    if date is not None:
        return (1, date)
    return (2, (stripped,))


def sort_tags(tags: List[str], config: Optional[SortConfig] = None) -> List[str]:
    """Return *tags* sorted according to *config*.

    Tags that look like semantic versions are sorted numerically.  Tags that
    follow a ``YYYY.MM.DD`` convention are sorted chronologically.  All other
    tags fall back to lexicographic ordering.  Pass ``reverse=True`` to get
    newest-first ordering.
    """
    if config is None:
        config = SortConfig()
    return sorted(tags, key=lambda t: _sort_key(t, config), reverse=config.reverse)
