"""CLI entry point for rolling window calculations."""
import argparse
import csv
import sys
from csvwrangler.window import rolling_mean, rolling_sum, rolling_min, rolling_max

_FNS = {"mean": rolling_mean, "sum": rolling_sum, "min": rolling_min, "max": rolling_max}


def _load_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(rows, path):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(prog="csvwrangler window", description="Rolling window calculations")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--col", required=True, help="Column to compute over")
    parser.add_argument("--func", choices=list(_FNS), default="mean", help="Aggregation function")
    parser.add_argument("--window", type=int, default=3, help="Window size")
    parser.add_argument("--dest", default=None, help="Destination column name")
    parser.add_argument("--output", default=None, help="Output CSV file (default: stdout)")
    args = parser.parse_args(argv)

    rows = _load_csv(args.input)
    if not rows:
        sys.exit("Input file is empty.")
    if args.col not in rows[0]:
        sys.exit(f"Column '{args.col}' not found in input.")
    if args.window < 1:
        sys.exit("Window size must be >= 1.")

    fn = _FNS[args.func]
    result = fn(rows, args.col, args.window, dest=args.dest)

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
