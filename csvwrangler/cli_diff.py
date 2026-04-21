"""CLI entry point for the diff command."""
import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.diff import diff_rows, diff_summary

Row = Dict[str, str]


def _load_csv(path: str) -> List[Row]:
    try:
        with open(path, newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: permission denied: {path}", file=sys.stderr)
        sys.exit(1)


def _write_csv(rows: List[Row], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler diff",
        description="Show row-level differences between two CSV files.",
    )
    parser.add_argument("left", help="Original CSV file")
    parser.add_argument("right", help="Updated CSV file")
    parser.add_argument(
        "--key", required=True, help="Comma-separated key column(s)"
    )
    parser.add_argument("--output", "-o", help="Write diff CSV to file")
    parser.add_argument(
        "--summary", action="store_true", help="Print counts only"
    )
    args = parser.parse_args(argv)

    left_rows = _load_csv(args.left)
    right_rows = _load_csv(args.right)
    key_cols = [c.strip() for c in args.key.split(",")]

    diff = diff_rows(left_rows, right_rows, key_cols)

    if args.summary:
        counts = diff_summary(diff)
        print(f"added:    {counts['added']}")
        print(f"removed:  {counts['removed']}")
        print(f"modified: {counts['modified']}")
        return

    if not diff:
        return

    if args.output:
        _write_csv(diff, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(diff[0].keys()))
        writer.writeheader()
        writer.writerows(diff)


if __name__ == "__main__":
    run()
