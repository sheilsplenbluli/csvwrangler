"""CLI entry point for auto-cast / type inference."""
from __future__ import annotations
import argparse
import csv
import sys
from csvwrangler.cast import infer_types, auto_cast


def _load_csv(path: str):
    with open(path, newline='') as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _write_csv(rows, path: str | None):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    fh = open(path, 'w', newline='') if path else sys.stdout
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    if path:
        fh.close()


def run(argv=None):
    parser = argparse.ArgumentParser(prog='csvwrangler cast',
                                     description='Auto-detect and cast column types')
    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('-o', '--output', default=None, help='Output CSV file (default: stdout)')
    parser.add_argument('--columns', nargs='+', default=None,
                        help='Columns to cast (default: all)')
    parser.add_argument('--infer-only', action='store_true',
                        help='Print inferred types and exit')
    args = parser.parse_args(argv)

    rows = _load_csv(args.input)
    if not rows:
        sys.exit(0)

    if args.infer_only:
        types = infer_types(rows)
        for col, typ in types.items():
            print(f'{col}: {typ}')
        return

    result = auto_cast(rows, columns=args.columns)
    _write_csv(result, args.output)


if __name__ == '__main__':
    run()
