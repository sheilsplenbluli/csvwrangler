"""CLI entry-point for z-score standardization."""
from __future__ import annotations

import argparse
import csv
import sys

from csvwrangler.zscore import zscore_column


def _load_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def _write_csv(path: str, fieldnames: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler zscore",
        description="Add z-score column(s) to a CSV.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument(
        "--col",
        required=True,
        action="append",
        dest="cols",
        metavar="COLUMN",
        help="Column to standardize (repeatable)",
    )
    parser.add_argument("--dest", help="Destination column name (single --col only)")
    parser.add_argument(
        "--decimals", type=int, default=4, help="Decimal places (default 4)"
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args(argv)

    if args.dest and len(args.cols) > 1:
        parser.error("--dest can only be used with a single --col")

    fieldnames, rows = _load_csv(args.input)
    if not rows:
        parser.error("Input CSV is empty")

    for col in args.cols:
        if col not in rows[0]:
            parser.error(f"Column not found: {col}")
        dest = args.dest if len(args.cols) == 1 else None
        rows = zscore_column(rows, col, dest=dest, decimals=args.decimals)

    # rebuild fieldnames to include new columns
    new_fields = list(rows[0].keys()) if rows else fieldnames

    if args.output:
        _write_csv(args.output, new_fields, rows)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":  # pragma: no cover
    run()
