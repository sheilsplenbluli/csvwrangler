import csv
import io
import os
import tempfile
from unittest.mock import patch

import pytest

from csvwrangler.cli_streak import run


def _write_csv(rows, fieldnames=None):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="")
    fieldnames = fieldnames or list(rows[0].keys())
    writer = csv.DictWriter(tmp, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    tmp.close()
    return tmp.name


SAMPLE = [
    {"team": "A", "result": "win"},
    {"team": "A", "result": "win"},
    {"team": "B", "result": "loss"},
    {"team": "A", "result": "win"},
]


def test_streak_stdout(capsys):
    path = _write_csv(SAMPLE)
    try:
        run([path, "--spec", "result:win"])
        captured = capsys.readouterr()
        reader = csv.DictReader(io.StringIO(captured.out))
        rows = list(reader)
        streaks = [r["result_streak"] for r in rows]
        assert streaks == ["1", "2", "0", "1"]
    finally:
        os.unlink(path)


def test_streak_output_file(tmp_path):
    path = _write_csv(SAMPLE)
    out = str(tmp_path / "out.csv")
    try:
        run([path, "--spec", "result:win", "-o", out])
        with open(out, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert rows[2]["result_streak"] == "0"
        assert rows[1]["result_streak"] == "2"
    finally:
        os.unlink(path)


def test_streak_custom_dest(capsys):
    path = _write_csv(SAMPLE)
    try:
        run([path, "--spec", "result:win", "--dest", "run"])
        captured = capsys.readouterr()
        reader = csv.DictReader(io.StringIO(captured.out))
        rows = list(reader)
        assert "run" in rows[0]
        assert "result_streak" not in rows[0]
    finally:
        os.unlink(path)


def test_streak_ignore_case(capsys):
    rows = [
        {"v": "WIN"},
        {"v": "win"},
        {"v": "Win"},
        {"v": "loss"},
    ]
    path = _write_csv(rows)
    try:
        run([path, "--spec", "v:win", "--ignore-case"])
        captured = capsys.readouterr()
        reader = csv.DictReader(io.StringIO(captured.out))
        result = list(reader)
        streaks = [r["v_streak"] for r in result]
        assert streaks == ["1", "2", "3", "0"]
    finally:
        os.unlink(path)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["nonexistent.csv", "--spec", "col:val"])


def test_bad_spec_exits():
    rows = [{"a": "1"}]
    path = _write_csv(rows)
    try:
        with pytest.raises(SystemExit):
            run([path, "--spec", "nocolon"])
    finally:
        os.unlink(path)
