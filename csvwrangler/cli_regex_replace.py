"""CLI entry point for regex find-and-replace on CSV columns."""

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.regex_replace import regex_replace


def _load_csv(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler regex-replace",
        description="Apply a regex find-and-replace to a CSV column.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--column", required=True, help="Column to search")
    parser.add_argument("--pattern", required=True, help="Regex pattern")
    parser.add_argument("--replacement", required=True, help="Replacement string")
    parser.add_argument(
        "--dest", default=None, help="Destination column (default: overwrite source)"
    )
    parser.add_argument(
        "--ignore-case", action="store_true", help="Case-insensitive matching"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Max substitutions per value (0 = unlimited)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file")

    args = parser.parse_args(argv)

    if not __import__("os").path.exists(args.input):
        print(f"error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    rows = _load_csv(args.input)

    if args.column not in (rows[0].keys() if rows else []):
        print(f"error: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        result = regex_replace(
            rows,
            column=args.column,
            pattern=args.pattern,
            replacement=args.replacement,
            dest=args.dest,
            ignore_case=args.ignore_case,
            count=args.count,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=result[0].keys() if result else [])
        writer.writeheader()
        writer.writerows(result)
