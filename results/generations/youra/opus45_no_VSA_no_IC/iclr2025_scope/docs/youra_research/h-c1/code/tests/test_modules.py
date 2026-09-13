"""Basic tests for h-c1 modules."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np
import pandas as pd


def test_config_imports():
    """Test config module loads correctly."""
    from config import MODELS, RANKS, SEEDS, TrainConfig, Paths, ComparisonConfig
    assert len(MODELS) == 4
    assert len(RANKS) == 6
    assert len(SEEDS) == 3
    assert TrainConfig().max_length == 512  # HotpotQA override
    assert ComparisonConfig().alpha_diff_threshold == 0.15


def test_data_hotpot_concat():
    """Test context concatenation logic."""
    from data_hotpot import _concat_context

    example = {
        "context": {
            "title": ["Doc1", "Doc2"],
            "sentences": [["Sentence 1.", "Sentence 2."], ["Sentence 3."]]
        }
    }
    result = _concat_context(example)
    assert "Doc1:" in result
    assert "Doc2:" in result
    assert "Sentence 1." in result
    assert "Sentence 3." in result


def test_analyze_compute_r_opt(tmp_path):
    """Test r_opt extraction from sweep CSV."""
    from analyze import compute_r_opt

    sweep_csv = tmp_path / "sweep.csv"
    sweep_csv.write_text(
        "model,rank,seed,f1_score\n"
        "pythia-1b,4,42,0.5\n"
        "pythia-1b,8,42,0.6\n"
        "pythia-1b,16,42,0.55\n"
        "pythia-1b,4,1337,0.52\n"
        "pythia-1b,8,1337,0.58\n"
        "pythia-1b,16,1337,0.6\n"
    )

    output_csv = tmp_path / "optimal.csv"
    df = compute_r_opt(str(sweep_csv), str(output_csv))

    assert len(df) == 2  # 1 model x 2 seeds
    assert (df["r_opt"] == 8).sum() == 1  # seed 42: best at rank 8
    assert (df["r_opt"] == 16).sum() == 1  # seed 1337: best at rank 16


def test_analyze_fit_scaling(tmp_path):
    """Test scaling law fit on synthetic data."""
    from analyze import fit_scaling_law

    optimal_df = pd.DataFrame({
        "model": ["m1", "m1", "m1", "m2", "m2", "m2"],
        "N": [1e9, 1e9, 1e9, 1e10, 1e10, 1e10],
        "seed": [42, 1337, 2024, 42, 1337, 2024],
        "r_opt": [10, 10, 10, 30, 30, 30],
        "best_f1": [0.5] * 6,
    })

    output_json = tmp_path / "fit.json"
    result = fit_scaling_law(optimal_df, n_bootstrap=100, output_json=str(output_json))

    assert "alpha" in result
    assert "alpha_ci_low" in result
    assert "alpha_ci_high" in result
    assert 0 < result["alpha"] < 1


def test_compare_alphas(tmp_path):
    """Test cross-task alpha comparison."""
    from compare import compare_alphas

    fit_squad = {"alpha": 0.5, "alpha_ci_low": 0.4, "alpha_ci_high": 0.6}
    fit_hotpot = {"alpha": 0.55, "alpha_ci_low": 0.45, "alpha_ci_high": 0.65}

    output_json = tmp_path / "comparison.json"
    result = compare_alphas(fit_squad, fit_hotpot, str(output_json))

    assert result["alpha_diff"] == pytest.approx(0.05, abs=0.001)
    assert result["ci_overlap"] is True
    assert result["pass_diff"] is True
    assert result["overall_pass"] is True


def test_compare_alphas_fail(tmp_path):
    """Test cross-task comparison failure case."""
    from compare import compare_alphas

    fit_squad = {"alpha": 0.3, "alpha_ci_low": 0.2, "alpha_ci_high": 0.4}
    fit_hotpot = {"alpha": 0.6, "alpha_ci_low": 0.5, "alpha_ci_high": 0.7}

    output_json = tmp_path / "comparison_fail.json"
    result = compare_alphas(fit_squad, fit_hotpot, str(output_json))

    assert result["alpha_diff"] == pytest.approx(0.3, abs=0.001)
    assert result["pass_diff"] is False
    assert result["overall_pass"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
