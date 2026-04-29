"""CLI entry point for the pivot-wide (spread) command."""
import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.pivot_wide import spread_rows


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
        prog="csvwrangler pivot-wide",
        description="Reshape long-format CSV into wide format by spreading a key column.",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument(
        "--index", required=True, metavar="COL",
        help="Column that identifies each output row",
    )
    parser.add_argument(
        "--key", required=True, metavar="COL",
        help="Column whose values become new column headers",
    )
    parser.add_argument(
        "--value", required=True, metavar="COL",
        help="Column whose values populate the new columns",
    )
    parser.add_argument(
        "--fill", default="", metavar="STR",
        help="Value to use for missing combinations (default: empty string)",
    )
    parser.add_argument(
        "--agg", choices=["first", "last", "sum"], default="first",
        help="Aggregation for duplicate index+key pairs (default: first)",
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE",
        help="Write output to FILE instead of stdout",
    )

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = spread_rows(
        rows,
        index_col=args.index,
        key_col=args.key,
        value_col=args.value,
        fill=args.fill,
        agg=args.agg,
    )

    if not result:
        return

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=list(result[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
