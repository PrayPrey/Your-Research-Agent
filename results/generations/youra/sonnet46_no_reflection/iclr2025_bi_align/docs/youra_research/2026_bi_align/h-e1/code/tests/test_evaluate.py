"""Tests for evaluate.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import tempfile
import numpy as np
import pandas as pd
import pytest

from evaluate import (
    compute_metrics, check_gate, save_metrics, save_model_summary, save_pairs_df,
    GATE_BETA4_MIN, GATE_OR_MIN, GATE_PVAL_MAX, GATE_CI_LO_MIN,
    RESULTS_DIR, METRICS_FILE,
)
from experiment import fit_baseline_model, fit_proposed_model, compute_supply_prop


def _make_df_pairs(n_per_split=600, n_clusters=120):
    rng = np.random.default_rng(42)
    n = n_per_split * 2
    split = np.array([0] * n_per_split + [1] * n_per_split)
    cluster_id = rng.integers(0, n_clusters, size=n)
    delta_aifs = rng.normal(0.1, 0.5, size=n)
    delta_length = rng.normal(0.0, 10.0, size=n)
    delta_aifs_x_split = delta_aifs * split
    chosen = rng.integers(0, 2, size=n)
    return pd.DataFrame({
        "chosen": chosen,
        "delta_aifs": delta_aifs,
        "delta_length": delta_length,
        "delta_aifs_x_split": delta_aifs_x_split,
        "split": split,
        "cluster_id": cluster_id,
    })


def test_compute_metrics_keys():
    df = _make_df_pairs()
    rb = fit_baseline_model(df)
    rp = fit_proposed_model(df)
    metrics = compute_metrics(rb, rp)
    required = {"beta4", "OR", "CI_lo", "CI_hi", "pval",
                "mcfadden_r2_baseline", "mcfadden_r2_proposed",
                "lrt_stat", "lrt_pval"}
    assert required.issubset(set(metrics.keys()))


def test_compute_metrics_or_is_exp_beta4():
    df = _make_df_pairs()
    rb = fit_baseline_model(df)
    rp = fit_proposed_model(df)
    metrics = compute_metrics(rb, rp)
    assert abs(metrics["OR"] - np.exp(metrics["beta4"])) < 1e-9


def test_check_gate_true():
    metrics = {
        "beta4": 0.5,
        "OR": 1.65,
        "CI_lo": 1.2,
        "CI_hi": 2.1,
        "pval": 0.001,
    }
    assert check_gate(metrics) is True


def test_check_gate_false_beta4():
    metrics = {"beta4": -0.1, "OR": 1.2, "CI_lo": 1.05, "pval": 0.005}
    assert check_gate(metrics) is False


def test_check_gate_false_or():
    metrics = {"beta4": 0.05, "OR": 1.05, "CI_lo": 1.01, "pval": 0.005}
    assert check_gate(metrics) is False


def test_check_gate_false_pval():
    metrics = {"beta4": 0.5, "OR": 1.5, "CI_lo": 1.2, "pval": 0.05}
    assert check_gate(metrics) is False


def test_check_gate_false_ci_lo():
    metrics = {"beta4": 0.5, "OR": 1.5, "CI_lo": 0.95, "pval": 0.005}
    assert check_gate(metrics) is False


def test_gate_constants():
    assert GATE_BETA4_MIN == 0.0
    assert GATE_OR_MIN == 1.10
    assert GATE_PVAL_MAX == 0.01
    assert GATE_CI_LO_MIN == 1.0


def test_save_metrics_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr("evaluate.RESULTS_DIR", str(tmp_path))
    monkeypatch.setattr("evaluate.METRICS_FILE", str(tmp_path / "metrics.json"))
    metrics = {"beta4": 0.5, "OR": 1.65, "CI_lo": 1.2, "CI_hi": 2.1,
               "pval": 0.001, "mcfadden_r2_baseline": 0.01,
               "mcfadden_r2_proposed": 0.02, "lrt_stat": 5.0, "lrt_pval": 0.02}
    save_metrics(metrics, gate_passed=True)
    out_file = tmp_path / "metrics.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["gate_passed"] is True
    assert "beta4" in data


def test_save_pairs_df_creates_parquet(tmp_path, monkeypatch):
    monkeypatch.setattr("evaluate.RESULTS_DIR", str(tmp_path))
    monkeypatch.setattr("evaluate.PAIRS_DF_FILE", str(tmp_path / "pairs_df.parquet"))
    df = _make_df_pairs(n_per_split=10, n_clusters=5)
    save_pairs_df(df)
    assert (tmp_path / "pairs_df.parquet").exists()
