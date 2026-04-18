"""CLI entry point for sampling CSV rows."""
import argparse
import csv
import sys

from csvwrangler.sample import sample_rows, sample_fraction, head_rows, tail_rows


def _load_csv(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def _write_csv(fieldnames, rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(argv=None):
    parser = argparse.ArgumentParser(prog="csvwrangler sample", description="Sample rows from a CSV file.")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--n", type=int, help="Sample exactly N rows at random")
    mode.add_argument("--frac", type=float, help="Sample a fraction of rows (0.0-1.0)")
    mode.add_argument("--head", type=int, help="Take first N rows")
    mode.add_argument("--tail", type=int, help="Take last N rows")

    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")

    args = parser.parse_args(argv)

    fieldnames, rows = _load_csv(args.input)

    if args.n is not None:
        result = sample_rows(rows, args.n, seed=args.seed)
    elif args.frac is not None:
        result = sample_fraction(rows, args.frac, seed=args.seed)
    elif args.head is not None:
        result = head_rows(rows, args.head)
    else:
        result = tail_rows(rows, args.tail)

    if args.output:
        _write_csv(fieldnames, result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
