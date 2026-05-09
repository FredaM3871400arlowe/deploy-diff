"""Annotates tags with metadata such as deploy timestamps and author info."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from deploy_diff.git_tagger import run_git


@dataclass
class TagAnnotation:
    tag: str
    commit_hash: str
    author_name: str
    author_email: str
    tag_date: str
    subject: str
    is_annotated: bool


def _is_annotated_tag(tag: str) -> bool:
    """Return True if the tag is an annotated (not lightweight) git tag."""
    result = run_git(["cat-file", "-t", f"refs/tags/{tag}"])
    return result.stdout.strip() == "tag"


def get_tag_annotation(tag: str) -> TagAnnotation:
    """Fetch metadata for a single tag from git."""
    is_annotated = _is_annotated_tag(tag)

    # Use %(*H) for annotated tags to dereference to commit; fall back to %H
    fmt = "%H%n%an%n%ae%n%ai%n%s"
    result = run_git(["log", "-1", "--format=" + fmt, tag])
    lines = result.stdout.splitlines()

    if len(lines) < 5:
        raise ValueError(f"Unexpected git log output for tag '{tag}': {result.stdout!r}")

    return TagAnnotation(
        tag=tag,
        commit_hash=lines[0].strip(),
        author_name=lines[1].strip(),
        author_email=lines[2].strip(),
        tag_date=lines[3].strip(),
        subject=lines[4].strip(),
        is_annotated=is_annotated,
    )


def annotate_tags(tags: list[str]) -> list[TagAnnotation]:
    """Return a list of TagAnnotation objects for each tag in order."""
    return [get_tag_annotation(t) for t in tags]


def format_annotation_summary(annotation: TagAnnotation) -> str:
    """Return a human-readable one-line summary of a tag annotation."""
    kind = "annotated" if annotation.is_annotated else "lightweight"
    return (
        f"{annotation.tag} [{kind}] "
        f"by {annotation.author_name} <{annotation.author_email}> "
        f"on {annotation.tag_date} — {annotation.subject}"
    )
