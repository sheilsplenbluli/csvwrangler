"""CLI entry point for CSV column transformations."""

import csv
import json
import sys
from typing import List, Dict

from csvwrangler.transform import build_transforms, apply_transforms


def _load_csv(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(rows: List[Dict], path: str | None) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    dest = open(path, "w", newline="", encoding="utf-8") if path else sys.stdout
    try:
        writer = csv.DictWriter(dest, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            dest.close()


def run(
    csv_path: str,
    specs_path: str,
    output_path: str | None = None,
) -> None:
    """Load CSV, apply transforms defined in a JSON specs file, write result.

    Specs file is a JSON array of transform spec objects, e.g.:
      [{"op": "drop", "columns": ["ssn"]}, {"op": "rename", "mapping": {"nm": "name"}}]
    """
    rows = _load_csv(csv_path)

    with open(specs_path, encoding="utf-8") as f:
        specs = json.load(f)

    if not isinstance(specs, list):
        print("error: specs file must contain a JSON array", file=sys.stderr)
        sys.exit(1)

    try:
        transforms = build_transforms(specs)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    result = apply_transforms(rows, transforms)
    _write_csv(result, output_path)


if __name__ == "__main__":  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Apply column transforms to a CSV file.")
    parser.add_argument("csv", help="Input CSV file")
    parser.add_argument("specs", help="JSON file with transform specs")
    parser.add_argument("-o", "--output", default=None, help="Output CSV file (default: stdout)")
    args = parser.parse_args()
    run(args.csv, args.specs, args.output)
