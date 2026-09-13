import pytest
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import (
    REQUIRED_COLS, COMPOSITE_COLS, BASELINE_COLS, TARGET_COL,
    TEST_N_MODELS, TEST_SEED,
)


@pytest.fixture
def synthetic_score_matrix():
    rng = np.random.default_rng(TEST_SEED)
    n = TEST_N_MODELS
    df = pd.DataFrame({
        "model_id":        [f"model_{i}" for i in range(n)],
        "ECE":             rng.uniform(0.01, 0.30, n),
        "Brier":           rng.uniform(0.05, 0.40, n),
        "TruthfulQA_pct":  rng.uniform(0.20, 0.80, n),
        "AdvGLUE_drop":    rng.uniform(0.0,  0.50, n),
        "ANLI_drop":       rng.uniform(0.0,  0.40, n),
        "MMLU_acc":        rng.uniform(0.30, 0.85, n),
        "HumanEval_pass1": rng.uniform(0.0,  0.60, n),
        "family":          [f"family_{i % 3}" for i in range(n)],
    })
    threshold = df["AdvGLUE_drop"].quantile(0.75)
    df[TARGET_COL] = (df["AdvGLUE_drop"] >= threshold).astype(int)
    return df


@pytest.fixture
def results_dir(tmp_path):
    d = tmp_path / "results"
    d.mkdir()
    return d


@pytest.fixture
def figures_dir(tmp_path):
    d = tmp_path / "figures"
    d.mkdir()
    return d
