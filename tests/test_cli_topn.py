import csv
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_topn import run


def _write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE = [
    {"name": "alice", "score": "90"},
    {"name": "bob", "score": "75"},
    {"name": "carol", "score": "60"},
    {"name": "dave", "score": "85"},
]


def test_top_n_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(SAMPLE, str(p))
    run([str(p), "score", "2"])
    captured = capsys.readouterr().out
    reader = list(csv.DictReader(io.StringIO(captured)))
    assert len(reader) == 2
    scores = [float(r["score"]) for r in reader]
    assert min(scores) >= 85


def test_bottom_n_stdout(capsys, tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(SAMPLE, str(p))
    run([str(p), "score", "2", "--mode", "bottom"])
    captured = capsys.readouterr().out
    reader = list(csv.DictReader(io.StringIO(captured)))
    assert len(reader) == 2
    scores = [float(r["score"]) for r in reader]
    assert max(scores) <= 75


def test_output_file(tmp_path):
    p = tmp_path / "data.csv"
    out = tmp_path / "out.csv"
    _write_csv(SAMPLE, str(p))
    run([str(p), "score", "1", "-o", str(out)])
    assert out.exists()
    rows = list(csv.DictReader(open(str(out))))
    assert len(rows) == 1
    assert rows[0]["score"] == "90"


def test_keep_ties(capsys, tmp_path):
    rows = [
        {"name": "a", "score": "90"},
        {"name": "b", "score": "90"},
        {"name": "c", "score": "70"},
    ]
    p = tmp_path / "data.csv"
    _write_csv(rows, str(p))
    run([str(p), "score", "1", "--keep-ties"])
    captured = capsys.readouterr().out
    result = list(csv.DictReader(io.StringIO(captured)))
    assert len(result) == 2


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["no_such_file.csv", "score", "2"])


def test_bad_column_exits(tmp_path):
    p = tmp_path / "data.csv"
    _write_csv(SAMPLE, str(p))
    with pytest.raises(SystemExit):
        run([str(p), "nonexistent", "2"])
