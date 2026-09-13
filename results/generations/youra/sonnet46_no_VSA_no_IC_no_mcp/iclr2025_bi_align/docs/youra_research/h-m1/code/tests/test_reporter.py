"""Spec compliance tests for src/reporting/reporter.py (H-M1)."""
import json
import numpy as np
import pytest
from src.reporting.reporter import print_report, save_results, save_divergence_curve
import pandas as pd


def _make_results(gate_pass=True):
    return {
        "dataset": "Coste2023",
        "n_kl_levels": 10,
        "baseline_rm": 0.12,
        "baseline_gold": 0.52,
        "gate_pass": gate_pass,
        "rho_rm_kl": 0.988,
        "p_rho": 0.0001,
        "monotone_pass": gate_pass,
        "mono_reason": "PASS: rho=0.988",
        "peak_idx": 3,
        "peak_kl": 2.0,
        "reversal_confirmed": gate_pass,
        "peak_kl_valid": True,
        "peak_reason": "PASS: peak at 2.0",
        "divergence_final": 1.70,
        "divergence_max": 1.70,
        "divergence_positive": True,
        "div_reason": "PASS: divergence_final=1.70",
    }


def test_save_results_creates_json(tmp_path):
    out = tmp_path / "h_m1_results.json"
    save_results(_make_results(True), str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["hypothesis_id"] == "h-m1"
    assert "gate_pass" in data
    assert "rho_rm_kl" in data
    assert "reversal_confirmed" in data


def test_print_report_pass(capsys):
    print_report(_make_results(True))
    out = capsys.readouterr().out
    assert "PASS" in out


def test_print_report_fail(capsys):
    print_report(_make_results(False))
    out = capsys.readouterr().out
    assert "FAIL" in out


def test_save_divergence_curve(tmp_path):
    kl = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    rm = np.array([0.1, 0.5, 1.0, 1.5, 1.8])
    gold = np.array([0.5, 0.6, 0.55, 0.45, 0.35])
    df = pd.DataFrame({"kl_budget": kl, "rm_score": rm, "gold_preference": gold})
    div = rm - gold
    out = tmp_path / "curve.csv"
    save_divergence_curve(df, div, str(out))
    assert out.exists()
    loaded = pd.read_csv(out)
    assert "divergence_gap" in loaded.columns
    assert len(loaded) == 5
