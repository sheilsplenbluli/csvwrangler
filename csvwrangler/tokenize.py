"""Tokenize text columns — split values into word-count or unique-token sets."""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List


def _tokenize(value: str, pattern: str = r"\w+", lower: bool = True) -> List[str]:
    """Return a list of tokens from *value*."""
    text = value.lower() if lower else value
    return re.findall(pattern, text)


def token_count(
    rows: Iterable[Dict],
    column: str,
    dest: str = "",
    pattern: str = r"\w+",
    lower: bool = True,
) -> List[Dict]:
    """Add a column with the number of tokens in *column*."""
    dest = dest or f"{column}_token_count"
    result = []
    for row in rows:
        new = dict(row)
        tokens = _tokenize(new.get(column, ""), pattern=pattern, lower=lower)
        new[dest] = str(len(tokens))
        result.append(new)
    return result


def unique_token_count(
    rows: Iterable[Dict],
    column: str,
    dest: str = "",
    pattern: str = r"\w+",
    lower: bool = True,
) -> List[Dict]:
    """Add a column with the number of *unique* tokens in *column*."""
    dest = dest or f"{column}_unique_tokens"
    result = []
    for row in rows:
        new = dict(row)
        tokens = _tokenize(new.get(column, ""), pattern=pattern, lower=lower)
        new[dest] = str(len(set(tokens)))
        result.append(new)
    return result


def top_tokens(
    rows: Iterable[Dict],
    column: str,
    n: int = 10,
    pattern: str = r"\w+",
    lower: bool = True,
) -> List[Dict]:
    """Return a frequency table of the top *n* tokens across all rows."""
    counter: Counter = Counter()
    for row in rows:
        tokens = _tokenize(row.get(column, ""), pattern=pattern, lower=lower)
        counter.update(tokens)
    total = sum(counter.values()) or 1
    return [
        {"token": token, "count": str(count), "percent": f"{100 * count / total:.2f}"}
        for token, count in counter.most_common(n)
    ]


def tokenize_many(
    rows: Iterable[Dict],
    specs: List[Dict],
) -> List[Dict]:
    """Apply multiple tokenize operations.

    Each spec: {"column": str, "mode": "count"|"unique", "dest": str (optional)}
    """
    rows = list(rows)
    for spec in specs:
        col = spec["column"]
        mode = spec.get("mode", "count")
        dest = spec.get("dest", "")
        if mode == "unique":
            rows = unique_token_count(rows, col, dest=dest)
        else:
            rows = token_count(rows, col, dest=dest)
    return rows
