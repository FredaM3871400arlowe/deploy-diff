"""Generates a combined changelog report across multiple tag groups/environments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from deploy_diff.tag_grouper import GroupConfig, TagGroup, group_tags, environment_pairs
from deploy_diff.changelog_formatter import build_changelog_entry, ChangelogEntry
from deploy_diff.summary_renderer import render_markdown, render_plain


@dataclass
class EnvReport:
    """Changelog report for a single environment."""
    env: str
    from_tag: Optional[str]
    to_tag: str
    entry: Optional[ChangelogEntry]  # None when from_tag is None


def build_env_reports(
    tags: List[str],
    config: GroupConfig,
    repo_path: str = ".",
) -> List[EnvReport]:
    """Build one :class:`EnvReport` per environment group.

    Tags must already be sorted (oldest → newest) before being passed in.
    """
    groups: Dict[str, TagGroup] = group_tags(tags, config)
    pairs = environment_pairs(groups)

    reports: List[EnvReport] = []
    for env, (from_tag, to_tag) in sorted(pairs.items()):
        if from_tag is None:
            reports.append(EnvReport(env=env, from_tag=None, to_tag=to_tag, entry=None))
            continue
        entry = build_changelog_entry(from_tag, to_tag, repo_path=repo_path)
        reports.append(EnvReport(env=env, from_tag=from_tag, to_tag=to_tag, entry=entry))

    return reports


def render_multi_env_markdown(reports: List[EnvReport]) -> str:
    """Render all environment reports as a single Markdown document."""
    sections: List[str] = []
    for report in reports:
        header = f"## Environment: {report.env}  ({report.from_tag or '?'} → {report.to_tag})"
        if report.entry is None:
            sections.append(f"{header}\n\n_No previous tag — baseline deployment._")
        else:
            body = render_markdown(report.entry)
            sections.append(f"{header}\n\n{body}")
    return "\n\n---\n\n".join(sections)


def render_multi_env_plain(reports: List[EnvReport]) -> str:
    """Render all environment reports as plain text."""
    sections: List[str] = []
    for report in reports:
        header = f"[{report.env}] {report.from_tag or '?'} -> {report.to_tag}"
        separator = "=" * len(header)
        if report.entry is None:
            sections.append(f"{separator}\n{header}\n{separator}\n\nNo previous tag — baseline deployment.")
        else:
            body = render_plain(report.entry)
            sections.append(f"{separator}\n{header}\n{separator}\n\n{body}")
    return "\n\n".join(sections)
