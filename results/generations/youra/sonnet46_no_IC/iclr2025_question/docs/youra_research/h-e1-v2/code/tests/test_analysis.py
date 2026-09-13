"""Smoke checks for analysis.py (task-006/012/013/014, LIGHT tier)."""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis import (corrected_auroc, degeneracy_screen, evaluate_gate,
                      check_baseline_anchor, verify_mechanism_activated,
                      _nan_to_none)


def test_corrected_auroc_flips_sub_half():
    labels = np.array([0, 0, 1, 1])
    scores = np.array([0.9, 0.8, 0.2, 0.1])  # perfectly anti-correlated
    auc, flipped = corrected_auroc(labels, scores)
    assert auc == 1.0 and flipped


def test_degeneracy_screen_drops_uniform_entropy_layer():
    V = 32000
    grid = np.full((10, 32), 5.0)
    grid[:, 3] = math.log(V)          # layer 3 exactly ln|V| -> dropped
    top1 = np.full(32, 0.5)
    top1[0] = 0.01                    # layer 0 <5% agreement -> dropped
    retained = degeneracy_screen(grid, top1, V)
    assert 3 not in retained and 0 not in retained and 10 in retained


def test_evaluate_gate_all_nan_returns_fail_not_crash():
    grid = np.full((3, 3), np.nan)
    out = evaluate_gate(grid, [5, 10, 31])
    assert out["gate_pass"] is False and out["best_layer"] is None


def test_evaluate_gate_intermediate_only_and_depth_check():
    grid = np.array([[0.70, 0.60, 0.55],   # layer idx 15 (intermediate)
                     [0.52, 0.51, 0.50]])  # layer idx 31 (final)
    out = evaluate_gate(grid, [15, 31])
    assert out["best_layer"] == 16 and out["best_signal"] == "entropy"
    assert out["gate_pass"] and out["depth_beats_final"]
    assert out["final_layer_entropy_auroc"] == 0.52


def test_baseline_anchor_and_nan():
    assert check_baseline_anchor(0.53, "llama2", "triviaqa")
    assert not check_baseline_anchor(0.60, "llama2", "triviaqa")
    assert not check_baseline_anchor(float("nan"), "llama2", "triviaqa")


def test_verify_mechanism_activated():
    signals = {"entropy": np.zeros(32), "model_key": "llama2",
               "dataset_name": "triviaqa", "final_layer_entropy_auroc": 0.52}
    grid = np.array([[0.70, 0.6, 0.5], [0.52, 0.5, 0.5]])
    ok, detail = verify_mechanism_activated(
        signals, grid, "Lens sweep: model=llama2 layers=32 ...")
    assert ok and all(detail.values())


def test_nan_to_none():
    assert _nan_to_none(float("nan")) is None and _nan_to_none(0.5) == 0.5
