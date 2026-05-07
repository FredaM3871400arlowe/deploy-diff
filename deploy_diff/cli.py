"""Command-line interface for deploy-diff."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from deploy_diff.changelog_formatter import build_changelog_entry, format_changelog
from deploy_diff.config_differ import collect_config_changes
from deploy_diff.git_tagger import get_tag_range
from deploy_diff.output_writer import build_output_config, write_output


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a human-readable changelog between two deployment tags."
    )
    parser.add_argument("from_tag", help="Starting git tag (older deployment).")
    parser.add_argument(
        "to_tag",
        nargs="?",
        default="HEAD",
        help="Ending git tag or ref (default: HEAD).",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to the git repository (default: current directory).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to the output file instead of overwriting.",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages on stderr.",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Omit config-file change annotations from the changelog.",
    )
    return parser.parse_args(argv)


def run(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)

    try:
        tag_range = get_tag_range(args.from_tag, args.to_tag, repo=args.repo)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    config_changes = [] if args.no_config else collect_config_changes(
        tag_range.from_tag, tag_range.to_tag, repo=args.repo
    )

    entry = build_changelog_entry(tag_range, config_changes, repo=args.repo)
    output = format_changelog([entry])

    out_cfg = build_output_config(
        args.output, append=args.append, quiet=args.quiet
    )
    write_output(output, out_cfg)
    return 0


def main() -> None:  # pragma: no cover
    sys.exit(run())
