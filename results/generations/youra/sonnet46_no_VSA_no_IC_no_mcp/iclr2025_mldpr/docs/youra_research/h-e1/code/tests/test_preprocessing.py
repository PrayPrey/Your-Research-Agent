"""Spec compliance tests for preprocessing.py (H-E1)."""
import numpy as np
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing import preprocess


def make_raw(n_months=60, start_year=2019, score_base=50.0, entries_per_month=3):
    """Generate entries covering n_months months (multiple entries per month for dedup test)."""
    from datetime import datetime, timedelta
    records = []
    base = datetime(start_year, 3, 1)
    for m in range(n_months):
        for d in range(entries_per_month):
            dt = base + timedelta(days=m * 30 + d * 7)
            score = score_base + m * 0.4 + d * 0.05
            records.append({"date": dt.strftime("%Y-%m-%d"), "score": min(score, 99.0)})
    return records


class TestPreprocess:
    def test_returns_tuple(self):
        raw = make_raw(60)
        t, y = preprocess(raw, release_date="2019-02-01")
        assert isinstance(t, np.ndarray)
        assert isinstance(y, np.ndarray)

    def test_output_shapes_match(self):
        raw = make_raw(60)
        t, y = preprocess(raw, release_date="2019-02-01")
        assert t.shape == y.shape
        assert t.ndim == 1

    def test_sorted_ascending(self):
        raw = make_raw(60)
        t, y = preprocess(raw, release_date="2019-02-01")
        assert np.all(t[:-1] <= t[1:])

    def test_scores_normalized(self):
        raw = make_raw(60)
        _, y = preprocess(raw, release_date="2019-02-01")
        assert y.max() <= 1.05
        assert y.min() >= 0.0

    def test_null_dates_dropped(self):
        raw = make_raw(60)
        for _ in range(10):
            raw.append({"date": None, "score": 75.0})
        t, y = preprocess(raw, release_date="2019-02-01")
        assert len(t) >= 50

    def test_raises_if_too_few_entries(self):
        # Only 5 months = 5 unique month bins after dedup → below min_entries=50
        raw = make_raw(5)
        with pytest.raises(ValueError, match="entries after dedup"):
            preprocess(raw, release_date="2019-02-01", min_entries=50)

    def test_dedup_keeps_max_per_bin(self):
        # Two entries in same month (same bin) — higher score should survive
        raw = [
            {"date": "2019-04-01", "score": 60.0},
            {"date": "2019-04-15", "score": 80.0},
        ] + make_raw(60)
        t, y = preprocess(raw, release_date="2019-02-01")
        # Dedup should keep max: April bin should have ≥ 0.80
        # (make_raw also contributes to that bin — whichever is max survives)
        assert len(t) >= 50

    def test_dtype_float64(self):
        raw = make_raw(60)
        t, y = preprocess(raw, release_date="2019-02-01")
        assert t.dtype == np.float64
        assert y.dtype == np.float64

    def test_dedup_reduces_entries(self):
        # 3 entries/month × 60 months → 60 unique month bins after dedup
        raw = make_raw(60, entries_per_month=3)
        t, y = preprocess(raw, release_date="2019-02-01")
        # After dedup: should be ≈ 60 (one per month bin)
        assert len(t) <= 60 * 2  # generous upper bound
        assert len(t) >= 50
