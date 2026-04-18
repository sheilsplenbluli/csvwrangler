"""Tests for cli_join.run()."""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from csvwrangler.cli_join import run


def _write_csv(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content).strip())
    return str(p)


def test_inner_join_stdout(tmp_path, capsys):
    left = _write_csv(tmp_path, "left.csv", """
        id,name
        1,Alice
        2,Bob
        3,Carol
    """)
    right = _write_csv(tmp_path, "right.csv", """
        id,score
        1,90
        2,85
    """)
    run([left, right, "--on", "id"])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[0]["score"] == "90"


def test_left_join_stdout(tmp_path, capsys):
    left = _write_csv(tmp_path, "left.csv", """
        id,name
        1,Alice
        2,Bob
    """)
    right = _write_csv(tmp_path, "right.csv", """
        id,score
        1,90
    """)
    run([left, right, "--on", "id", "--how", "left"])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[1]["score"] == ""


def test_output_file(tmp_path, capsys):
    left = _write_csv(tmp_path, "left.csv", """
        id,name
        1,Alice
    """)
    right = _write_csv(tmp_path, "right.csv", """
        id,dept
        1,Eng
    """)
    out_file = str(tmp_path / "out.csv")
    run([left, right, "--on", "id", "--output", out_file])
    rows = list(csv.DictReader(open(out_file)))
    assert rows[0]["dept"] == "Eng"
    assert capsys.readouterr().out == ""


def test_right_join(tmp_path, capsys):
    left = _write_csv(tmp_path, "left.csv", """
        id,name
        1,Alice
    """)
    right = _write_csv(tmp_path, "right.csv", """
        id,score
        1,90
        2,75
    """)
    run([left, right, "--on", "id", "--how", "right"])
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 2
