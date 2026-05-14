"""Tracks commit activity per tag over time, producing per-tag activity summaries."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from deploy_diff.git_tagger import run_git


@dataclass
class TagActivity:
    tag: str
    commit_count: int
    authors: List[str] = field(default_factory=list)
    first_commit: Optional[str] = None
    last_commit: Optional[str] = None

    @property
    def unique_authors(self) -> List[str]:
        return sorted(set(self.authors))

    @property
    def author_count(self) -> int:
        return len(self.unique_authors)


def _get_log_lines(from_tag: str, to_tag: str, fmt: str) -> List[str]:
    result = run_git(["log", f"{from_tag}..{to_tag}", f"--pretty=format:{fmt}"])
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def get_tag_activity(from_tag: str, to_tag: str) -> TagActivity:
    """Build a TagActivity for commits between from_tag and to_tag."""
    authors = _get_log_lines(from_tag, to_tag, "%aN")
    dates = _get_log_lines(from_tag, to_tag, "%ci")

    first_commit: Optional[str] = dates[-1] if dates else None
    last_commit: Optional[str] = dates[0] if dates else None

    return TagActivity(
        tag=to_tag,
        commit_count=len(authors),
        authors=authors,
        first_commit=first_commit,
        last_commit=last_commit,
    )


def track_activity(tags: List[str]) -> List[TagActivity]:
    """Return TagActivity for each consecutive tag pair in the list."""
    if len(tags) < 2:
        return []
    results: List[TagActivity] = []
    for from_tag, to_tag in zip(tags, tags[1:]):
        results.append(get_tag_activity(from_tag, to_tag))
    return results


def format_activity_table(activities: List[TagActivity]) -> str:
    """Render a plain-text table summarising tag activity."""
    if not activities:
        return "No activity data available."
    header = f"{'Tag':<30} {'Commits':>8} {'Authors':>8} {'Last Commit':<25}"
    sep = "-" * len(header)
    rows = [header, sep]
    for a in activities:
        last = a.last_commit or "—"
        rows.append(f"{a.tag:<30} {a.commit_count:>8} {a.author_count:>8} {last:<25}")
    return "\n".join(rows)
