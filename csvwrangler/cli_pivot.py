"""CLI entry point for pivot/melt operations."""
import argparse
import csv
import sys
from typing import List, Dict, Any

from csvwrangler.pivot import pivot_rows, melt_rows


def _load_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def run(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler-pivot",
        description="Pivot or melt a CSV file.",
    )
    parser.add_argument("file", help="Input CSV file")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pivot = sub.add_parser("pivot", help="Pivot rows into columns")
    p_pivot.add_argument("--index", required=True, help="Column to use as row index")
    p_pivot.add_argument("--columns", required=True, help="Column whose values become headers")
    p_pivot.add_argument("--values", required=True, help="Column to aggregate")
    p_pivot.add_argument(
        "--aggfunc",
        default="first",
        choices=["first", "last", "sum", "count"],
        help="Aggregation function (default: first)",
    )

    p_melt = sub.add_parser("melt", help="Unpivot columns into rows")
    p_melt.add_argument(
        "--id-vars", required=True, help="Comma-separated columns to keep as identifiers"
    )
    p_melt.add_argument(
        "--value-vars", default=None, help="Comma-separated columns to unpivot (default: all others)"
    )
    p_melt.add_argument("--var-name", default="variable", help="Name for the variable column")
    p_melt.add_argument("--value-name", default="value", help="Name for the value column")

    args = parser.parse_args(argv)
    rows = _load_csv(args.file)

    if args.cmd == "pivot":
        result = pivot_rows(
            rows,
            index=args.index,
            columns=args.columns,
            values=args.values,
            aggfunc=args.aggfunc,
        )
    else:
        id_vars = [v.strip() for v in args.id_vars.split(",")]
        value_vars = (
            [v.strip() for v in args.value_vars.split(",")] if args.value_vars else None
        )
        result = melt_rows(
            rows,
            id_vars=id_vars,
            value_vars=value_vars,
            var_name=args.var_name,
            value_name=args.value_name,
        )

    _write_csv(result)


if __name__ == "__main__":
    run()
