"""CLI entry point for group-by aggregation."""
import csv
import sys
import argparse
import io
from csvwrangler.aggregate import aggregate_rows


def _load_csv(path: str) -> tuple[list[dict], list[str]]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return rows, list(fieldnames)


def _write_csv(rows: list[dict], fieldnames: list[str], dest) -> None:
    writer = csv.DictWriter(dest, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler aggregate",
        description="Group CSV rows and compute aggregations.",
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument(
        "--group-by", required=True,
        help="Comma-separated columns to group by",
    )
    parser.add_argument(
        "--agg", action="append", required=True, metavar="OUT:FUNC:SRC",
        help="Aggregation spec, e.g. total_salary:sum:salary (repeatable)",
    )
    parser.add_argument("-o", "--output", default=None, help="Output CSV file")
    args = parser.parse_args(argv)

    rows, _ = _load_csv(args.input)
    group_by = [c.strip() for c in args.group_by.split(",")]

    aggregations: dict[str, str] = {}
    for spec in args.agg:
        parts = spec.split(":", 2)
        if len(parts) != 3:
            print(f"Invalid --agg spec '{spec}', expected OUT:FUNC:SRC", file=sys.stderr)
            sys.exit(1)
        out_col, func, src = parts
        aggregations[out_col] = f"{func}:{src}"

    result = aggregate_rows(rows, group_by, aggregations)
    if not result:
        return

    fieldnames = group_by + [k for k in aggregations]

    if args.output:
        with open(args.output, "w", newline="") as f:
            _write_csv(result, fieldnames, f)
    else:
        _write_csv(result, fieldnames, sys.stdout)


if __name__ == "__main__":
    run()
