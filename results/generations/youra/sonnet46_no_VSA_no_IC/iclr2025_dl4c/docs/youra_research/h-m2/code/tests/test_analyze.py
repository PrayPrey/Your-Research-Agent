import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np
from analyze import extract_frac_zero_std, compute_gate_metrics


def make_log_history(vals, key="frac_reward_zero_std"):
    return [{key: v, "step": i+1} for i, v in enumerate(vals)]


def test_extract_frac_zero_std_basic():
    log = make_log_history([0.8, 0.7, 0.6])
    vals = extract_frac_zero_std(log)
    assert vals == [0.8, 0.7, 0.6]


def test_extract_frac_zero_std_missing_raises():
    log = [{"loss": 0.5, "step": 1}]
    with pytest.raises(ValueError, match="frac_reward_zero_std"):
        extract_frac_zero_std(log)


def test_extract_frac_zero_std_skips_entries_without_key():
    log = [{"loss": 0.5}, {"frac_reward_zero_std": 0.7, "step": 2}]
    vals = extract_frac_zero_std(log)
    assert vals == [0.7]


def test_compute_gate_metrics_variance_wins():
    frac_var = [0.5] * 50  # lower
    frac_rnd = [0.7] * 50  # higher
    g = compute_gate_metrics(frac_var, frac_rnd)
    assert g["primary_gate_pass"] is True
    assert g["checkpoint_10"]["gate_pass"] is True
    assert g["checkpoint_10"]["gap_pp"] == pytest.approx(0.2)
    assert g["secondary_gate_pass"] is True  # gap 0.2 >= 0.05


def test_compute_gate_metrics_variance_loses():
    frac_var = [0.7] * 50
    frac_rnd = [0.5] * 50
    g = compute_gate_metrics(frac_var, frac_rnd)
    assert g["primary_gate_pass"] is False
    assert g["secondary_gate_pass"] is False


def test_compute_gate_metrics_partial_pass():
    """Passes at step 10 but fails at step 50."""
    frac_var = [0.5] * 10 + [0.8] * 40
    frac_rnd = [0.7] * 10 + [0.6] * 40
    g = compute_gate_metrics(frac_var, frac_rnd)
    assert g["checkpoint_10"]["gate_pass"] is True
    assert g["checkpoint_50"]["gate_pass"] is False
    assert g["primary_gate_pass"] is False
