"""CLI entry point for lag/lead column operations."""

import argparse
import csv
import sys
from csvwrangler.lag import lag_column, lead_column


def _load_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _write_csv(rows, path):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler lag",
        description="Add lagged or lead columns to a CSV.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("column", help="Column to lag/lead")
    parser.add_argument(
        "--direction",
        choices=["lag", "lead"],
        default="lag",
        help="Direction: lag (look back) or lead (look ahead). Default: lag",
    )
    parser.add_argument(
        "--periods",
        type=int,
        default=1,
        help="Number of periods to shift. Default: 1",
    )
    parser.add_argument(
        "--dest",
        default=None,
        help="Destination column name (default: auto-generated)",
    )
    parser.add_argument(
        "--fill",
        default="",
        help="Fill value for out-of-bounds positions. Default: empty string",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file")

    args = parser.parse_args(argv)

    if args.periods < 1:
        print("error: --periods must be >= 1", file=sys.stderr)
        sys.exit(1)

    rows = _load_csv(args.input)
    if not rows:
        return

    if args.direction == "lead":
        result = lead_column(
            rows, args.column, periods=args.periods, dest=args.dest, fill=args.fill
        )
    else:
        result = lag_column(
            rows, args.column, periods=args.periods, dest=args.dest, fill=args.fill
        )

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=result[0].keys())
        writer.writeheader()
        writer.writerows(result)
