import sys
import os
import tempfile
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_loader import load_score_matrix, load_score_matrix_t07, validate_schema
import config

SCORE_MATRIX_PATH = config.SCORE_MATRIX_PATH


def test_load_score_matrix_valid():
    df = load_score_matrix(SCORE_MATRIX_PATH)
    assert df.shape[0] >= 25
    assert "ECE" in df.columns
    assert "TruthfulQA_pct" in df.columns
    assert "MMLU_acc" in df.columns


def test_validate_schema_missing_col():
    df = pd.DataFrame({"ECE": [0.1], "Brier": [0.2]})
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_schema(df, config.REQUIRED_COLS, config.GATE_COLS)


def test_load_t07_missing_returns_empty():
    df = load_score_matrix_t07("/nonexistent/path/score_matrix_t07.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_load_score_matrix_insufficient_rows():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False) as f:
        cols = config.REQUIRED_COLS
        f.write(",".join(cols) + "\n")
        for i in range(5):
            f.write(",".join(["0.1"] * len(cols)) + "\n")
        path = f.name
    with pytest.raises(ValueError, match="Insufficient rows"):
        load_score_matrix(path)
    os.unlink(path)
