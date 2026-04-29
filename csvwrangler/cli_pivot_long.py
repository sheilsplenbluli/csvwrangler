"""CLI entry point for wide<->long reshaping."""
import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.pivot_long import wide_to_long, long_to_wide


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
        prog="csvwrangler pivot-long",
        description="Reshape CSV between wide and long formats.",
    )
    sub = parser.add_subparsers(dest="direction", required=True)

    # wide -> long
    p_wtl = sub.add_parser("wide-to-long", help="Convert wide format to long.")
    p_wtl.add_argument("file", help="Input CSV file.")
    p_wtl.add_argument("--id-cols", required=True, help="Comma-separated id columns.")
    p_wtl.add_argument("--value-cols", default=None, help="Comma-separated value columns (default: all non-id).")
    p_wtl.add_argument("--var-name", default="variable", help="Name for variable column.")
    p_wtl.add_argument("--val-name", default="value", help="Name for value column.")
    p_wtl.add_argument("--output", "-o", default=None, help="Output file (default: stdout).")

    # long -> wide
    p_ltw = sub.add_parser("long-to-wide", help="Convert long format to wide.")
    p_ltw.add_argument("file", help="Input CSV file.")
    p_ltw.add_argument("--id-cols", required=True, help="Comma-separated id columns.")
    p_ltw.add_argument("--var-col", required=True, help="Column holding variable names.")
    p_ltw.add_argument("--val-col", required=True, help="Column holding values.")
    p_ltw.add_argument("--fill", default="", help="Fill value for missing cells.")
    p_ltw.add_argument("--output", "-o", default=None, help="Output file (default: stdout).")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    id_cols = [c.strip() for c in args.id_cols.split(",")]

    if args.direction == "wide-to-long":
        value_cols = (
            [c.strip() for c in args.value_cols.split(",")]
            if args.value_cols
            else None
        )
        result = wide_to_long(
            rows,
            id_cols=id_cols,
            value_cols=value_cols,
            var_name=args.var_name,
            val_name=args.val_name,
        )
    else:
        result = long_to_wide(
            rows,
            id_cols=id_cols,
            var_col=args.var_col,
            val_col=args.val_col,
            fill=args.fill,
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
