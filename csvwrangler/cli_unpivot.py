"""CLI entry point for the unpivot (melt) command."""
import argparse
import csv
import sys
from typing import List

from csvwrangler.unpivot import unpivot_rows


def _load_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[dict], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv: List[str] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler unpivot",
        description="Melt wide CSV columns into long format (unpivot).",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument(
        "--id-cols",
        required=True,
        help="Comma-separated list of identifier columns to keep",
    )
    parser.add_argument(
        "--value-cols",
        default=None,
        help="Comma-separated list of columns to unpivot (default: all non-id cols)",
    )
    parser.add_argument(
        "--var-name",
        default="variable",
        help="Name for the new variable column (default: variable)",
    )
    parser.add_argument(
        "--val-name",
        default="value",
        help="Name for the new value column (default: value)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")

    args = parser.parse_args(argv)

    rows = _load_csv(args.input)
    id_cols = [c.strip() for c in args.id_cols.split(",")]
    value_cols = (
        [c.strip() for c in args.value_cols.split(",")] if args.value_cols else None
    )

    result = unpivot_rows(
        rows,
        id_cols=id_cols,
        value_cols=value_cols,
        var_name=args.var_name,
        val_name=args.val_name,
    )

    if not result:
        return

    fieldnames = list(result[0].keys())

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
