"""CLI entry-point for the enrich command."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from csvwrangler.enrich import add_column, add_row_number


def _load_csv(path: str) -> tuple[list[dict], list[str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def _write_csv(rows: list[dict], fieldnames: list[str], dest: str | None) -> None:
    out = open(dest, "w", newline="", encoding="utf-8") if dest else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if dest:
            out.close()


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler enrich",
        description="Add computed columns to a CSV file.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("-o", "--output", help="Output CSV file (default: stdout)")

    sub = parser.add_subparsers(dest="subcmd", required=True)

    col_p = sub.add_parser("add-column", help="Add a computed column")
    col_p.add_argument("name", help="New column name")
    col_p.add_argument("expr", help="Template or math expression using {field} syntax")
    col_p.add_argument(
        "--mode",
        choices=["template", "math"],
        default="template",
        help="Evaluation mode (default: template)",
    )

    sub.add_parser("add-rownum", help="Add a sequential row-number column")

    args = parser.parse_args(argv)
    rows, fieldnames = _load_csv(args.input)

    if args.subcmd == "add-column":
        rows = add_column(rows, args.name, args.expr, mode=args.mode)
        if args.name not in fieldnames:
            fieldnames = fieldnames + [args.name]
    else:
        rows = add_row_number(rows)
        fieldnames = ["row_num"] + fieldnames

    _write_csv(rows, fieldnames, args.output)


if __name__ == "__main__":
    run()
