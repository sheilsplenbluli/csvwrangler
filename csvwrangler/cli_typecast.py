"""CLI entry-point for typecast command."""
from __future__ import annotations
import argparse
import csv
import sys
from csvwrangler.typecast import typecast_many


def _load_csv(path: str):
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader), reader.fieldnames or []


def _write_csv(rows, fieldnames, path):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler typecast",
        description="Cast column values to a given type.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument(
        "--cast",
        metavar="COL:TYPE",
        action="append",
        required=True,
        help="column:type pair, e.g. age:int. Repeatable.",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    args = parser.parse_args(argv)

    spec: dict[str, str] = {}
    for item in args.cast:
        if ":" not in item:
            print(f"Invalid --cast spec {item!r}; expected COL:TYPE", file=sys.stderr)
            sys.exit(1)
        col, cast_type = item.split(":", 1)
        spec[col] = cast_type

    try:
        rows, fieldnames = _load_csv(args.input)
        out_rows = typecast_many(rows, spec)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        _write_csv(out_rows, fieldnames, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)


if __name__ == "__main__":
    run()
