"""CLI entry point for stack/unstack operations."""
import argparse
import csv
import sys
from typing import List, Dict, Any

from csvwrangler.pivot_stack import stack_columns, unstack_column


def _load_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, Any]], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(prog="csvwrangler pivot-stack", description="Stack or unstack CSV columns")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # stack sub-command
    sp = sub.add_parser("stack", help="Pivot value columns into variable/value rows")
    sp.add_argument("file", help="Input CSV file")
    sp.add_argument("--id-cols", required=True, help="Comma-separated id columns")
    sp.add_argument("--value-cols", required=True, help="Comma-separated value columns to stack")
    sp.add_argument("--var-col", default="variable", help="Name for variable column (default: variable)")
    sp.add_argument("--val-col", default="value", help="Name for value column (default: value)")
    sp.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    # unstack sub-command
    up = sub.add_parser("unstack", help="Pivot variable/value rows back to wide format")
    up.add_argument("file", help="Input CSV file")
    up.add_argument("--id-cols", required=True, help="Comma-separated id columns")
    up.add_argument("--var-col", default="variable", help="Column holding variable names")
    up.add_argument("--val-col", default="value", help="Column holding values")
    up.add_argument("--fill", default="", help="Fill value for missing cells")
    up.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    id_cols = [c.strip() for c in args.id_cols.split(",")]

    if args.cmd == "stack":
        value_cols = [c.strip() for c in args.value_cols.split(",")]
        result = stack_columns(rows, id_cols=id_cols, value_cols=value_cols,
                               var_col=args.var_col, val_col=args.val_col)
    else:
        result = unstack_column(rows, id_cols=id_cols, var_col=args.var_col,
                                val_col=args.val_col, fill=args.fill)

    if not result:
        return

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)
