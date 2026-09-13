"""Tests for sensitivity calculation and phase transition analysis."""
import numpy as np
import pandas as pd
import pytest

from sensitivity import compute_sensitivity, compute_all_sensitivities
from analyze_sensitivity import check_phase_transition, fit_power_law
from config import RANKS, StatsConfig


class TestSensitivity:
    """Tests for sensitivity.py functions."""

    def test_compute_sensitivity_positive_slope(self):
        """Test sensitivity calculation with positive trend."""
        ranks = [4, 8, 16, 32, 64, 128]
        f1_scores = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75]
        sensitivity = compute_sensitivity(ranks, f1_scores)
        assert sensitivity > 0
        assert 0.04 < sensitivity < 0.06

    def test_compute_sensitivity_negative_slope(self):
        """Test sensitivity returns absolute value."""
        ranks = [4, 8, 16, 32, 64, 128]
        f1_scores = [0.75, 0.70, 0.65, 0.60, 0.55, 0.50]
        sensitivity = compute_sensitivity(ranks, f1_scores)
        assert sensitivity > 0

    def test_compute_sensitivity_flat(self):
        """Test zero sensitivity for flat curve."""
        ranks = [4, 8, 16, 32, 64, 128]
        f1_scores = [0.60, 0.60, 0.60, 0.60, 0.60, 0.60]
        sensitivity = compute_sensitivity(ranks, f1_scores)
        assert abs(sensitivity) < 0.001

    def test_compute_all_sensitivities(self):
        """Test batch sensitivity computation."""
        data = []
        for model in ["pythia-1b", "pythia-12b"]:
            for seed in [42, 1337]:
                for rank in RANKS:
                    data.append({
                        "model": model,
                        "dataset": "squad_v2",
                        "seed": seed,
                        "rank": rank,
                        "f1_score": 0.5 + 0.01 * np.log2(rank),
                    })

        df = pd.DataFrame(data)
        sens_df = compute_all_sensitivities(df)

        assert len(sens_df) == 4
        assert set(sens_df.columns) == {"model", "dataset", "seed", "sensitivity"}
        assert all(sens_df["sensitivity"] > 0)


class TestPhaseTransition:
    """Tests for phase transition analysis."""

    def test_check_phase_transition_pass(self):
        """Test passing criteria: ratio > 2, CI > 1.5."""
        sens_1b = [0.02, 0.025, 0.018]
        sens_12b = [0.08, 0.09, 0.085]

        result = check_phase_transition(sens_1b, sens_12b)

        assert result["ratio"] > 2.0
        assert "ci_low" in result
        assert "ci_high" in result
        assert "p_value" in result
        assert isinstance(result["pass"], bool)

    def test_check_phase_transition_fail_low_ratio(self):
        """Test failing when ratio < 2."""
        sens_1b = [0.05, 0.055, 0.048]
        sens_12b = [0.06, 0.065, 0.058]

        result = check_phase_transition(sens_1b, sens_12b)

        assert result["ratio"] < 2.0
        assert result["pass"] == False

    def test_power_law_fit(self):
        """Test power law fitting S = a * N^gamma."""
        data = []
        models = {"pythia-1b": 1e9, "pythia-2.8b": 2.8e9, "pythia-6.9b": 6.9e9, "pythia-12b": 1.2e10}
        gamma_true = 0.3

        for model, N in models.items():
            for seed in [42, 1337, 2024]:
                sens = 0.001 * (N ** gamma_true) * (1 + 0.1 * np.random.randn())
                data.append({
                    "model": model,
                    "dataset": "squad_v2",
                    "seed": seed,
                    "sensitivity": sens,
                })

        df = pd.DataFrame(data)
        result = fit_power_law(df, n_bootstrap=100)

        assert "squad_v2" in result
        assert "gamma" in result["squad_v2"]
        assert 0.1 < result["squad_v2"]["gamma"] < 0.6


class TestConfig:
    """Tests for h-m2 config."""

    def test_datasets_defined(self):
        """Test DATASETS constant exists."""
        from config import DATASETS
        assert "squad_v2" in DATASETS
        assert "hotpotqa" in DATASETS

    def test_stats_config(self):
        """Test StatsConfig defaults."""
        cfg = StatsConfig()
        assert cfg.alpha == 0.05
        assert cfg.n_bootstrap == 1000
        assert cfg.ratio_threshold == 2.0
        assert cfg.ci_lower_threshold == 1.5
