"""CLI entry point for the summarize subcommand."""

import csv
import sys
import json
import argparse
from pathlib import Path

from csvwrangler.summarize import summarize_all, summarize_column


def _load_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _print_table(summaries: list[dict]) -> None:
    if not summaries:
        print("No data.")
        return
    keys = list(summaries[0].keys())
    widths = {k: max(len(k), max(len(str(s.get(k, ""))) for s in summaries)) for k in keys}
    header = "  ".join(k.ljust(widths[k]) for k in keys)
    print(header)
    print("-" * len(header))
    for s in summaries:
        print("  ".join(str(s.get(k, "")).ljust(widths[k]) for k in keys))


def run(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="csvwrangler summarize",
        description="Summarize columns of a CSV file.",
    )
    parser.add_argument("file", help="Path to CSV file")
    parser.add_argument("--col", metavar="COLUMN", help="Summarize a single column")
    parser.add_argument(
        "--format", choices=["table", "json"], default="table", dest="fmt"
    )
    args = parser.parse_args(argv)

    if not Path(args.file).exists():
        print(f"error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    rows = _load_csv(args.file)

    if args.col:
        summaries = [summarize_column(rows, args.col)]
    else:
        summaries = summarize_all(rows)

    if args.fmt == "json":
        print(json.dumps(summaries, indent=2))
    else:
        _print_table(summaries)


if __name__ == "__main__":
    run()
