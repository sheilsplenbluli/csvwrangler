"""CLI entry-point for the fillna command."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csvwrangler.fillna import fill_many


def _load_csv(path: str):
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, list(fieldnames)


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv: List[str] | None = None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler fillna",
        description="Fill empty values in CSV columns.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("-o", "--output", help="Output CSV file (default: stdout)")
    parser.add_argument(
        "-f",
        "--fill",
        action="append",
        metavar="COL:METHOD[:VALUE]",
        required=True,
        help=(
            "Fill spec: COL:value:TEXT  |  COL:forward  |  COL:backward. "
            "Repeat for multiple columns."
        ),
    )

    args = parser.parse_args(argv)

    fills = []
    for spec in args.fill:
        parts = spec.split(":", 2)
        if len(parts) < 2:
            print(f"Bad fill spec: {spec!r}", file=sys.stderr)
            sys.exit(1)
        col, method = parts[0], parts[1]
        val = parts[2] if len(parts) == 3 else ""
        fills.append({"column": col, "method": method, "value": val})

    rows, fieldnames = _load_csv(args.input)

    try:
        result = fill_many(rows, fills)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        _write_csv(args.output, result, fieldnames)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
