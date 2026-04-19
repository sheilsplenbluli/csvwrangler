import csv
import os
import pytest
from unittest.mock import patch
from csvwrangler.cli_split import run


def _write_csv(path, rows):
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


SAMPLE = [
    {"dept": "eng", "name": "Alice"},
    {"dept": "hr", "name": "Bob"},
    {"dept": "eng", "name": "Carol"},
]


def test_column_split_creates_files(tmp_path):
    src = tmp_path / "in.csv"
    _write_csv(str(src), SAMPLE)
    out = tmp_path / "out"
    run([str(src), "--outdir", str(out), "column", "dept"])
    files = list(out.iterdir())
    assert len(files) == 2


def test_column_split_correct_row_counts(tmp_path):
    src = tmp_path / "in.csv"
    _write_csv(str(src), SAMPLE)
    out = tmp_path / "out"
    run([str(src), "--outdir", str(out), "column", "dept"])
    eng_file = out / "part_eng.csv"
    with open(eng_file, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2


def test_column_split_bad_column_exits(tmp_path):
    src = tmp_path / "in.csv"
    _write_csv(str(src), SAMPLE)
    with pytest.raises(SystemExit):
        run([str(src), "column", "nonexistent"])


def test_chunk_split_creates_files(tmp_path):
    src = tmp_path / "in.csv"
    rows = [{"n": str(i)} for i in range(10)]
    _write_csv(str(src), rows)
    out = tmp_path / "out"
    run([str(src), "--outdir", str(out), "chunk", "3"])
    files = sorted(out.iterdir())
    assert len(files) == 4


def test_chunk_split_last_chunk_size(tmp_path):
    src = tmp_path / "in.csv"
    rows = [{"n": str(i)} for i in range(10)]
    _write_csv(str(src), rows)
    out = tmp_path / "out"
    run([str(src), "--outdir", str(out), "chunk", "3"])
    last = sorted(out.iterdir())[-1]
    with open(last, newline="") as fh:
        assert len(list(csv.DictReader(fh))) == 1


def test_chunk_zero_exits(tmp_path):
    src = tmp_path / "in.csv"
    _write_csv(str(src), SAMPLE)
    with pytest.raises(SystemExit):
        run([str(src), "chunk", "0"])
