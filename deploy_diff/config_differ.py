"""Detects and annotates configuration file changes between two git refs."""

import subprocess
from dataclasses import dataclass, field
from typing import Optional

CONFIG_EXTENSIONS = {".env", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}


@dataclass
class ConfigChange:
    """Represents a change in a single config file."""
    path: str
    status: str  # 'added', 'modified', 'deleted'
    diff_lines: list[str] = field(default_factory=list)


def _is_config_file(path: str) -> bool:
    """Return True if the path looks like a config file."""
    from pathlib import Path
    return Path(path).suffix.lower() in CONFIG_EXTENSIONS or Path(path).name.startswith(".env")


def get_changed_files(
    from_ref: str, to_ref: str, repo_path: str
) -> list[tuple[str, str]]:
    """Return list of (status, path) tuples for files changed between refs."""
    result = subprocess.run(
        ["git", "diff", "--name-status", from_ref, to_ref],
        capture_output=True,
        text=True,
        cwd=repo_path,
        check=True,
    )
    entries = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status_code, path = parts
            entries.append((status_code[0], path))
    return entries


def get_file_diff(from_ref: str, to_ref: str, path: str, repo_path: str) -> list[str]:
    """Return unified diff lines for a single file."""
    result = subprocess.run(
        ["git", "diff", from_ref, to_ref, "--", path],
        capture_output=True,
        text=True,
        cwd=repo_path,
    )
    return result.stdout.splitlines()


def collect_config_changes(
    from_ref: str, to_ref: str, repo_path: str
) -> list[ConfigChange]:
    """Collect all config-file changes between two refs."""
    status_map = {"A": "added", "M": "modified", "D": "deleted"}
    changed = get_changed_files(from_ref, to_ref, repo_path)
    config_changes = []
    for status_code, path in changed:
        if not _is_config_file(path):
            continue
        status = status_map.get(status_code, "modified")
        diff_lines = get_file_diff(from_ref, to_ref, path, repo_path)
        config_changes.append(ConfigChange(path=path, status=status, diff_lines=diff_lines))
    return config_changes
