"""Integration tests for cli_outlier.run"""
import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_outlier import run


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


ROWS = [
    {"name": "a", "val": "10"},
    {"name": "b", "val": "12"},
    {"name": "c", "val": "11"},
    {"name": "d", "val": "13"},
    {"name": "e", "val": "200"},
]


def test_flag_mode_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "val"])
    run([str(p), "--column", "val", "--mode", "flag"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    flags = {r["name"]: r["_outlier"] for r in rows}
    assert flags["e"] == "1"
    assert flags["a"] == "0"


def test_keep_mode_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "val"])
    run([str(p), "--column", "val", "--mode", "keep"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["name"] == "e"


def test_remove_mode_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "val"])
    run([str(p), "--column", "val", "--mode", "remove"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    names = [r["name"] for r in rows]
    assert "e" not in names
    assert len(rows) == 4


def test_output_file(tmp_path):
    p = tmp_path / "data.csv"
    out = tmp_path / "out.csv"
    _write_csv(p, ROWS, ["name", "val"])
    run([str(p), "--column", "val", "--output", str(out)])
    assert out.exists()
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 5


def test_bad_column_exits(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "val"])
    with pytest.raises(SystemExit):
        run([str(p), "--column", "nonexistent"])
