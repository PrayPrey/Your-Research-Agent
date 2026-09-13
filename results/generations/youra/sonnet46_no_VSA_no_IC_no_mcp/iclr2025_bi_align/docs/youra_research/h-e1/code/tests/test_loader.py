import pytest
import pandas as pd
import tempfile, os
from src.data.loader import load_dataset


def _write_csv(rows, path):
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def test_load_valid_csv(tmp_path):
    p = tmp_path / "valid.csv"
    _write_csv([
        {"kl_budget": i*0.5, "rm_score": float(i), "gold_preference": 0.5+i*0.01}
        for i in range(7)
    ], p)
    df = load_dataset(str(p), "Test")
    assert all(c in df.columns for c in ["kl_budget", "rm_score", "gold_preference"])


def test_load_missing_column(tmp_path):
    p = tmp_path / "missing.csv"
    pd.DataFrame({"kl_budget": [1, 2, 3, 4, 5], "rm_score": [1, 2, 3, 4, 5]}).to_csv(p, index=False)
    with pytest.raises(ValueError, match="missing columns"):
        load_dataset(str(p), "Test")


def test_load_too_few_rows(tmp_path):
    p = tmp_path / "few.csv"
    _write_csv([
        {"kl_budget": i, "rm_score": float(i), "gold_preference": 0.5}
        for i in range(4)
    ], p)
    with pytest.raises(ValueError, match="non-null paired rows"):
        load_dataset(str(p), "Test")
