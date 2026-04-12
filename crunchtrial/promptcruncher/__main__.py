#!/usr/bin/env python3
"""
promptcruncher CLI

Usage:
    python -m promptcruncher "your prompt here"
    echo "your prompt" | python -m promptcruncher
    python -m promptcruncher --aggressive "your prompt here"
    python -m promptcruncher --file prompt.txt
"""

import argparse
import sys
from . import crunch


def main():
    parser = argparse.ArgumentParser(
        prog="promptcruncher",
        description="Compress prompts before sending to an LLM. Free, local, no API needed.",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt text to compress (or pipe via stdin)",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Read prompt from a file instead",
    )
    parser.add_argument(
        "--aggressive", "-a",
        action="store_true",
        help="Also strip hedging and softening language",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Disable sentence deduplication",
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Print stats only, not the compressed text",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Print only the compressed text, no stats",
    )

    args = parser.parse_args()

    # Get input
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.prompt:
        text = args.prompt
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)

    result = crunch(
        text,
        deduplicate=not args.no_dedup,
        aggressive=args.aggressive,
    )

    if args.quiet:
        print(result.text)
    elif args.stats_only:
        result.report()
    else:
        print(result.text)
        print()
        result.report()


if __name__ == "__main__":
    main()
