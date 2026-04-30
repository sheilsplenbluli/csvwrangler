"""CLI entry point for the scorecard command."""
import argparse
import csv
import json
import sys
from csvwrangler.scorecard import score_rows, scorecard_summary


def _load_csv(path: str):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _write_csv(rows, path=None):
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


def _parse_rules(specs):
    """Parse rule strings like 'age:gt:18:10' into dicts."""
    rules = []
    for spec in specs:
        parts = spec.split(":")
        if len(parts) != 4:
            print(f"Invalid rule spec '{spec}'. Expected col:op:threshold:points", file=sys.stderr)
            sys.exit(1)
        col, op, threshold, points_str = parts
        try:
            points = float(points_str)
        except ValueError:
            print(f"Points must be numeric in rule '{spec}'", file=sys.stderr)
            sys.exit(1)
        rules.append({"col": col, "op": op, "threshold": threshold, "points": points})
    return rules


def run(argv=None):
    parser = argparse.ArgumentParser(description="Score rows based on weighted column rules")
    parser.add_argument("file", help="Input CSV file")
    parser.add_argument("-r", "--rule", dest="rules", action="append", default=[],
                        metavar="col:op:threshold:points",
                        help="Rule spec (repeatable). op: gt,gte,lt,lte,eq,contains,notempty")
    parser.add_argument("--dest", default="score", help="Output column name (default: score)")
    parser.add_argument("--default", type=float, default=0.0,
                        help="Base score before rules (default: 0)")
    parser.add_argument("--summary", action="store_true", help="Print score summary to stderr")
    parser.add_argument("-o", "--output", default=None, help="Output file (default: stdout)")
    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    rules = _parse_rules(args.rules)
    scored = score_rows(rows, rules, dest=args.dest, default=args.default)
    _write_csv(scored, args.output)

    if args.summary:
        summary = scorecard_summary(scored, dest=args.dest)
        print(json.dumps(summary), file=sys.stderr)


if __name__ == "__main__":
    run()
