"""Preprocessing: filter, convert, normalize, dedup Papers With Code entries."""
import numpy as np
from datetime import datetime


def preprocess(
    raw: list[dict],
    release_date: str,
    min_date: str = "2019-01-01",
    min_entries: int = 50,
) -> tuple[np.ndarray, np.ndarray]:
    """Filter, convert, normalize, dedup raw API entries.

    Args:
        raw: list of {"date": str|None, "score": float} dicts
        release_date: "YYYY-MM-DD" benchmark release date
        min_date: earliest valid entry date
        min_entries: minimum entries required after dedup

    Returns:
        (t_months [M,], scores [M,]) sorted by t ascending

    Raises:
        ValueError if entries after dedup < min_entries
    """
    rel = datetime.strptime(release_date, "%Y-%m-%d")
    min_dt = datetime.strptime(min_date, "%Y-%m-%d")

    filtered = []
    for entry in raw:
        if entry.get("date") is None:
            continue
        try:
            dt = datetime.strptime(entry["date"][:10], "%Y-%m-%d")
        except (ValueError, TypeError):
            continue
        if dt < min_dt:
            continue
        t_raw = (dt - rel).days / 30.44
        y_raw = float(entry["score"]) / 100.0
        filtered.append((t_raw, y_raw))

    if not filtered:
        raise ValueError(f"No valid entries after date filtering (need {min_entries})")

    t_arr = np.array([x[0] for x in filtered], dtype=np.float64)
    y_arr = np.array([x[1] for x in filtered], dtype=np.float64)

    # Month-bin deduplication: keep max score per integer month bin
    month_bins = np.floor(t_arr).astype(int)
    unique_bins = np.unique(month_bins)
    t_dedup, y_dedup = [], []
    for b in unique_bins:
        mask = month_bins == b
        best_idx = np.argmax(y_arr[mask])
        t_dedup.append(t_arr[mask][best_idx])
        y_dedup.append(y_arr[mask][best_idx])

    t_out = np.array(t_dedup, dtype=np.float64)
    y_out = np.array(y_dedup, dtype=np.float64)

    # Sort by t ascending
    order = np.argsort(t_out)
    t_out, y_out = t_out[order], y_out[order]

    if len(t_out) < min_entries:
        raise ValueError(
            f"Only {len(t_out)} entries after dedup, need {min_entries}"
        )

    return t_out, y_out
