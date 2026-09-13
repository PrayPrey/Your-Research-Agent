# Sub-prediction tests module for h-m1
import json
import os
import pandas as pd
from scipy.stats import ttest_ind
from config import PATHS


def quartile_split(df: pd.DataFrame, col: str = "metadata_score") -> tuple:
    """Return (Q1_df, Q4_df) via metadata_quartile."""
    q1 = df[df["metadata_quartile"] == 1]
    q4 = df[df["metadata_quartile"] == 4]
    return q1, q4


def _ttest_quartiles(df: pd.DataFrame, col: str) -> dict:
    """t-test comparing Q4 vs Q1 on given column."""
    q1, q4 = quartile_split(df)

    if len(q1) < 2 or len(q4) < 2:
        return {
            "t_stat": 0.0,
            "p_value": 1.0,
            "mean_q1": 0.0,
            "mean_q4": 0.0,
            "pct_reduction": 0.0,
            "n_q1": len(q1),
            "n_q4": len(q4),
        }

    t, p = ttest_ind(q4[col].dropna(), q1[col].dropna(), equal_var=False)
    mean_q1 = float(q1[col].mean())
    mean_q4 = float(q4[col].mean())
    pct_reduction = 0.0 if mean_q1 == 0 else (mean_q1 - mean_q4) / mean_q1

    return {
        "t_stat": float(t),
        "p_value": float(p),
        "mean_q1": mean_q1,
        "mean_q4": mean_q4,
        "pct_reduction": pct_reduction,
        "n_q1": len(q1),
        "n_q4": len(q4),
    }


def test_p2a(df: pd.DataFrame) -> dict:
    """P2a: t-test H_prep Q4 vs Q1. Expect significant reduction."""
    result = _ttest_quartiles(df, "prep_entropy")
    result["test"] = "P2a"
    result["description"] = "Preprocessing entropy Q4 vs Q1"
    return result


def test_p2b(df: pd.DataFrame) -> dict:
    """P2b: t-test H_hyp Q4 vs Q1. Expect non-significant."""
    result = _ttest_quartiles(df, "hyp_entropy")
    result["test"] = "P2b"
    result["description"] = "Hyperparameter entropy Q4 vs Q1"
    return result


def save_subprediction_results(p2a: dict, p2b: dict, path: str) -> None:
    """Save sub-prediction results to JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"p2a": p2a, "p2b": p2b}, f, indent=2)
    print(f"  Saved sub-prediction results to {path}")
