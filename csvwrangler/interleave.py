"""Interleave rows from multiple datasets in round-robin or weighted order."""
from itertools import zip_longest
from typing import Dict, Iterator, List, Optional

_SENTINEL = object()


def interleave_rows(
    datasets: List[List[Dict]],
    fill: Optional[str] = None,
) -> List[Dict]:
    """Round-robin interleave rows from multiple datasets.

    Stops when the shortest dataset is exhausted unless *fill* is given,
    in which case missing cells are filled with *fill* and all rows are kept.
    """
    if not datasets:
        return []

    if fill is None:
        result = []
        for group in zip(*datasets):
            result.extend(group)
        return result

    # Collect all fieldnames across datasets (first-appearance order)
    fieldnames: List[str] = []
    seen: set = set()
    for ds in datasets:
        for row in ds:
            for k in row:
                if k not in seen:
                    fieldnames.append(k)
                    seen.add(k)

    result = []
    for group in zip_longest(*datasets, fillvalue=_SENTINEL):
        for item in group:
            if item is _SENTINEL:
                result.append({f: fill for f in fieldnames})
            else:
                aligned = {f: item.get(f, fill) for f in fieldnames}  # type: ignore[union-attr]
                result.append(aligned)
    return result


def interleave_weighted(
    datasets: List[List[Dict]],
    weights: List[int],
) -> List[Dict]:
    """Interleave rows taking *weight* rows from each dataset in turn.

    Stops when any dataset is exhausted.
    """
    if len(datasets) != len(weights):
        raise ValueError("datasets and weights must be the same length")
    if not datasets:
        return []

    iterators = [iter(ds) for ds in datasets]
    result = []
    try:
        while True:
            for it, w in zip(iterators, weights):
                for _ in range(w):
                    result.append(next(it))
    except StopIteration:
        pass
    return result
