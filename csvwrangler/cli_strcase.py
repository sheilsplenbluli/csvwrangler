"""CLI entry-point for the strcase command."""

import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.strcase import strcase_column


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, str]], path: str = None) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    out = open(path, 'w', newline='', encoding='utf-8') if path else sys.stdout
    try:
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            out.close()


def run(argv=None) -> None:
    parser = argparse.ArgumentParser(
        prog='csvwrangler strcase',
        description='Convert string case of a CSV column.',
    )
    parser.add_argument('file', help='Input CSV file')
    parser.add_argument('column', help='Column to convert')
    parser.add_argument(
        'mode',
        choices=['snake', 'camel', 'pascal', 'kebab'],
        help='Target case style',
    )
    parser.add_argument(
        '--dest',
        default=None,
        help='Destination column name (default: overwrite source column)',
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Write output to this file instead of stdout',
    )

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if rows and args.column not in rows[0]:
        print(f"Error: column '{args.column}' not found in CSV.", file=sys.stderr)
        sys.exit(1)

    result = strcase_column(rows, args.column, args.mode, dest=args.dest)
    _write_csv(result, args.output)


if __name__ == '__main__':
    run()
