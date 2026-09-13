"""Spec tests for D-2 A2-v2 protocol-internal anchor (FR-4.1/4.2, FR-6.1).

v2 delta: check_anchor_and_halt no longer compares against H_E1_REFERENCES and
NEVER raises SystemExit on any AUROC value. It returns the within-sweep
final-layer (L32) entropy corrected AUROC and emits the clause-(c) descriptive
direction-consistency log. Both v1 ValueError contract guards are retained
byte-identical (empty selection split; single-class labels).
"""
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis import corrected_auroc, verify_mechanism_activated
from run_h_e1 import check_anchor_and_halt


def _cache_df(labels, entropy_l32, split="selection"):
    n = len(labels)
    return pd.DataFrame({
        "example_id": range(n), "dataset": ["triviaqa"] * n,
        "model": ["llama2"] * n, "split": [split] * n,
        "label": labels, "entropy_L32": entropy_l32,
    })


def _frames_across_auroc_range():
    """Frames spanning near-chance to perfectly separable (corrected AUROC 1.0,
    >0.55 away from every v1 reference) — v1 raised SystemExit on the extremes."""
    near_chance = _cache_df([0] * 50 + [1] * 50,
                            list(range(50)) + [25.5] * 50)          # AUROC 0.52
    separable = _cache_df([0] * 20 + [1] * 20,
                          list(range(20)) + list(range(100, 120)))  # AUROC 1.00
    inverted = _cache_df([0] * 20 + [1] * 20,
                         list(range(100, 120)) + list(range(20)))   # flipped -> 1.00
    return [near_chance, separable, inverted]


def test_anchor_no_systemexit_on_any_auroc_value():
    for df in _frames_across_auroc_range():
        result = check_anchor_and_halt("llama2", "triviaqa", df)  # must not raise
        assert isinstance(result, float)


def test_anchor_returns_final_auroc():
    df = _frames_across_auroc_range()[0]
    sel = df[df["split"] == "selection"]
    expected, _ = corrected_auroc(sel["label"].to_numpy(),
                                  sel["entropy_L32"].to_numpy())
    assert check_anchor_and_halt("llama2", "triviaqa", df) == pytest.approx(expected)


def test_anchor_clause_c_log_emitted(caplog):
    with caplog.at_level(logging.INFO, logger="h_e1.run"):
        check_anchor_and_halt("llama2", "triviaqa", _frames_across_auroc_range()[0])
    assert "A2-v2 anchor:" in caplog.text
    assert "consistent=" in caplog.text


def test_anchor_pending_split_valueerror():
    df = _cache_df([0, 1] * 10, [0.5] * 20, split="pending")
    with pytest.raises(ValueError):
        check_anchor_and_halt("llama2", "triviaqa", df)


def test_anchor_single_class_valueerror():
    df = _cache_df([1] * 20, list(range(20)))
    with pytest.raises(ValueError):
        check_anchor_and_halt("llama2", "triviaqa", df)


def test_verify_mechanism_activated_no_h_e1_references():
    """Gap A closure: detail keyed by protocol-internal anchor_computed, no
    H_E1_REFERENCES-backed baseline_reproduced."""
    signals = {"entropy": np.linspace(1.0, 5.0, 32), "model_key": "llama2",
               "dataset_name": "triviaqa", "final_layer_entropy_auroc": 0.60}
    grid = np.tile(np.linspace(0.5, 0.7, 20), (3, 1)).T  # std > 0.01
    ok, detail = verify_mechanism_activated(signals, grid,
                                            "Lens sweep: model=llama2 ...")
    assert "baseline_reproduced" not in detail
    assert detail["anchor_computed"] is True
    assert ok is True
