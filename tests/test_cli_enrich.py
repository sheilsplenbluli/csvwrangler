import csv
import io
import sys
from pathlib import Path

import pytest

from csvwrangler.cli_enrich import run


def _write_csv(tmp_path: Path, rows: list[dict], name: str = "in.csv") -> str:
    p = tmp_path / name
    fields = list(rows[0].keys())
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return str(p)


ROWS = [
    {"first": "Alice", "last": "Smith", "score": "10"},
    {"first": "Bob", "last": "Jones", "score": "20"},
]


def test_add_column_template_stdout(tmp_path, capsys):
    src = _write_csv(tmp_path, ROWS)
    run([src, "add-column", "full", "{first} {last}"])
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    result = list(reader)
    assert result[0]["full"] == "Alice Smith"
    assert result[1]["full"] == "Bob Jones"


def test_add_column_math_stdout(tmp_path, capsys):
    src = _write_csv(tmp_path, ROWS)
    run([src, "add-column", "double", "{score} * 2", "--mode", "math"])
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    result = list(reader)
    assert result[0]["double"] == "20.0"


def test_add_column_output_file(tmp_path):
    src = _write_csv(tmp_path, ROWS)
    dest = str(tmp_path / "out.csv")
    run([src, "-o", dest, "add-column", "tag", "person"])
    with open(dest, newline="") as fh:
        result = list(csv.DictReader(fh))
    assert result[0]["tag"] == "person"


def test_add_rownum_stdout(tmp_path, capsys):
    src = _write_csv(tmp_path, ROWS)
    run([src, "add-rownum"])
    out = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(out))
    result = list(reader)
    assert result[0]["row_num"] == "1"
    assert result[1]["row_num"] == "2"
    assert list(result[0].keys())[0] == "row_num"
