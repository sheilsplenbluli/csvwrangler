"""CLI entry point for cross-join and set-style joins."""
from __future__ import annotations
import argparse
import csv
import sys
from csvwrangler.crossjoin import cross_join, anti_join, semi_join


def _load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(rows, path: str | None):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    out = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            out.close()


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler crossjoin",
        description="Cross-join or set-style join two CSV files.",
    )
    parser.add_argument("left", help="Left CSV file")
    parser.add_argument("right", help="Right CSV file")
    parser.add_argument(
        "--mode",
        choices=["cross", "anti", "semi"],
        default="cross",
        help="Join mode (default: cross)",
    )
    parser.add_argument(
        "--keys",
        help="Comma-separated key columns (required for anti/semi)",
    )
    parser.add_argument("-o", "--output", help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    if args.mode in ("anti", "semi") and not args.keys:
        parser.error("--keys is required for anti and semi join modes")

    left_rows = _load_csv(args.left)
    right_rows = _load_csv(args.right)

    if args.mode == "cross":
        result = cross_join(left_rows, right_rows)
    elif args.mode == "anti":
        keys = [k.strip() for k in args.keys.split(",")]
        result = anti_join(left_rows, right_rows, keys)
    else:  # semi
        keys = [k.strip() for k in args.keys.split(",")]
        result = semi_join(left_rows, right_rows, keys)

    _write_csv(result, args.output)


if __name__ == "__main__":
    run()
