import csv
import io
import os
import tempfile
from unittest.mock import patch
import pytest

from csvwrangler.cli_merge import run


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def test_merge_stdout(capsys, tmp_path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    _write_csv(f1, [{"x": "1"}, {"x": "2"}], ["x"])
    _write_csv(f2, [{"x": "3"}], ["x"])
    run([str(f1), str(f2)])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 3
    assert rows[2]["x"] == "3"


def test_merge_fills_missing(capsys, tmp_path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    _write_csv(f1, [{"a": "1", "b": "2"}], ["a", "b"])
    _write_csv(f2, [{"a": "3", "c": "4"}], ["a", "c"])
    run([str(f1), str(f2)])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[1]["b"] == ""
    assert rows[0]["c"] == ""


def test_merge_output_file(tmp_path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    out = tmp_path / "out.csv"
    _write_csv(f1, [{"n": "1"}], ["n"])
    _write_csv(f2, [{"n": "2"}], ["n"])
    run([str(f1), str(f2), "-o", str(out)])
    rows = list(csv.DictReader(open(out)))
    assert len(rows) == 2


def test_missing_file_exits(tmp_path):
    with pytest.raises(SystemExit):
        run([str(tmp_path / "nope.csv")])
