"""CLI entry-point for the merge command."""
import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.merge import merge_rows

Row = Dict[str, str]


def _load_csv(path: str) -> List[Row]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Row], fieldnames: List[str], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler merge",
        description="Stack multiple CSV files vertically.",
    )
    parser.add_argument("inputs", nargs="+", metavar="FILE", help="CSV files to merge")
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    parser.add_argument("--fill", default="", help="Fill value for missing columns (default: empty)")
    parser.add_argument(
        "--fields",
        default=None,
        help="Comma-separated explicit column order",
    )
    args = parser.parse_args(argv)

    datasets = []
    for path in args.inputs:
        try:
            datasets.append(_load_csv(path))
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    fieldnames = [f.strip() for f in args.fields.split(",")] if args.fields else None
    rows = merge_rows(datasets, fill=args.fill, fieldnames=fieldnames)

    if not rows:
        if args.output is None:
            print("")
        return

    out_fields = fieldnames if fieldnames else list(rows[0].keys())

    if args.output:
        _write_csv(rows, out_fields, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    run()
