"""CLI entry point for pivot-agg command."""
import argparse
import csv
import sys
from csvwrangler.pivot_agg import pivot_agg

_AGGFUNCS = ("sum", "mean", "count", "min", "max", "first", "last")


def _load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _write_csv(rows, path: str):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler pivot-agg",
        description="Pivot rows: group by index column, spread column values as headers.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--index", required=True, help="Column to use as row index")
    parser.add_argument("--columns", required=True, help="Column whose values become headers")
    parser.add_argument("--values", required=True, help="Column to aggregate")
    parser.add_argument(
        "--aggfunc",
        default="sum",
        choices=_AGGFUNCS,
        help="Aggregation function (default: sum)",
    )
    parser.add_argument(
        "--fill-value",
        default="",
        dest="fill_value",
        help="Value for missing cells (default: empty string)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.input)
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    result = pivot_agg(
        rows,
        index=args.index,
        columns=args.columns,
        values=args.values,
        aggfunc=args.aggfunc,
        fill_value=args.fill_value,
    )

    if not result:
        return

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
