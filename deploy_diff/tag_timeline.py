"""Builds a chronological timeline of tag deployments with metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from deploy_diff.git_tagger import run_git
from deploy_diff.tag_annotator import TagAnnotation, get_tag_annotation


@dataclass
class TimelineEntry:
    tag: str
    commit: str
    author: str
    date: str
    annotation: Optional[TagAnnotation] = None
    commit_count: int = 0


@dataclass
class TagTimeline:
    entries: List[TimelineEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)


def _get_commit_info(tag: str) -> tuple[str, str, str]:
    """Return (commit_hash, author, date) for a given tag."""
    out = run_git(["log", "-1", "--format=%H%x1f%an%x1f%ai", tag])
    parts = out.strip().split("\x1f")
    if len(parts) != 3:
        return ("", "", "")
    return parts[0], parts[1], parts[2]


def _count_commits_since_previous(tag: str, previous: Optional[str]) -> int:
    """Return number of commits between previous tag and this tag."""
    if previous is None:
        return 0
    out = run_git(["rev-list", "--count", f"{previous}..{tag}"])
    try:
        return int(out.strip())
    except ValueError:
        return 0


def build_timeline(tags: List[str], include_annotations: bool = True) -> TagTimeline:
    """Build a TagTimeline from an ordered list of tags."""
    entries: List[TimelineEntry] = []
    for i, tag in enumerate(tags):
        commit, author, date = _get_commit_info(tag)
        previous = tags[i - 1] if i > 0 else None
        commit_count = _count_commits_since_previous(tag, previous)
        annotation = get_tag_annotation(tag) if include_annotations else None
        entries.append(
            TimelineEntry(
                tag=tag,
                commit=commit,
                author=author,
                date=date,
                annotation=annotation,
                commit_count=commit_count,
            )
        )
    return TagTimeline(entries=entries)


def render_timeline_plain(timeline: TagTimeline) -> str:
    """Render a plain-text summary of the tag timeline."""
    lines: List[str] = ["Tag Timeline", "=" * 40]
    for entry in timeline:
        lines.append(f"  {entry.tag}")
        lines.append(f"    commit : {entry.commit[:12] if entry.commit else 'unknown'}")
        lines.append(f"    author : {entry.author or 'unknown'}")
        lines.append(f"    date   : {entry.date or 'unknown'}")
        if entry.commit_count:
            lines.append(f"    commits: +{entry.commit_count} since previous")
        if entry.annotation and entry.annotation.message:
            lines.append(f"    note   : {entry.annotation.message}")
        lines.append("")
    return "\n".join(lines)
