"""CLI entry point for binning numeric columns."""
from __future__ import annotations
import argparse
import csv
import sys
from csvwrangler.bin import bin_column


def _load_csv(path: str) -> tuple[list[str], list[dict]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return list(fieldnames), rows


def _write_csv(fieldnames: list[str], rows: list[dict], path: str | None) -> None:
    out = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            out.close()


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler-bin",
        description="Bin a numeric column into labeled buckets.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--column", required=True, help="Column to bin")
    parser.add_argument(
        "--edges",
        required=True,
        help="Comma-separated edge values, e.g. 10,20,30",
    )
    parser.add_argument(
        "--labels",
        default=None,
        help="Comma-separated labels (must be len(edges)+1)",
    )
    parser.add_argument("--dest", default=None, help="Destination column name")
    parser.add_argument("--default", default="", help="Value for non-numeric rows")
    parser.add_argument("-o", "--output", default=None, help="Output CSV file")

    args = parser.parse_args(argv)

    try:
        edges = [float(e.strip()) for e in args.edges.split(",")]
    except ValueError:
        print("ERROR: --edges must be comma-separated numbers", file=sys.stderr)
        sys.exit(1)

    labels = [l.strip() for l in args.labels.split(",")] if args.labels else None

    fieldnames, rows = _load_csv(args.input)

    if args.column not in fieldnames:
        print(f"ERROR: column '{args.column}' not found", file=sys.stderr)
        sys.exit(1)

    try:
        result = bin_column(rows, args.column, edges, labels=labels, dest=args.dest, default=args.default)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    out_col = args.dest or f"{args.column}_bin"
    out_fields = fieldnames + ([out_col] if out_col not in fieldnames else [])
    _write_csv(out_fields, result, args.output)


if __name__ == "__main__":
    run()
