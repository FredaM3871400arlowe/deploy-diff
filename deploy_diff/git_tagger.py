"""Module for fetching and comparing git tags to identify deployment ranges."""

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class TagRange:
    """Represents a range between two git tags."""
    from_tag: str
    to_tag: str
    from_commit: str
    to_commit: str


def run_git(args: list[str], cwd: Optional[str] = None) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
        check=True,
    )
    return result.stdout.strip()


def list_tags(repo_path: str) -> list[str]:
    """Return all git tags sorted by version (newest first)."""
    output = run_git(["tag", "--sort=-version:refname"], cwd=repo_path)
    return [t for t in output.splitlines() if t]


def resolve_commit(tag: str, repo_path: str) -> str:
    """Resolve a tag to its full commit SHA."""
    return run_git(["rev-list", "-n", "1", tag], cwd=repo_path)


def get_tag_range(from_tag: str, to_tag: str, repo_path: str) -> TagRange:
    """Build a TagRange object for the given tag pair."""
    from_commit = resolve_commit(from_tag, repo_path)
    to_commit = resolve_commit(to_tag, repo_path)
    return TagRange(
        from_tag=from_tag,
        to_tag=to_tag,
        from_commit=from_commit,
        to_commit=to_commit,
    )


def get_commits_in_range(tag_range: TagRange, repo_path: str) -> list[dict]:
    """Return commits between two tags as a list of dicts."""
    log_format = "%H|%s|%an|%ad"
    output = run_git(
        [
            "log",
            f"{tag_range.from_commit}..{tag_range.to_commit}",
            f"--pretty=format:{log_format}",
            "--date=short",
        ],
        cwd=repo_path,
    )
    commits = []
    for line in output.splitlines():
        if not line:
            continue
        sha, subject, author, date = line.split("|", 3)
        commits.append({"sha": sha, "subject": subject, "author": author, "date": date})
    return commits
