"""Tests for cli_sort.run."""
from __future__ import annotations

import csv
import io
import os
import tempfile

import pytest

from csvwrangler.cli_sort import run


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


DATA = [
    {"name": "Charlie", "score": "70"},
    {"name": "Alice", "score": "90"},
    {"name": "Bob", "score": "80"},
]


def test_sort_string_asc_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), DATA, ["name", "score"])
    run([str(p), "-k", "name"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    names = [r["name"] for r in reader]
    assert names == ["Alice", "Bob", "Charlie"]


def test_sort_numeric_desc_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), DATA, ["name", "score"])
    run([str(p), "-k", "score", "--desc"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    scores = [r["score"] for r in reader]
    assert scores == ["90", "80", "70"]


def test_sort_output_file(tmp_path):
    p = tmp_path / "data.csv"
    out = tmp_path / "out.csv"
    _write_csv(str(p), DATA, ["name", "score"])
    run([str(p), "-k", "name", "-o", str(out)])
    with open(str(out), newline="") as fh:
        reader = csv.DictReader(fh)
        names = [r["name"] for r in reader]
    assert names == ["Alice", "Bob", "Charlie"]


def test_sort_case_insensitive_default(capsys, tmp_path):
    rows = [{"word": "banana"}, {"word": "Apple"}, {"word": "cherry"}]
    p = tmp_path / "data.csv"
    _write_csv(str(p), rows, ["word"])
    run([str(p), "-k", "word"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    words = [r["word"] for r in reader]
    assert words == ["Apple", "banana", "cherry"]


def test_sort_missing_key_exits(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), DATA, ["name", "score"])
    with pytest.raises(SystemExit):
        run([str(p)])
