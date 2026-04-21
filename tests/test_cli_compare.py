import csv
import io
import os
import sys
import tempfile

import pytest

from csvwrangler.cli_compare import run


def _write_csv(path: str, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(
        str(p),
        [{"name": "alice", "a": "10", "b": "4"}, {"name": "bob", "a": "3", "b": "3"}],
        ["name", "a", "b"],
    )
    return str(p)


def test_diff_stdout(sample_csv, capsys):
    run([sample_csv, "--col-a", "a", "--col-b", "b", "--mode", "diff", "--dest", "delta"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["delta"] == "6.0"
    assert rows[1]["delta"] == "0.0"


def test_eq_mode_stdout(sample_csv, capsys):
    run([sample_csv, "--col-a", "a", "--col-b", "b", "--mode", "eq"])
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    rows = list(reader)
    assert rows[0]["_cmp"] == "0"
    assert rows[1]["_cmp"] == "1"


def test_output_file(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    run([sample_csv, "--col-a", "a", "--col-b", "b", "--mode", "gt", "-o", out])
    with open(out, newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows[0]["_cmp"] == "1"


def test_bad_column_exits(sample_csv):
    with pytest.raises(SystemExit):
        run([sample_csv, "--col-a", "missing", "--col-b", "b"])
