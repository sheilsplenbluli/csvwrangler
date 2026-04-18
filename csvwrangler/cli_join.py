"""CLI entry-point for join operations."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.join import join_rows


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, str]], out) -> None:
    if not rows:
        return
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def run(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler-join",
        description="Join two CSV files on a common key column.",
    )
    parser.add_argument("left", help="Path to the left CSV file")
    parser.add_argument("right", help="Path to the right CSV file")
    parser.add_argument(
        "--on",
        required=True,
        metavar="COLUMN",
        help="Column name to join on (must exist in both files)",
    )
    parser.add_argument(
        "--how",
        choices=["inner", "left", "right"],
        default="inner",
        help="Join type (default: inner)",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )

    args = parser.parse_args(argv)

    left_rows = _load_csv(args.left)
    right_rows = _load_csv(args.right)

    result = join_rows(left_rows, right_rows, key=args.on, how=args.how)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result, fh)
    else:
        _write_csv(result, sys.stdout)


if __name__ == "__main__":
    run()
