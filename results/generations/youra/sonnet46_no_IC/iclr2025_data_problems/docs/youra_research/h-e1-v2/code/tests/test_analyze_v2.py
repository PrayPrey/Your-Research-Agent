"""Tests for analyze_v2.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np

from analyze_v2 import check_direction_v2, gate_check_v2


def make_test_df(tau_star_14=20, tau_star_31=35):
    """Create synthetic results DataFrame for testing."""
    rows = []
    for scale in [14, 31]:
        for tau in [20, 35, 50]:
            for j in [0.7, 0.9]:
                for seed in [1, 2]:
                    # 14M peaks at tau_star_14, 31M peaks at tau_star_31
                    if scale == 14:
                        acc = 0.4 - 0.02 * abs(tau - tau_star_14)
                    else:
                        acc = 0.4 - 0.02 * abs(tau - tau_star_31)
                    rows.append({
                        "scale": scale,
                        "ppl_threshold": tau,
                        "dedup_j": j,
                        "seed": seed,
                        "hellaswag_acc_norm": acc,
                        "checkpoint_tokens": 1_000_000_000,
                    })
    return pd.DataFrame(rows)


def test_check_direction_v2_returns_keys():
    df = make_test_df(20, 35)
    result = check_direction_v2(df, dv="hellaswag_acc_norm")
    assert "tau_star_14m" in result
    assert "tau_star_31m" in result
    assert "direction_confirmed" in result
    assert "interaction_exists" in result
    assert "above_random" in result


def test_check_direction_v2_correct_tau():
    df = make_test_df(tau_star_14=20, tau_star_31=50)
    result = check_direction_v2(df, dv="hellaswag_acc_norm")
    assert result["tau_star_14m"] == 20
    assert result["tau_star_31m"] == 50


def test_check_direction_v2_direction_confirmed():
    df = make_test_df(tau_star_14=20, tau_star_31=50)
    result = check_direction_v2(df, dv="hellaswag_acc_norm")
    assert result["direction_confirmed"] is True


def test_check_direction_v2_direction_failed():
    # When 14M has higher tau_star than 31M
    df = make_test_df(tau_star_14=50, tau_star_31=20)
    result = check_direction_v2(df, dv="hellaswag_acc_norm")
    assert result["direction_confirmed"] is False


def test_gate_check_v2_pass():
    analysis = {
        "direction_confirmed": True,
        "above_random": True,
        "interaction_exists": True,
        "tau_star_14m": 20,
        "tau_star_31m": 35,
    }
    gate = gate_check_v2(analysis)
    assert gate["passed"] is True
    assert gate["reason"] == "PASS"


def test_gate_check_v2_fail_direction():
    analysis = {
        "direction_confirmed": False,
        "above_random": True,
        "interaction_exists": True,
        "tau_star_14m": 50,
        "tau_star_31m": 20,
    }
    gate = gate_check_v2(analysis)
    assert gate["passed"] is False
    assert "direction FAILED" in gate["reason"]


def test_gate_check_v2_fail_above_random():
    analysis = {
        "direction_confirmed": True,
        "above_random": False,
        "interaction_exists": True,
        "tau_star_14m": 20,
        "tau_star_31m": 35,
    }
    gate = gate_check_v2(analysis)
    assert gate["passed"] is False


def test_gate_check_v2_no_ancova_needed():
    # v2 gate should NOT require ANCOVA fields (p_value, eta2)
    analysis = {
        "direction_confirmed": True,
        "above_random": True,
        "interaction_exists": True,
        "tau_star_14m": 20,
        "tau_star_31m": 50,
        # No ANCOVA fields
    }
    gate = gate_check_v2(analysis)
    assert "p_value_passes" not in gate.get("checks", {})
    assert gate["passed"] is True
