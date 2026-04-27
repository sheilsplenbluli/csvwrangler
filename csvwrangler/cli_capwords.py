"""cli_capwords.py – CLI entry-point for the capwords subcommand.

Usage examples::

    csvwrangler capwords input.csv --column name --mode title
    csvwrangler capwords input.csv --column name --mode upper --dest name_upper -o out.csv
    csvwrangler capwords input.csv --column name --column city --mode lower
"""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvwrangler.capwords import capwords_column


def _load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def _write_csv(rows, fieldnames, path: str | None):
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
        prog="csvwrangler capwords",
        description="Capitalize / title-case / sentence-case CSV column values.",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument(
        "--column", "-c",
        action="append",
        dest="columns",
        required=True,
        metavar="COL",
        help="Column(s) to transform (repeat for multiple).",
    )
    parser.add_argument(
        "--mode", "-m",
        default="title",
        choices=["title", "upper", "lower", "sentence"],
        help="Capitalization mode (default: title).",
    )
    parser.add_argument(
        "--dest", "-d",
        default=None,
        metavar="DEST",
        help="Destination column name (only valid when a single --column is given).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        metavar="FILE",
        help="Write output to FILE instead of stdout.",
    )

    args = parser.parse_args(argv)

    if args.dest and len(args.columns) > 1:
        parser.error("--dest can only be used when a single --column is specified.")

    try:
        rows, fieldnames = _load_csv(args.file)
    except FileNotFoundError:
        sys.stderr.write(f"error: file not found: {args.file}\n")
        sys.exit(1)

    result = rows
    for col in args.columns:
        dest = args.dest if len(args.columns) == 1 else None
        result = capwords_column(result, column=col, mode=args.mode, dest=dest)
        # update fieldnames if a new dest column was introduced
        effective_dest = dest if dest else col
        if effective_dest not in fieldnames:
            fieldnames = fieldnames + [effective_dest]

    _write_csv(result, fieldnames, args.output)


if __name__ == "__main__":  # pragma: no cover
    run()
