"""CLI entry-point for the compare command."""
from __future__ import annotations

import argparse
import csv
import sys

from csvwrangler.compare import compare_columns


def _load_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return fieldnames, rows


def _write_csv(rows: list[dict], fieldnames: list[str], dest: str | None) -> None:
    out = open(dest, "w", newline="", encoding="utf-8") if dest else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if dest:
            out.close()


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler compare",
        description="Add a column comparing two existing columns.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--col-a", required=True, help="First column")
    parser.add_argument("--col-b", required=True, help="Second column")
    parser.add_argument("--dest", default="_cmp", help="Output column name (default: _cmp)")
    parser.add_argument(
        "--mode",
        default="diff",
        choices=["diff", "ratio", "eq", "gt", "lt"],
        help="Comparison mode (default: diff)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    fieldnames, rows = _load_csv(args.input)

    for col in (args.col_a, args.col_b):
        if col not in fieldnames:
            print(f"error: column {col!r} not found in input", file=sys.stderr)
            sys.exit(1)

    result = compare_columns(rows, args.col_a, args.col_b, dest=args.dest, mode=args.mode)
    out_fields = fieldnames + ([args.dest] if args.dest not in fieldnames else [])
    _write_csv(result, out_fields, args.output)


if __name__ == "__main__":
    run()
