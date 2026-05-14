"""Attributes each tag to the git user who created it."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from deploy_diff.git_tagger import run_git


@dataclass(frozen=True)
class TagBlame:
    tag: str
    tagger_name: str
    tagger_email: str
    date: str
    message: str

    @property
    def short_identity(self) -> str:
        """Return 'Name <email>' string."""
        return f"{self.tagger_name} <{self.tagger_email}>"


def _get_blame_for_tag(tag: str, repo_path: str = ".") -> Optional[TagBlame]:
    """Return blame info for a single tag, or None if unavailable."""
    # Try annotated tag first
    result = run_git(
        ["tag", "-v", tag],
        cwd=repo_path,
        check=False,
    )
    if result.returncode == 0:
        name = email = date = message = ""
        for line in result.stderr.splitlines():
            if line.startswith("tagger "):
                rest = line[len("tagger "):].strip()
                # format: Name <email> timestamp tz
                if "<" in rest:
                    name_part, rest2 = rest.split("<", 1)
                    name = name_part.strip()
                    email_part, date_part = rest2.split(">", 1)
                    email = email_part.strip()
                    date = date_part.strip()
            elif line.startswith(" ") and not message:
                message = line.strip()
        if name:
            return TagBlame(tag=tag, tagger_name=name, tagger_email=email,
                            date=date, message=message)

    # Fall back to commit author
    log_result = run_git(
        ["log", "-1", "--format=%an%x00%ae%x00%ai%x00%s", f"refs/tags/{tag}"],
        cwd=repo_path,
        check=False,
    )
    if log_result.returncode != 0 or not log_result.stdout.strip():
        return None
    parts = log_result.stdout.strip().split("\x00")
    if len(parts) < 4:
        return None
    return TagBlame(
        tag=tag,
        tagger_name=parts[0],
        tagger_email=parts[1],
        date=parts[2],
        message=parts[3],
    )


def blame_tags(tags: List[str], repo_path: str = ".") -> List[TagBlame]:
    """Return blame info for each tag that can be resolved."""
    results: List[TagBlame] = []
    for tag in tags:
        blame = _get_blame_for_tag(tag, repo_path=repo_path)
        if blame is not None:
            results.append(blame)
    return results


def format_blame_table(blames: List[TagBlame]) -> str:
    """Render blame list as a plain-text table."""
    if not blames:
        return "No blame information available."
    lines = [f"{'Tag':<30} {'Author':<30} {'Date':<25} Message"]
    lines.append("-" * 100)
    for b in blames:
        lines.append(
            f"{b.tag:<30} {b.short_identity:<30} {b.date[:19]:<25} {b.message}"
        )
    return "\n".join(lines)
