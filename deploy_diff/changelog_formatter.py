"""Formats collected config changes and git log into a human-readable changelog."""

from dataclasses import dataclass
from typing import List, Optional

from deploy_diff.config_differ import ConfigChange
from deploy_diff.git_tagger import TagRange, run_git


@dataclass
class ChangelogEntry:
    tag_range: TagRange
    commits: List[str]
    config_changes: List[ConfigChange]


def get_commits_between(tag_range: TagRange, repo_path: str = ".") -> List[str]:
    """Return a list of commit summary lines between two tags."""
    ref_range = f"{tag_range.start}..{tag_range.end}"
    result = run_git(["log", "--oneline", "--no-merges", ref_range], cwd=repo_path)
    lines = result.stdout.strip().splitlines()
    return [line.strip() for line in lines if line.strip()]


def format_changelog(entry: ChangelogEntry, include_diff: bool = False) -> str:
    """Render a ChangelogEntry as a Markdown string."""
    lines: List[str] = []

    lines.append(f"## Changelog: {entry.tag_range.start} → {entry.tag_range.end}\n")

    lines.append("### Commits\n")
    if entry.commits:
        for commit in entry.commits:
            lines.append(f"- {commit}")
    else:
        lines.append("_No commits found._")

    lines.append("")
    lines.append("### Config Changes\n")

    if entry.config_changes:
        for change in entry.config_changes:
            status_label = {
                "A": "Added",
                "M": "Modified",
                "D": "Deleted",
            }.get(change.status, change.status)
            lines.append(f"- **{status_label}**: `{change.path}`")
            if include_diff and change.diff:
                lines.append("  ```diff")
                for diff_line in change.diff.splitlines():
                    lines.append(f"  {diff_line}")
                lines.append("  ```")
    else:
        lines.append("_No config file changes detected._")

    lines.append("")
    return "\n".join(lines)


def build_changelog_entry(
    tag_range: TagRange,
    config_changes: List[ConfigChange],
    repo_path: str = ".",
) -> ChangelogEntry:
    """Fetch commits and combine with config changes into a ChangelogEntry."""
    commits = get_commits_between(tag_range, repo_path=repo_path)
    return ChangelogEntry(
        tag_range=tag_range,
        commits=commits,
        config_changes=config_changes,
    )
