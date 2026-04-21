"""CLI entry-point for cumulative (running) aggregations."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.rolling import cumulative_sum, cumulative_min, cumulative_max, cumulative_mean

_FUNCS = {
    "sum": cumulative_sum,
    "min": cumulative_min,
    "max": cumulative_max,
    "mean": cumulative_mean,
}


def _load_csv(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler rolling",
        description="Add a cumulative aggregation column to a CSV.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--func", choices=list(_FUNCS), default="sum",
                        help="Aggregation function (default: sum)")
    parser.add_argument("--column", required=True, help="Column to aggregate")
    parser.add_argument("--dest", default="", help="Destination column name (optional)")
    parser.add_argument("--output", "-o", default="", help="Output file (default: stdout)")
    args = parser.parse_args(argv)

    rows = _load_csv(args.input)
    if rows and args.column not in rows[0]:
        print(f"Error: column '{args.column}' not found in input.", file=sys.stderr)
        sys.exit(1)

    fn = _FUNCS[args.func]
    result = fn(rows, args.column, dest=args.dest)

    if args.output:
        _write_csv(result, args.output)
    else:
        if result:
            writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
            writer.writeheader()
            writer.writerows(result)


if __name__ == "__main__":
    run()
