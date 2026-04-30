"""CLI entry point for word/character count commands."""
from __future__ import annotations

import argparse
import csv
import sys

from csvwrangler.wordcount import word_count, char_count


def _load_csv(path: str) -> tuple[list[dict], list[str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def _write_csv(rows: list[dict], fieldnames: list[str], path: str | None) -> None:
    dest = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            dest.close()


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler-wordcount",
        description="Add word or character count columns to a CSV.",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument("column", help="Column to count")
    parser.add_argument(
        "--mode",
        choices=["word", "char"],
        default="word",
        help="Count words (default) or characters",
    )
    parser.add_argument("--dest", default=None, help="Destination column name")
    parser.add_argument(
        "--sep",
        default=None,
        help="Word separator (word mode only; default: whitespace)",
    )
    parser.add_argument(
        "--no-strip",
        action="store_true",
        help="Do not strip whitespace before counting chars (char mode only)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args(argv)

    try:
        rows, fieldnames = _load_csv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if args.column not in (fieldnames or (rows[0].keys() if rows else [])):
        print(f"Error: column '{args.column}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.mode == "word":
        out = word_count(rows, args.column, dest=args.dest, sep=args.sep)
    else:
        out = char_count(rows, args.column, dest=args.dest, strip=not args.no_strip)

    new_fields = list(out[0].keys()) if out else fieldnames
    _write_csv(out, new_fields, args.output)


if __name__ == "__main__":  # pragma: no cover
    run()
