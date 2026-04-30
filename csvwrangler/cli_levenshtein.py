"""CLI for fuzzy string matching via Levenshtein distance."""

from __future__ import annotations
import argparse
import csv
import sys
from typing import List, Dict

from csvwrangler.levenshtein import distance_column, nearest_match, similarity_score


def _load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _write_csv(rows: List[Dict[str, str]], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler-levenshtein",
        description="Fuzzy string matching using Levenshtein distance",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # distance sub-command
    p_dist = sub.add_parser("distance", help="Add edit-distance column")
    p_dist.add_argument("file")
    p_dist.add_argument("--col-a", required=True)
    p_dist.add_argument("--col-b", required=True)
    p_dist.add_argument("--dest")
    p_dist.add_argument("--ignore-case", action="store_true")
    p_dist.add_argument("--output", "-o")

    # nearest sub-command
    p_near = sub.add_parser("nearest", help="Find nearest candidate string")
    p_near.add_argument("file")
    p_near.add_argument("--col", required=True)
    p_near.add_argument("--candidates", required=True, help="Comma-separated list")
    p_near.add_argument("--dest")
    p_near.add_argument("--ignore-case", action="store_true")
    p_near.add_argument("--output", "-o")

    # similarity sub-command
    p_sim = sub.add_parser("similarity", help="Add 0-1 similarity score column")
    p_sim.add_argument("file")
    p_sim.add_argument("--col-a", required=True)
    p_sim.add_argument("--col-b", required=True)
    p_sim.add_argument("--dest")
    p_sim.add_argument("--ignore-case", action="store_true")
    p_sim.add_argument("--output", "-o")

    args = parser.parse_args(argv)

    try:
        rows = _load_csv(args.file)
    except FileNotFoundError:
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    if args.cmd == "distance":
        result = distance_column(rows, args.col_a, args.col_b,
                                 dest=args.dest, ignore_case=args.ignore_case)
    elif args.cmd == "nearest":
        candidates = [c.strip() for c in args.candidates.split(",")]
        result = nearest_match(rows, args.col, candidates,
                               dest=args.dest, ignore_case=args.ignore_case)
    else:  # similarity
        result = similarity_score(rows, args.col_a, args.col_b,
                                  dest=args.dest, ignore_case=args.ignore_case)

    if not result:
        return

    if args.output:
        _write_csv(result, args.output)
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)


if __name__ == "__main__":
    run()
