"""Phonetic encoding: Soundex and Metaphone-style matching for fuzzy deduplication."""
from __future__ import annotations

from typing import List, Dict


# ---------------------------------------------------------------------------
# Soundex
# ---------------------------------------------------------------------------

_SOUNDEX_TABLE = str.maketrans(
    "AEHIOUYBFPVCGJKQSXZDTLMNR",
    "000000011122222222334556",
)


def _soundex(value: str) -> str:
    """Return a 4-character Soundex code for *value*."""
    v = value.upper().strip()
    if not v:
        return ""
    first = v[0]
    coded = v.translate(_SOUNDEX_TABLE)
    # collapse consecutive identical digits and remove zeros
    result = first
    prev = coded[0]
    for ch in coded[1:]:
        if ch != "0" and ch != prev:
            result += ch
        prev = ch
    return (result + "000")[:4]


def soundex_column(
    rows: List[Dict[str, str]],
    col: str,
    dest: str | None = None,
) -> List[Dict[str, str]]:
    """Add a Soundex code column derived from *col*."""
    dest = dest or f"{col}_soundex"
    out = []
    for row in rows:
        new = dict(row)
        new[dest] = _soundex(row.get(col, ""))
        out.append(new)
    return out


# ---------------------------------------------------------------------------
# Simplified Metaphone (first-pass consonant encoding)
# ---------------------------------------------------------------------------

_VOWELS = set("AEIOU")


def _metaphone(value: str) -> str:
    """Return a simplified Metaphone code (max 6 chars) for *value*."""
    v = value.upper().strip()
    if not v:
        return ""
    # Drop trailing S if preceded by a vowel
    if len(v) > 1 and v[-1] == "S" and v[-2] in _VOWELS:
        v = v[:-1]
    result = []
    for i, ch in enumerate(v):
        if ch in _VOWELS:
            if i == 0:
                result.append(ch)
        elif ch == "B":
            if not (i > 0 and v[i - 1] == "M"):
                result.append("B")
        elif ch in ("C", "K", "Q"):
            result.append("K")
        elif ch in ("D", "T"):
            result.append("T")
        elif ch in ("F", "P", "V"):
            result.append("F")
        elif ch in ("G", "J"):
            result.append("K")
        elif ch in ("L",):
            result.append("L")
        elif ch in ("M", "N"):
            result.append("M")
        elif ch == "R":
            result.append("R")
        elif ch in ("S", "X", "Z"):
            result.append("S")
        elif ch in ("H", "W", "Y"):
            pass  # silent
    # collapse runs
    collapsed = ""
    prev = ""
    for ch in result:
        if ch != prev:
            collapsed += ch
        prev = ch
    return collapsed[:6]


def metaphone_column(
    rows: List[Dict[str, str]],
    col: str,
    dest: str | None = None,
) -> List[Dict[str, str]]:
    """Add a Metaphone code column derived from *col*."""
    dest = dest or f"{col}_metaphone"
    out = []
    for row in rows:
        new = dict(row)
        new[dest] = _metaphone(row.get(col, ""))
        out.append(new)
    return out


def phonetic_many(
    rows: List[Dict[str, str]],
    specs: List[Dict],
) -> List[Dict[str, str]]:
    """Apply multiple phonetic encodings.

    Each spec: {"col": str, "method": "soundex"|"metaphone", "dest": str|None}
    """
    for spec in specs:
        method = spec.get("method", "soundex")
        col = spec["col"]
        dest = spec.get("dest")
        if method == "metaphone":
            rows = metaphone_column(rows, col, dest)
        else:
            rows = soundex_column(rows, col, dest)
    return rows
