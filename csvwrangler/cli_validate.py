"""CLI entry point for CSV column validation."""
from __future__ import annotations

import argparse
import csv
import json
import sys

from csvwrangler.validate import validate_all


def _load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _print_table(violations: dict[str, list[dict]]) -> None:
    if not violations:
        print("No violations found.")
        return
    header = f"{'Column':<20} {'Row':>5} {'Value':<20} Reason"
    print(header)
    print("-" * len(header))
    for col, viols in violations.items():
        for v in viols:
            print(f"{v['column']:<20} {v['row']:>5} {v['value']:<20} {v['reason']}")


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate CSV columns")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--rule", action="append", dest="rules", default=[],
                        help="Rule as JSON, e.g. '{\"column\":\"age\",\"dtype\":\"numeric\"}'")
    parser.add_argument("--no-empty", dest="no_empty_cols", nargs="+", metavar="COL",
                        help="Columns that must not be empty")
    parser.add_argument("--allowed", nargs="+", metavar="COL=v1,v2",
                        help="Allowed values per column, e.g. status=active,inactive")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    args = parser.parse_args(argv)

    rows = _load_csv(args.input)
    rules: list[dict] = [json.loads(r) for r in args.rules]

    if args.no_empty_cols:
        for col in args.no_empty_cols:
            rules.append({"column": col, "allow_empty": False})

    if args.allowed:
        for item in args.allowed:
            col, vals = item.split("=", 1)
            rules.append({"column": col, "allowed": vals.split(",")})

    if not rules:
        parser.error("Provide at least one rule via --rule, --no-empty, or --allowed")

    violations = validate_all(rows, rules)

    if args.format == "json":
        print(json.dumps(violations, indent=2))
    else:
        _print_table(violations)

    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    run()
