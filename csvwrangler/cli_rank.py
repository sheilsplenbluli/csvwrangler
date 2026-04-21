"""CLI entry point for the rank subcommand.

Examples
--------
  # rank by score descending, add 'rank' column
  csvwrangler rank input.csv --col score --desc

  # rank multiple columns
  csvwrangler rank input.csv --col score --col age --dest score_rank --dest age_rank

  # write to file
  csvwrangler rank input.csv --col score -o ranked.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional

from csvwrangler.rank import rank_many


def _load_csv(path: str) -> tuple[list[dict], list[str]]:
    """Return (rows, fieldnames) from a CSV file."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    return rows, fieldnames


def _write_csv(
    rows: list[dict],
    fieldnames: list[str],
    path: Optional[str],
) -> None:
    """Write rows to *path* or stdout."""
    dest = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            dest.close()


def run(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler rank",
        description="Add rank columns to a CSV file.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument(
        "--col",
        dest="cols",
        action="append",
        required=True,
        metavar="COLUMN",
        help="Column to rank (repeatable).",
    )
    parser.add_argument(
        "--dest",
        dest="dests",
        action="append",
        metavar="DEST_COLUMN",
        help="Destination column name for the rank (repeatable, must match --col count).",
    )
    parser.add_argument(
        "--method",
        choices=["rownum", "average", "min", "max", "dense"],
        default="rownum",
        help="Ranking method (default: rownum).",
    )
    parser.add_argument(
        "--desc",
        action="store_true",
        help="Rank in descending order (highest value = rank 1).",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output",
        default=None,
        help="Output CSV file (default: stdout).",
    )

    args = parser.parse_args(argv)

    cols: list[str] = args.cols
    dests: list[str] = args.dests or []

    # Validate dest count when provided
    if dests and len(dests) != len(cols):
        parser.error(
            f"--dest count ({len(dests)}) must match --col count ({len(cols)})"
        )

    rows, fieldnames = _load_csv(args.input)

    # Validate columns exist
    for col in cols:
        if col not in fieldnames:
            print(f"error: column '{col}' not found in CSV", file=sys.stderr)
            sys.exit(1)

    # Build spec list: [(col, dest), ...]
    specs = [
        (col, dests[i] if dests else f"{col}_rank")
        for i, col in enumerate(cols)
    ]

    result = rank_many(
        rows,
        specs=specs,
        method=args.method,
        ascending=not args.desc,
    )

    # Build updated fieldnames (append new rank columns not already present)
    out_fields = list(fieldnames)
    for _, dest in specs:
        if dest not in out_fields:
            out_fields.append(dest)

    _write_csv(result, out_fields, args.output)


if __name__ == "__main__":  # pragma: no cover
    run()
