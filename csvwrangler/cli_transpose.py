"""CLI entry-point for the transpose command."""
import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.transpose import transpose_rows, pivot_transpose


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
        prog="csvwrangler transpose",
        description="Transpose CSV rows<->columns or pivot key/value pairs.",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    # --- flip sub-command ---
    flip = sub.add_parser("flip", help="Transpose rows to columns")
    flip.add_argument("input", help="Input CSV file")
    flip.add_argument("--header-col", default="field",
                      help="Name for the field-name column (default: field)")
    flip.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    # --- pivot sub-command ---
    pvt = sub.add_parser("pivot", help="Pivot key/value rows into a wide row")
    pvt.add_argument("input", help="Input CSV file")
    pvt.add_argument("--key", required=True, help="Column to use as keys")
    pvt.add_argument("--value", required=True, help="Column to use as values")
    pvt.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    args = parser.parse_args(argv)
    rows = _load_csv(args.input)

    if args.mode == "flip":
        result = transpose_rows(rows, header_col=args.header_col)
    else:
        result = pivot_transpose(rows, key_col=args.key, value_col=args.value)

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
