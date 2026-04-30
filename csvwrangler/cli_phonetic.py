"""CLI entry-point for phonetic encoding (soundex / metaphone)."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.phonetic import soundex_column, metaphone_column


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, str]], path: str | None) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    dest = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            dest.close()


def run(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler phonetic",
        description="Add phonetic encoding columns (soundex or metaphone).",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument(
        "--col",
        required=True,
        dest="cols",
        action="append",
        metavar="COLUMN",
        help="Column to encode (repeatable)",
    )
    parser.add_argument(
        "--method",
        choices=["soundex", "metaphone"],
        default="soundex",
        help="Encoding method (default: soundex)",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination column name (only used when a single --col is given)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    cols = args.cols
    dest = args.dest if len(cols) == 1 else None

    for col in cols:
        if col not in (rows[0] if rows else {}):
            print(f"error: column not found: {col}", file=sys.stderr)
            sys.exit(1)
        if args.method == "metaphone":
            rows = metaphone_column(rows, col, dest)
        else:
            rows = soundex_column(rows, col, dest)

    _write_csv(rows, args.output)


if __name__ == "__main__":  # pragma: no cover
    run()
