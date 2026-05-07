"""Handles writing changelog output to files or stdout."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class OutputConfig:
    """Configuration for output destination and formatting."""

    output_path: Optional[Path] = None
    append: bool = False
    quiet: bool = False


def write_output(content: str, config: OutputConfig) -> None:
    """Write changelog content to the configured destination.

    Args:
        content: The formatted changelog string to write.
        config: Output configuration (file path, append mode, quiet flag).
    """
    if config.output_path is not None:
        _write_to_file(content, config)
        if not config.quiet:
            print(f"Changelog written to {config.output_path}", file=sys.stderr)
    else:
        if not config.quiet:
            sys.stdout.write(content)
            if not content.endswith("\n"):
                sys.stdout.write("\n")


def _write_to_file(content: str, config: OutputConfig) -> None:
    """Write content to a file, creating parent directories as needed."""
    assert config.output_path is not None
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if config.append else "w"
    with config.output_path.open(mode, encoding="utf-8") as fh:
        fh.write(content)
        if not content.endswith("\n"):
            fh.write("\n")


def build_output_config(
    output_path: Optional[str],
    append: bool = False,
    quiet: bool = False,
) -> OutputConfig:
    """Construct an OutputConfig from raw CLI values."""
    path = Path(output_path) if output_path else None
    return OutputConfig(output_path=path, append=append, quiet=quiet)
