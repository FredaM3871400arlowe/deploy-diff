"""Command-line interface for deploy-diff."""

import argparse
import sys
from pathlib import Path

from deploy_diff.git_tagger import get_tag_range
from deploy_diff.config_differ import collect_config_changes
from deploy_diff.changelog_formatter import build_changelog_entry, format_changelog


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="deploy-diff",
        description="Generate a human-readable changelog between two deployment tags.",
    )
    parser.add_argument(
        "from_tag",
        help="The earlier git tag (start of range).",
    )
    parser.add_argument(
        "to_tag",
        nargs="?",
        default="HEAD",
        help="The later git tag or ref (default: HEAD).",
    )
    parser.add_argument(
        "--repo",
        default=".",
        metavar="PATH",
        help="Path to the git repository (default: current directory).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="FILE",
        help="Write changelog to FILE instead of stdout.",
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Omit config-change annotations from the output.",
    )
    return parser.parse_args(argv)


def run(argv=None):
    args = parse_args(argv)

    try:
        tag_range = get_tag_range(args.from_tag, args.to_tag, repo=args.repo)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    config_changes = [] if args.no_config else collect_config_changes(
        tag_range.from_tag, tag_range.to_tag, repo=args.repo
    )

    entry = build_changelog_entry(tag_range, config_changes, repo=args.repo)
    output = format_changelog([entry])

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Changelog written to {args.output}")
    else:
        print(output, end="")

    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
