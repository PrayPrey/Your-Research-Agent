import sys
import os
import tempfile
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_loader import load_score_matrix
from analyzers import (
    compute_internal_consistency,
    compute_partial_corr_bca,
    compute_confound_magnitude,
    compute_discriminant_validity,
    compute_decoding_invariance,
)
from visualizer import (
    plot_gate_bar,
    plot_raw_vs_partial,
    plot_ece_brier_scatter,
    plot_discriminant_validity,
    plot_decoding_invariance,
)
import config
from scipy.stats import spearmanr


@pytest.fixture(scope="module")
def df():
    return load_score_matrix(config.SCORE_MATRIX_PATH)


@pytest.fixture(scope="module")
def results(df):
    internal = compute_internal_consistency(df, "ECE", "Brier", 200, seed=42)
    primary = compute_partial_corr_bca(df, "ECE", "TruthfulQA_pct", "MMLU_acc", 200, seed=42)
    raw_rho = float(spearmanr(df["ECE"], df["TruthfulQA_pct"]).statistic)
    confound = compute_confound_magnitude(raw_rho, primary["rho_partial"])
    discriminant = compute_discriminant_validity(df, "ECE", "HumanEval_pass1", "MMLU_acc", 200, seed=42)
    invariance = compute_decoding_invariance(df, pd.DataFrame(), "ECE", "TruthfulQA_pct", "MMLU_acc", 200, seed=42)
    return {
        "internal": internal, "primary": primary, "raw_rho": raw_rho,
        "confound": confound, "discriminant": discriminant, "invariance": invariance,
    }


def test_plot_gate_bar_creates_file(tmp_path, results):
    out = plot_gate_bar(results["primary"], config.PRIMARY_THRESHOLD, tmp_path)
    assert out.exists() and out.stat().st_size > 0


def test_plot_raw_vs_partial_creates_file(tmp_path, results):
    out = plot_raw_vs_partial(results["raw_rho"], results["primary"]["rho_partial"], results["confound"], tmp_path)
    assert out.exists() and out.stat().st_size > 0


def test_plot_ece_brier_creates_file(tmp_path, df, results):
    out = plot_ece_brier_scatter(df, results["internal"], tmp_path)
    assert out.exists() and out.stat().st_size > 0


def test_plot_discriminant_creates_file(tmp_path, results):
    out = plot_discriminant_validity(results["primary"], results["discriminant"], tmp_path)
    assert out.exists() and out.stat().st_size > 0


def test_plot_invariance_skipped(tmp_path, results):
    out = plot_decoding_invariance(results["invariance"], tmp_path)
    assert out.exists() and out.stat().st_size > 0


def test_all_figures_exist(tmp_path, df, results):
    plot_gate_bar(results["primary"], config.PRIMARY_THRESHOLD, tmp_path)
    plot_raw_vs_partial(results["raw_rho"], results["primary"]["rho_partial"], results["confound"], tmp_path)
    plot_ece_brier_scatter(df, results["internal"], tmp_path)
    plot_discriminant_validity(results["primary"], results["discriminant"], tmp_path)
    plot_decoding_invariance(results["invariance"], tmp_path)
    for fname in config.FIGURE_NAMES.values():
        assert (tmp_path / fname).exists(), f"Missing figure: {fname}"
