import csv
import io
import os
import tempfile
import pytest
from unittest.mock import patch

from csvwrangler.cli_levenshtein import run


def _write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


SAMPLE = [
    {"word": "colour", "alt": "color"},
    {"word": "hello", "alt": "hello"},
    {"word": "kitten", "alt": "sitting"},
]


def test_distance_stdout(capsys):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(SAMPLE, f.name)
        fname = f.name
    try:
        run(["distance", fname, "--col-a", "word", "--col-b", "alt"])
        out = capsys.readouterr().out
        reader = csv.DictReader(io.StringIO(out))
        rows = list(reader)
        assert "word_dist_alt" in rows[0]
        assert rows[1]["word_dist_alt"] == "0"
        assert rows[2]["word_dist_alt"] == "3"
    finally:
        os.unlink(fname)


def test_distance_ignore_case(capsys):
    data = [{"a": "Hello", "b": "hello"}]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(data, f.name)
        fname = f.name
    try:
        run(["distance", fname, "--col-a", "a", "--col-b", "b", "--ignore-case"])
        out = capsys.readouterr().out
        rows = list(csv.DictReader(io.StringIO(out)))
        assert rows[0]["a_dist_b"] == "0"
    finally:
        os.unlink(fname)


def test_nearest_stdout(capsys):
    data = [{"name": "colour"}, {"name": "teh"}]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(data, f.name)
        fname = f.name
    try:
        run(["nearest", fname, "--col", "name", "--candidates", "color,the,ten"])
        out = capsys.readouterr().out
        rows = list(csv.DictReader(io.StringIO(out)))
        assert rows[0]["name_nearest"] == "color"
        assert rows[1]["name_nearest"] == "the"
    finally:
        os.unlink(fname)


def test_similarity_stdout(capsys):
    data = [{"x": "abc", "y": "abc"}, {"x": "abc", "y": "xyz"}]
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(data, f.name)
        fname = f.name
    try:
        run(["similarity", fname, "--col-a", "x", "--col-b", "y"])
        out = capsys.readouterr().out
        rows = list(csv.DictReader(io.StringIO(out)))
        assert rows[0]["x_sim_y"] == "1.0"
        assert float(rows[1]["x_sim_y"]) < 1.0
    finally:
        os.unlink(fname)


def test_output_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        _write_csv(SAMPLE, f.name)
        in_name = f.name
    out_name = in_name + "_out.csv"
    try:
        run(["distance", in_name, "--col-a", "word", "--col-b", "alt",
             "--output", out_name])
        assert os.path.exists(out_name)
        with open(out_name, newline="") as fh:
            rows = list(csv.DictReader(fh))
        assert len(rows) == 3
        assert "word_dist_alt" in rows[0]
    finally:
        os.unlink(in_name)
        if os.path.exists(out_name):
            os.unlink(out_name)


def test_missing_file_exits():
    with pytest.raises(SystemExit):
        run(["distance", "nonexistent.csv", "--col-a", "a", "--col-b", "b"])
