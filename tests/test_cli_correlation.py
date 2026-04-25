import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch
from csvwrangler.cli_correlation import run


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE = [
    {"x": "1", "y": "2", "label": "a"},
    {"x": "2", "y": "4", "label": "b"},
    {"x": "3", "y": "6", "label": "c"},
    {"x": "4", "y": "8", "label": "d"},
    {"x": "5", "y": "10", "label": "e"},
]


def test_all_columns_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), SAMPLE)
    run([str(p)])
    out = capsys.readouterr().out
    assert "col_a" in out
    assert "col_b" in out
    assert "r" in out


def test_pair_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), SAMPLE)
    run([str(p), "--pair", "x", "y"])
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    # header + 1 data row
    assert len(lines) == 2
    assert "1.000000" in out


def test_cols_subset(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), SAMPLE)
    run([str(p), "--cols", "x", "y"])
    out = capsys.readouterr().out
    assert "x" in out
    assert "y" in out


def test_output_file(tmp_path):
    p = tmp_path / "data.csv"
    out_p = tmp_path / "out.csv"
    _write_csv(str(p), SAMPLE)
    run([str(p), "--pair", "x", "y", "-o", str(out_p)])
    assert out_p.exists()
    with open(str(out_p)) as fh:
        content = fh.read()
    assert "r" in content


def test_no_numeric_pairs_exits(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(str(p), [{"a": "foo", "b": "bar"}, {"a": "baz", "b": "qux"}])
    with pytest.raises(SystemExit):
        run([str(p)])
