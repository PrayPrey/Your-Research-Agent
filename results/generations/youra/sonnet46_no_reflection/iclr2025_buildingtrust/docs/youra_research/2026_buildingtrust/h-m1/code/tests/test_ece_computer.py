"""test_ece_computer.py — Unit tests for ECEComputer."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ece_computer import ECEComputer, compute_ece_scores
import config


class TestECEComputer:
    @pytest.fixture
    def computer(self):
        return ECEComputer(n_bootstrap=50, seed=config.TEST_SEED)

    @pytest.fixture
    def mock_probs_labels(self):
        rng = np.random.default_rng(config.TEST_SEED)
        n = 100
        probs = rng.uniform(0.0, 1.0, size=n)
        labels = (rng.uniform(size=n) < probs).astype(float)
        return probs, labels

    def test_compute_ece_returns_scalar(self, computer, mock_probs_labels):
        probs, labels = mock_probs_labels
        ece = computer.compute_ece(probs, labels)
        assert isinstance(ece, float)
        assert 0.0 <= ece <= 1.0

    def test_compute_ece_ci_returns_tuple(self, computer, mock_probs_labels):
        probs, labels = mock_probs_labels
        ci_low, ci_high = computer.compute_ece_ci(probs, labels)
        assert ci_low <= ci_high
        assert 0.0 <= ci_low
        assert ci_high <= 1.0

    def test_mock_ece_shape(self, computer):
        n = 30
        model_ids = [f"model_{i}" for i in range(n)]
        df = computer._mock_ece(n, model_ids)
        assert df.shape == (30, 4)
        assert "ECE" in df.columns
        assert (df["ECE"] >= 0.0).all()
        assert (df["ECE"] <= 1.0).all()

    def test_load_or_compute_mock_fallback(self, computer):
        """load_or_compute with no logits returns mock DataFrame."""
        model_ids = [f"model_{i}" for i in range(30)]
        df = computer.load_or_compute(model_ids, model_logit_paths=None)
        assert len(df) == 30
        assert "ECE" in df.columns
        assert df["ECE"].isna().sum() == 0

    def test_load_or_compute_uses_cache(self, computer, tmp_path):
        """load_or_compute loads from cache when available."""
        import pandas as pd
        model_ids = [f"model_{i}" for i in range(30)]
        cache_data = pd.DataFrame({
            "model_id": model_ids,
            "ECE": [0.1] * 30,
            "ECE_ci_lower": [0.08] * 30,
            "ECE_ci_upper": [0.12] * 30,
        })
        cache_data.to_csv(tmp_path / "ece_scores.csv", index=False)
        computer.cache_dir = tmp_path
        df = computer.load_or_compute(model_ids, force_recompute=False)
        assert len(df) == 30

    def test_compute_ece_invalid_probs_raises(self, computer):
        """compute_ece raises AssertionError for out-of-range probs."""
        probs = np.array([0.5, 1.5, 0.3])
        labels = np.array([1.0, 0.0, 1.0])
        with pytest.raises(AssertionError):
            computer.compute_ece(probs, labels)
