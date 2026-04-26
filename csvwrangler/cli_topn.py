"""CLI entry point for top-N / bottom-N row selection."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.topn import top_n, bottom_n


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, str]], dest) -> None:
    if not rows:
        return
    writer = csv.DictWriter(dest, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def run(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler topn",
        description="Select the top or bottom N rows by a numeric column.",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument("column", help="Column to rank by")
    parser.add_argument("n", type=int, help="Number of rows to return")
    parser.add_argument(
        "--mode",
        choices=["top", "bottom"],
        default="top",
        help="Return top (default) or bottom rows",
    )
    parser.add_argument(
        "--keep-ties",
        action="store_true",
        default=False,
        help="Include all rows tied at the boundary",
    )
    parser.add_argument("-o", "--output", help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if args.column not in (rows[0].keys() if rows else []):
        print(f"error: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)

    fn = top_n if args.mode == "top" else bottom_n
    result = fn(rows, args.column, args.n, keep_ties=args.keep_ties)

    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            _write_csv(result, fh)
    else:
        _write_csv(result, sys.stdout)


if __name__ == "__main__":
    run()
