"""CLI entry-point for sorting CSV rows."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional

from csvwrangler.sort import sort_rows


def _load_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return list(fieldnames), rows


def _write_csv(fieldnames: list[str], rows: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler sort",
        description="Sort CSV rows by one or more columns.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument(
        "-k", "--keys",
        required=True,
        nargs="+",
        metavar="COL",
        help="Column(s) to sort by (in priority order)",
    )
    parser.add_argument(
        "--desc",
        action="store_true",
        default=False,
        help="Sort descending",
    )
    parser.add_argument(
        "--case-sensitive",
        action="store_true",
        default=False,
        help="Use case-sensitive string comparison",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    fieldnames, rows = _load_csv(args.input)
    sorted_rows = sort_rows(
        rows,
        keys=args.keys,
        descending=args.desc,
        case_sensitive=args.case_sensitive,
    )

    if args.output:
        _write_csv(fieldnames, sorted_rows, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)


if __name__ == "__main__":
    run()
