"""Formats ValidationResult errors for CLI output."""

from __future__ import annotations

from typing import IO, Optional
import sys

from deploy_diff.tag_validator import ValidationResult

_PREFIX_ERROR = "  ✗"
_PREFIX_OK = "  ✓"


def _header(from_tag: str, to_tag: str) -> str:
    return f"Validating tag range: {from_tag!r} → {to_tag!r}"


def format_validation_report(
    result: ValidationResult,
    from_tag: str,
    to_tag: str,
) -> str:
    """Return a human-readable validation report string."""
    lines = [_header(from_tag, to_tag)]
    if result.valid:
        lines.append(f"{_PREFIX_OK} Tag range is valid")
    else:
        for error in result.errors:
            lines.append(f"{_PREFIX_ERROR} {error}")
    return "\n".join(lines)


def report_and_exit_if_invalid(
    result: ValidationResult,
    from_tag: str,
    to_tag: str,
    stream: Optional[IO[str]] = None,
    exit_code: int = 1,
) -> None:
    """Print a validation report to *stream* and exit if the result is invalid.

    Does nothing if *result* is valid.
    """
    if result.valid:
        return
    out = stream or sys.stderr
    out.write(format_validation_report(result, from_tag, to_tag))
    out.write("\n")
    sys.exit(exit_code)
