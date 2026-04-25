"""CLI entry point for date parsing operations."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.dateparse import extract_parts, format_date, date_diff


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


def _print_rows(rows: List[Dict[str, str]]) -> None:
    if not rows:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="csvwrangler dateparse", description="Date parsing utilities")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("-o", "--output", help="Output file (default: stdout)")
    sub = p.add_subparsers(dest="cmd", required=True)

    ep = sub.add_parser("extract", help="Extract date parts into new columns")
    ep.add_argument("--column", required=True, help="Date column")
    ep.add_argument("--parts", required=True, help="Comma-separated parts: year,month,day,weekday,quarter")
    ep.add_argument("--prefix", default="", help="Prefix for new column names")

    fp = sub.add_parser("format", help="Reformat a date column")
    fp.add_argument("--column", required=True, help="Date column")
    fp.add_argument("--fmt", required=True, help="strftime format string")
    fp.add_argument("--dest", default=None, help="Destination column (default: overwrite source)")

    dp = sub.add_parser("diff", help="Compute difference between two date columns")
    dp.add_argument("--col-a", required=True, dest="col_a", help="First date column")
    dp.add_argument("--col-b", required=True, dest="col_b", help="Second date column")
    dp.add_argument("--unit", default="days", choices=["days", "hours", "seconds"])
    dp.add_argument("--dest", default=None, help="Destination column name")

    return p


def run(argv=None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.cmd == "extract":
            parts = [p.strip() for p in args.parts.split(",")]
            result = extract_parts(rows, args.column, parts, prefix=args.prefix)
        elif args.cmd == "format":
            result = format_date(rows, args.column, args.fmt, dest=args.dest)
        else:
            result = date_diff(rows, args.col_a, args.col_b, unit=args.unit, dest=args.dest)
    except (ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        _write_csv(result, args.output)
    else:
        _print_rows(result)


if __name__ == "__main__":  # pragma: no cover
    run()
