"""CLI entry point for the resample command."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.resample import resample_rows


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, str]], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler resample",
        description="Resample time-series rows by date frequency.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--date-col", required=True, help="Column containing dates")
    parser.add_argument(
        "--freq",
        required=True,
        choices=["Y", "M", "W", "D"],
        help="Resampling frequency: Y=yearly, M=monthly, W=weekly, D=daily",
    )
    parser.add_argument("--agg-col", required=True, help="Numeric column to aggregate")
    parser.add_argument(
        "--agg",
        default="sum",
        choices=["sum", "mean", "count", "min", "max"],
        help="Aggregation function (default: sum)",
    )
    parser.add_argument("--dest", default=None, help="Output column name (default: <agg_col>_<agg>)")
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.input)
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        result = resample_rows(
            rows,
            date_col=args.date_col,
            freq=args.freq,
            agg_col=args.agg_col,
            agg=args.agg,
            dest=args.dest,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result:
        print("Warning: no rows produced.", file=sys.stderr)
        return

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
