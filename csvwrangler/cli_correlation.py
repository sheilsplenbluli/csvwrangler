"""CLI entry-point for correlation computation."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.correlation import correlate_pair, correlate_matrix, correlate_all


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _print_table(rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def run(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler-correlation",
        description="Compute Pearson correlation between numeric columns.",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument(
        "--cols",
        nargs="+",
        metavar="COL",
        help="Columns to include (default: all numeric)",
    )
    parser.add_argument(
        "--pair",
        nargs=2,
        metavar=("COL_A", "COL_B"),
        help="Compute correlation for a single pair",
    )
    parser.add_argument("-o", "--output", help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)
    rows = _load_csv(args.file)

    if args.pair:
        results = [correlate_pair(rows, args.pair[0], args.pair[1])]
    elif args.cols:
        results = correlate_matrix(rows, args.cols)
    else:
        results = correlate_all(rows)

    if not results:
        print("No numeric column pairs found.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(results[0].keys()))
            writer.writeheader()
            writer.writerows(results)
    else:
        _print_table(results)


if __name__ == "__main__":  # pragma: no cover
    run()
