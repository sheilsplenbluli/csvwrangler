"""CLI entry-point for the split command."""
from __future__ import annotations
import argparse
import csv
import os
import sys

from csvwrangler.split import split_by_column, split_by_row_count


def _load_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return list(fieldnames), rows


def _write_csv(path: str, fieldnames: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler split",
        description="Split a CSV into multiple files.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--outdir", default=".", help="Output directory (default: .)")
    parser.add_argument("--prefix", default="part", help="Output filename prefix")

    sub = parser.add_subparsers(dest="mode", required=True)

    col_p = sub.add_parser("column", help="Split by column value")
    col_p.add_argument("column", help="Column name to split on")

    chunk_p = sub.add_parser("chunk", help="Split into fixed-size chunks")
    chunk_p.add_argument("size", type=int, help="Rows per chunk")

    args = parser.parse_args(argv)
    fieldnames, rows = _load_csv(args.input)
    os.makedirs(args.outdir, exist_ok=True)

    if args.mode == "column":
        if args.column not in fieldnames:
            print(f"error: column '{args.column}' not found", file=sys.stderr)
            sys.exit(1)
        groups = split_by_column(rows, args.column)
        for value, group_rows in groups.items():
            safe = value.replace(os.sep, "_") or "__empty__"
            out_path = os.path.join(args.outdir, f"{args.prefix}_{safe}.csv")
            _write_csv(out_path, fieldnames, group_rows)
            print(f"wrote {len(group_rows)} rows -> {out_path}")
    else:
        try:
            chunks = split_by_row_count(rows, args.size)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        for idx, chunk in enumerate(chunks, 1):
            out_path = os.path.join(args.outdir, f"{args.prefix}_{idx:04d}.csv")
            _write_csv(out_path, fieldnames, chunk)
            print(f"wrote {len(chunk)} rows -> {out_path}")


if __name__ == "__main__":
    run()
