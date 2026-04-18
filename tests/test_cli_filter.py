"""Tests for cli_filter.run."""

import csv
import os
import sys
import tempfile
import types
import pytest
from csvwrangler.cli_filter import run


def _write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


ROWS = [
    {"name": "Alice", "score": "90"},
    {"name": "Bob", "score": "70"},
    {"name": "Carol", "score": "85"},
]


def _make_args(input_path, filters, output=None):
    return types.SimpleNamespace(input=input_path, filter=filters, output=output)


def test_filter_gt_stdout(tmp_path, capsys):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "score"])
    run(_make_args(str(p), ["score:gt:80"]))
    out = capsys.readouterr().out
    assert "Alice" in out
    assert "Carol" in out
    assert "Bob" not in out


def test_filter_eq_string(tmp_path, capsys):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "score"])
    run(_make_args(str(p), ["name:eq:Bob"]))
    out = capsys.readouterr().out
    assert "Bob" in out
    assert "Alice" not in out


def test_filter_output_file(tmp_path):
    p = tmp_path / "data.csv"
    out_p = tmp_path / "out.csv"
    _write_csv(p, ROWS, ["name", "score"])
    run(_make_args(str(p), ["score:lte:70"], output=str(out_p)))
    with open(out_p, newline="") as f:
        result = list(csv.DictReader(f))
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_no_filters_returns_all(tmp_path, capsys):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "score"])
    run(_make_args(str(p), []))
    out = capsys.readouterr().out
    assert "Alice" in out
    assert "Bob" in out
    assert "Carol" in out


def test_bad_filter_spec_exits(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(p, ROWS, ["name", "score"])
    with pytest.raises(SystemExit):
        run(_make_args(str(p), ["badspec"]))
