"""Validates tag pairs before diffing to provide clear error messages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from deploy_diff.git_tagger import list_tags


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]

    def __bool__(self) -> bool:
        return self.valid


def _tag_exists(tag: str, known_tags: List[str]) -> bool:
    return tag in known_tags


def _tags_are_distinct(from_tag: str, to_tag: str) -> bool:
    return from_tag != to_tag


def _from_precedes_to(from_tag: str, to_tag: str, known_tags: List[str]) -> bool:
    """Return True if from_tag appears before to_tag in the ordered tag list."""
    if from_tag not in known_tags or to_tag not in known_tags:
        return True  # can't determine order; let other checks catch missing tags
    return known_tags.index(from_tag) < known_tags.index(to_tag)


def validate_tag_range(
    from_tag: str,
    to_tag: str,
    repo_path: str = ".",
    known_tags: Optional[List[str]] = None,
) -> ValidationResult:
    """Validate that from_tag and to_tag form a sensible diff range."""
    errors: List[str] = []

    tags = known_tags if known_tags is not None else list_tags(repo_path)

    if not _tag_exists(from_tag, tags):
        errors.append(f"Tag not found in repository: '{from_tag}'")

    if not _tag_exists(to_tag, tags):
        errors.append(f"Tag not found in repository: '{to_tag}'")

    if not errors and not _tags_are_distinct(from_tag, to_tag):
        errors.append(f"from_tag and to_tag must differ, both are '{from_tag}'")

    if not errors and not _from_precedes_to(from_tag, to_tag, tags):
        errors.append(
            f"from_tag '{from_tag}' does not precede to_tag '{to_tag}' in tag history"
        )

    return ValidationResult(valid=len(errors) == 0, errors=errors)
