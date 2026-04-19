"""CLI entry-point for column-rename operations."""
from __future__ import annotations

import argparse
import csv
import sys
from io import StringIO

from csvwrangler.rename import rename_columns, rename_prefix, rename_strip, rename_pattern


def _load_csv(path: str):
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _write_csv(rows, path: str | None):
    if not rows:
        return
    out = open(path, "w", newline="") if path else sys.stdout
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    if path:
        out.close()


def run(argv=None):
    parser = argparse.ArgumentParser(prog="csvwrangler rename", description="Rename CSV columns")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")

    sub = parser.add_subparsers(dest="mode", required=True)

    p_map = sub.add_parser("map", help="Explicit old=new mapping")
    p_map.add_argument("pairs", nargs="+", metavar="OLD=NEW")

    p_pre = sub.add_parser("prefix", help="Add prefix to column names")
    p_pre.add_argument("prefix")
    p_pre.add_argument("--columns", nargs="+", default=None)

    p_strip = sub.add_parser("strip", help="Strip whitespace from column names")
    p_strip.add_argument("--chars", default=None)

    p_pat = sub.add_parser("pattern", help="Regex substitution on column names")
    p_pat.add_argument("pattern")
    p_pat.add_argument("replacement")

    args = parser.parse_args(argv)
    rows = _load_csv(args.input)

    if args.mode == "map":
        mapping = {}
        for pair in args.pairs:
            if "=" not in pair:
                print(f"Invalid pair (expected OLD=NEW): {pair}", file=sys.stderr)
                sys.exit(1)
            old, new = pair.split("=", 1)
            mapping[old] = new
        rows = rename_columns(rows, mapping)

    elif args.mode == "prefix":
        rows = rename_prefix(rows, args.prefix, columns=args.columns)

    elif args.mode == "strip":
        rows = rename_strip(rows, chars=args.chars)

    elif args.mode == "pattern":
        rows = rename_pattern(rows, args.pattern, args.replacement)

    _write_csv(rows, args.output)


if __name__ == "__main__":  # pragma: no cover
    run()
