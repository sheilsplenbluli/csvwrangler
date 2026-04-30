"""CLI tests for csvwrangler.cli_phonetic."""
import csv
import io
import os
import sys
from pathlib import Path

import pytest

from csvwrangler.cli_phonetic import run


def _write_csv(tmp_path: Path, rows, filename="data.csv") -> str:
    path = str(tmp_path / filename)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


SAMPLE = [
    {"id": "1", "name": "Robert"},
    {"id": "2", "name": "Rupert"},
    {"id": "3", "name": "Smith"},
]


def test_soundex_stdout(tmp_path, capsys):
    path = _write_csv(tmp_path, SAMPLE)
    run([path, "--col", "name"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "name_soundex" in rows[0]
    assert rows[0]["name_soundex"] == rows[1]["name_soundex"]  # Robert == Rupert


def test_metaphone_stdout(tmp_path, capsys):
    path = _write_csv(tmp_path, SAMPLE)
    run([path, "--col", "name", "--method", "metaphone"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "name_metaphone" in rows[0]


def test_custom_dest(tmp_path, capsys):
    path = _write_csv(tmp_path, SAMPLE)
    run([path, "--col", "name", "--dest", "sx"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "sx" in rows[0]
    assert "name_soundex" not in rows[0]


def test_output_file(tmp_path, capsys):
    path = _write_csv(tmp_path, SAMPLE)
    out = str(tmp_path / "out.csv")
    run([path, "--col", "name", "-o", out])
    assert os.path.exists(out)
    with open(out, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert "name_soundex" in rows[0]


def test_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        run([str(tmp_path / "nope.csv"), "--col", "name"])


def test_bad_column_exits(tmp_path):
    path = _write_csv(tmp_path, SAMPLE)
    with pytest.raises(SystemExit):
        run([path, "--col", "nonexistent"])


def test_multiple_cols(tmp_path, capsys):
    data = [
        {"first": "Alice", "last": "Smith"},
        {"first": "Bob", "last": "Jones"},
    ]
    path = _write_csv(tmp_path, data)
    run([path, "--col", "first", "--col", "last"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert "first_soundex" in rows[0]
    assert "last_soundex" in rows[0]
