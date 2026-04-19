"""CLI entry-point: csvwrangler frequency"""
import argparse
import csv
import sys
from csvwrangler.frequency import frequency_table, frequency_all


def _load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _print_table(rows, file=sys.stdout):
    if not rows:
        return
    headers = list(rows[0].keys())
    col_widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}
    header_line = "  ".join(h.ljust(col_widths[h]) for h in headers)
    print(header_line, file=file)
    print("-" * len(header_line), file=file)
    for row in rows:
        print("  ".join(str(row[h]).ljust(col_widths[h]) for h in headers), file=file)


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler frequency",
        description="Show value frequency distribution for CSV columns.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--column", "-c", help="Column to analyse (omit for all)")
    parser.add_argument("--top", "-n", type=int, default=None, help="Show top N values")
    parser.add_argument(
        "--sort",
        choices=["count", "value"],
        default="count",
        help="Sort order (default: count)",
    )
    args = parser.parse_args(argv)

    rows = _load_csv(args.input)

    if args.column:
        if args.column not in (rows[0].keys() if rows else []):
            print(f"Error: column '{args.column}' not found.", file=sys.stderr)
            sys.exit(1)
        result = frequency_table(rows, args.column, top_n=args.top, sort_by=args.sort)
        print(f"\nColumn: {args.column}")
        _print_table(result)
    else:
        all_freq = frequency_all(rows, top_n=args.top)
        for col, table in all_freq.items():
            print(f"\nColumn: {col}")
            _print_table(table)


if __name__ == "__main__":
    run()
