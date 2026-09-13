"""Spec tests for A-3 anchor pre-gate (task-004/011/012)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from run_h_e1 import check_anchor_and_halt


def _cache_df(labels, entropy_l32, split="selection"):
    n = len(labels)
    return pd.DataFrame({
        "example_id": range(n), "dataset": ["triviaqa"] * n,
        "model": ["llama2"] * n, "split": [split] * n,
        "label": labels, "entropy_L32": entropy_l32,
    })


def _near_chance_frame():
    """Corrected AUROC exactly 0.52 (|0.52 - 0.5186| <= 0.03 -> pass).
    50 negatives scored 0..49; 50 positives all scored 25.5 -> each positive
    beats 26 negatives -> AUROC = 26/50 = 0.52."""
    labels = [0] * 50 + [1] * 50
    scores = list(range(50)) + [25.5] * 50
    return _cache_df(labels, scores)


def test_anchor_pass_within_tolerance():
    assert check_anchor_and_halt("llama2", "triviaqa", _near_chance_frame()) is None


def test_anchor_breach_systemexit_with_delta():
    # perfectly separable -> corrected AUROC 1.0, far outside 0.5186 +/- 0.03
    labels = [0] * 20 + [1] * 20
    scores = list(range(20)) + list(range(100, 120))
    with pytest.raises(SystemExit) as ei:
        check_anchor_and_halt("llama2", "triviaqa", _cache_df(labels, scores))
    msg = str(ei.value)
    assert "delta=" in msg and "llama2" in msg and "triviaqa" in msg


def test_anchor_pending_split_valueerror():
    df = _cache_df([0, 1] * 10, [0.5] * 20, split="pending")
    with pytest.raises(ValueError):
        check_anchor_and_halt("llama2", "triviaqa", df)


def test_anchor_single_class_valueerror():
    df = _cache_df([1] * 20, list(range(20)))
    with pytest.raises(ValueError):
        check_anchor_and_halt("llama2", "triviaqa", df)
