import pytest
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import data_loader
import config


def test_load_score_matrix_returns_dataframe(tmp_path, synthetic_score_matrix):
    # Build a full-size synthetic matrix to satisfy MIN_MODELS constraint
    import numpy as np
    rng = np.random.default_rng(0)
    n = config.MIN_MODELS + 5
    big_df = pd.DataFrame({
        "model_id":        [f"model_{i}" for i in range(n)],
        "ECE":             rng.uniform(0.01, 0.30, n),
        "Brier":           rng.uniform(0.05, 0.40, n),
        "TruthfulQA_pct":  rng.uniform(0.20, 0.80, n),
        "AdvGLUE_drop":    rng.uniform(0.0,  0.50, n),
        "ANLI_drop":       rng.uniform(0.0,  0.40, n),
        "MMLU_acc":        rng.uniform(0.30, 0.85, n),
        "HumanEval_pass1": rng.uniform(0.0,  0.60, n),
    })
    path = tmp_path / "score_matrix.csv"
    big_df.to_csv(path, index=False)
    df = data_loader.load_score_matrix(str(path))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == n


def test_load_score_matrix_missing_file():
    with pytest.raises(FileNotFoundError):
        data_loader.load_score_matrix("/nonexistent/path/score_matrix.csv")


def test_load_score_matrix_too_few_rows(tmp_path, synthetic_score_matrix):
    small = synthetic_score_matrix.head(3)
    path = tmp_path / "small.csv"
    small.to_csv(path, index=False)
    with pytest.raises(ValueError, match="rows"):
        data_loader.load_score_matrix(str(path))


def test_validate_schema_passes(synthetic_score_matrix):
    result = data_loader.validate_schema(
        synthetic_score_matrix,
        config.REQUIRED_COLS,
        ["ECE", "Brier", "TruthfulQA_pct", "AdvGLUE_drop", "MMLU_acc"],
    )
    assert result is True


def test_validate_schema_missing_col(synthetic_score_matrix):
    df = synthetic_score_matrix.drop(columns=["ECE"])
    with pytest.raises(ValueError, match="Missing required columns"):
        data_loader.validate_schema(df, config.REQUIRED_COLS, ["ECE"])


def test_validate_schema_nan_in_gate_col(synthetic_score_matrix):
    df = synthetic_score_matrix.copy()
    df.loc[0, "ECE"] = float("nan")
    with pytest.raises(ValueError, match="NaN values"):
        data_loader.validate_schema(df, config.REQUIRED_COLS, ["ECE"])


def test_add_top_quartile_label():
    import numpy as np
    rng = np.random.default_rng(99)
    n = 20
    raw_df = pd.DataFrame({
        "model_id":        [f"m_{i}" for i in range(n)],
        "AdvGLUE_drop":    rng.uniform(0.0, 0.50, n),
    })
    df = data_loader.add_top_quartile_label(raw_df, "AdvGLUE_drop", 0.75)
    assert config.TARGET_COL in df.columns
    n_pos = df[config.TARGET_COL].sum()
    assert 1 <= n_pos <= n
    # Original df not mutated (raw_df has no TARGET_COL)
    assert config.TARGET_COL not in raw_df.columns
