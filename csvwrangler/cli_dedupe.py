"""CLI entry point for deduplication."""
import argparse
import csv
import sys
from typing import List, Optional

from csvwrangler.dedupe import dedupe_rows, count_duplicates


def _load_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[dict], path: Optional[str]) -> None:
    if not rows:
        return
    out = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    if path:
        out.close()


def run(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler dedupe",
        description="Remove duplicate rows from a CSV file.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")
    parser.add_argument(
        "-c", "--columns", nargs="+", default=None,
        metavar="COL",
        help="Columns to use for uniqueness check (default: all columns)",
    )
    parser.add_argument(
        "--keep", choices=["first", "last"], default="first",
        help="Which duplicate to keep (default: first)",
    )
    parser.add_argument(
        "--count", action="store_true",
        help="Print duplicate count and exit without writing output",
    )
    args = parser.parse_args(argv)

    rows = _load_csv(args.input)

    if args.count:
        n = count_duplicates(rows, columns=args.columns)
        print(f"Duplicate rows: {n}")
        return

    result = dedupe_rows(rows, columns=args.columns, keep=args.keep)
    removed = len(rows) - len(result)
    print(f"Removed {removed} duplicate(s).", file=sys.stderr)
    _write_csv(result, args.output)


if __name__ == "__main__":
    run()
