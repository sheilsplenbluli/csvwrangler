"""CLI entry-point for streak detection."""

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.streak import streak_any


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


def run(argv=None):
    parser = argparse.ArgumentParser(
        prog="csvwrangler streak",
        description="Add streak-count columns for consecutive matching values.",
    )
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument(
        "--spec",
        action="append",
        metavar="COL:TARGET",
        required=True,
        help="column:target pair (repeatable). E.g. --spec status:win",
    )
    parser.add_argument(
        "--dest",
        action="append",
        metavar="DEST_COL",
        default=None,
        help="Destination column names (same order as --spec).",
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        default=False,
        help="Case-insensitive matching.",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    dests = args.dest or []
    specs = []
    for i, spec_str in enumerate(args.spec):
        if ":" not in spec_str:
            print(f"error: invalid spec '{spec_str}', expected COL:TARGET", file=sys.stderr)
            sys.exit(1)
        col, target = spec_str.split(":", 1)
        entry = {"column": col, "target": target, "case_sensitive": not args.ignore_case}
        if i < len(dests):
            entry["dest"] = dests[i]
        specs.append(entry)

    result = streak_any(rows, specs)

    if args.output:
        _write_csv(result, args.output)
    else:
        if result:
            writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
            writer.writeheader()
            writer.writerows(result)


if __name__ == "__main__":
    run()
