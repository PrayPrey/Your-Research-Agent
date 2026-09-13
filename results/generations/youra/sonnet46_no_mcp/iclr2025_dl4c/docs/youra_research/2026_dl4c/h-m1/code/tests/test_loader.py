"""Tests for A-2 LogLoader (loader.py) - spec compliance tests."""

import os
import sys
import tempfile
import numpy as np
import pandas as pd
import pytest

# Add analysis dir to path
_ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), "..", "analysis")
sys.path.insert(0, _ANALYSIS_DIR)

from loader import (
    load_reward_density_logs,
    validate_full_training,
    compute_early_phase_density,
    compute_late_phase_density,
    CONDITIONS,
    WINDOW_SIZE,
)


def _make_logs(tmpdir, n_rows=20):
    """Create synthetic CSV logs with n_rows steps."""
    os.makedirs(tmpdir, exist_ok=True)
    for cond in CONDITIONS:
        rows = [{"step": i + 1, "reward_density": 0.7 if cond == "curriculum" else 0.5}
                for i in range(n_rows)]
        pd.DataFrame(rows).to_csv(os.path.join(tmpdir, f"reward_density_{cond}.csv"), index=False)


class TestLoadRewardDensityLogs:
    def test_returns_dict_with_all_conditions(self, tmp_path):
        _make_logs(str(tmp_path))
        logs = load_reward_density_logs(str(tmp_path))
        assert set(logs.keys()) == set(CONDITIONS)

    def test_dataframe_has_required_columns(self, tmp_path):
        _make_logs(str(tmp_path))
        logs = load_reward_density_logs(str(tmp_path))
        for df in logs.values():
            assert "step" in df.columns
            assert "reward_density" in df.columns

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_reward_density_logs(str(tmp_path))


class TestValidateFullTraining:
    def test_returns_true_when_sufficient(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=20)
        logs = load_reward_density_logs(str(tmp_path))
        valid, counts = validate_full_training(logs, min_rows=10)
        assert valid is True
        assert all(c >= 10 for c in counts.values())

    def test_raises_valueerror_when_insufficient(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=5)
        logs = load_reward_density_logs(str(tmp_path))
        with pytest.raises(ValueError, match="Run run_training.py first"):
            validate_full_training(logs, min_rows=10)

    def test_error_message_contains_condition_and_count(self, tmp_path):
        _make_logs(str(tmp_path), n_rows=3)
        logs = load_reward_density_logs(str(tmp_path))
        with pytest.raises(ValueError) as exc:
            validate_full_training(logs, min_rows=10)
        assert "3" in str(exc.value)


class TestComputeEarlyPhaseDensity:
    def test_returns_ndarray_shape_5_for_2500_steps(self, tmp_path):
        # Build 2500-row log
        rows = [{"step": i + 1, "reward_density": 0.8} for i in range(2500)]
        df = pd.DataFrame(rows)
        result = compute_early_phase_density(df, max_step=2500, window_size=500)
        assert isinstance(result, np.ndarray)
        assert result.shape == (5,)

    def test_window_aggregation_uses_groupby(self, tmp_path):
        # Steps 1-500 all density=0.8, steps 501-1000 all density=0.6
        rows = (
            [{"step": i + 1, "reward_density": 0.8} for i in range(500)] +
            [{"step": i + 501, "reward_density": 0.6} for i in range(500)]
        )
        df = pd.DataFrame(rows)
        result = compute_early_phase_density(df, max_step=1000, window_size=500)
        assert abs(result[0] - 0.8) < 1e-6
        assert abs(result[1] - 0.6) < 1e-6

    def test_returns_float_array(self, tmp_path):
        rows = [{"step": i + 1, "reward_density": 0.7} for i in range(2500)]
        df = pd.DataFrame(rows)
        result = compute_early_phase_density(df)
        assert result.dtype == float


class TestComputeLatePhaseDensity:
    def test_returns_ndarray_shape_5_for_full_training(self):
        rows = [{"step": i + 1, "reward_density": 0.5} for i in range(5000)]
        df = pd.DataFrame(rows)
        result = compute_late_phase_density(df, min_step=2501, window_size=500)
        assert isinstance(result, np.ndarray)
        assert result.shape == (5,)
