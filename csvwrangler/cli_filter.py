"""CLI entry point for filtering CSV rows."""

import csv
import sys
from csvwrangler.filters import build_filter, apply_filters


def _load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, fieldnames


def _write_csv(rows, fieldnames, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(args):
    """args: Namespace with input, output, filter (list of col:op:val strings)."""
    rows, fieldnames = _load_csv(args.input)

    predicates = []
    for spec in args.filter or []:
        parts = spec.split(":", 2)
        if len(parts) != 3:
            print(f"Invalid filter spec '{spec}'. Expected col:op:val.", file=sys.stderr)
            sys.exit(1)
        col, op, val = parts
        try:
            predicates.append(build_filter(col, op, val))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

    filtered = apply_filters(rows, predicates)

    if args.output:
        _write_csv(filtered, fieldnames, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered)
