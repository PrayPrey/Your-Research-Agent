"""conftest.py — Shared pytest fixtures for H-M1 test suite."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import config


@pytest.fixture
def mock_model_df() -> pd.DataFrame:
    """30-model DataFrame with correct column schema."""
    rng = np.random.default_rng(config.TEST_SEED)
    n = config.TEST_N_MODELS
    families = config.TEST_MODEL_FAMILIES  # 12 LLaMA, 10 Mistral, 8 Qwen

    # Generate correlated RI and ECE (rho ~ 0.55 to ensure gate passes)
    ri_base = rng.normal(0.0, 0.15, size=n)
    ece_base = 0.12 + 0.4 * ri_base + rng.normal(0.0, 0.03, size=n)
    ece_base = np.clip(ece_base, 0.05, 0.30)

    pc1 = rng.normal(0.0, 1.5, size=n)
    mean_conf = rng.uniform(0.4, 0.8, size=n)

    model_ids = [f"model_{i:02d}" for i in range(n)]
    scales = ["7B"] * 10 + ["13B"] * 10 + ["70B"] * 10

    return pd.DataFrame({
        "model_id": model_ids,
        "model_family": families,
        "scale": scales,
        "training_regime": ["pretrained"] * 15 + ["instruction-tuned"] * 15,
        "PC1": pc1,
        "mean_confidence": mean_conf,
        "advglue_drop": rng.uniform(0.1, 0.4, size=n),
        "RI": ri_base,
        "ECE": ece_base,
    })


@pytest.fixture
def mock_ece_series(mock_model_df: pd.DataFrame) -> pd.Series:
    """ECE series indexed by model_id."""
    return mock_model_df.set_index("model_id")["ECE"]


@pytest.fixture
def mock_ece_df(mock_model_df: pd.DataFrame) -> pd.DataFrame:
    """ECE DataFrame with CI columns."""
    rng = np.random.default_rng(config.TEST_SEED)
    n = len(mock_model_df)
    ece_vals = mock_model_df["ECE"].values
    ci_half = rng.uniform(0.01, 0.03, size=n)
    return pd.DataFrame({
        "model_id": mock_model_df["model_id"].values,
        "ECE": ece_vals,
        "ECE_ci_lower": np.clip(ece_vals - ci_half, 0.0, 1.0),
        "ECE_ci_upper": np.clip(ece_vals + ci_half, 0.0, 1.0),
    })


@pytest.fixture
def mock_partial_corr_results(mock_model_df: pd.DataFrame) -> dict:
    """Pre-computed partial correlation results dict."""
    from partial_corr import PartialCorrAnalyzer
    analyzer = PartialCorrAnalyzer(n_bootstrap=100, seed=config.TEST_SEED)
    return analyzer.run_all(mock_model_df)
