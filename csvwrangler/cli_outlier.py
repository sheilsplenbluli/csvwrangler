"""CLI entry point for outlier detection."""
from __future__ import annotations
import argparse
import csv
import sys
from csvwrangler.outlier import flag_outliers, filter_outliers


def _load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def _write_csv(rows, fieldnames, path=None):
    out = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    if path:
        out.close()


def run(argv=None):
    parser = argparse.ArgumentParser(prog="csvwrangler outlier", description="Detect outliers in a CSV column.")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--column", required=True, help="Column to analyse")
    parser.add_argument("--method", choices=["iqr", "zscore"], default="iqr")
    parser.add_argument("--factor", type=float, default=1.5, help="IQR multiplier or z-score threshold")
    parser.add_argument(
        "--mode",
        choices=["flag", "keep", "remove"],
        default="flag",
        help="flag=add column, keep=only outliers, remove=drop outliers",
    )
    parser.add_argument("--flag-column", default="_outlier", help="Name for the flag column (flag mode)")
    parser.add_argument("--output", default=None, help="Output CSV file (default: stdout)")
    args = parser.parse_args(argv)

    rows, fieldnames = _load_csv(args.input)

    if args.column not in fieldnames:
        print(f"Error: column '{args.column}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.mode == "flag":
        result = flag_outliers(rows, args.column, args.method, args.factor, args.flag_column)
        out_fields = list(fieldnames) + ([args.flag_column] if args.flag_column not in fieldnames else [])
    elif args.mode == "keep":
        result = filter_outliers(rows, args.column, args.method, args.factor, keep=True)
        out_fields = list(fieldnames)
    else:
        result = filter_outliers(rows, args.column, args.method, args.factor, keep=False)
        out_fields = list(fieldnames)

    _write_csv(result, out_fields, args.output)


if __name__ == "__main__":
    run()
