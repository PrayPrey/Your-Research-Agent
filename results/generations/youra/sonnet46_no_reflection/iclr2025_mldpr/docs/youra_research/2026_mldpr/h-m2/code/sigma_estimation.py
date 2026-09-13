"""H-M1: Sigma Estimation — per-benchmark measurement noise from repeated submissions."""
import pandas as pd
import numpy as np


def estimate_sigma_measurement(pwc_raw: pd.DataFrame) -> pd.Series:
    """Compute per-benchmark sigma from repeated model submissions.
    Groups by (task, dataset, model), takes std of score; then mean per benchmark.
    Fallback: NaN benchmarks get cross-benchmark median.
    Returns: Series indexed by (task, dataset), name='sigma_meas'
    """
    # Per (benchmark, model): std across repeated submissions
    model_std = (
        pwc_raw.groupby(["task", "dataset", "model"])["score"]
        .std()
        .reset_index()
        .rename(columns={"score": "model_score_std"})
    )

    # Per benchmark: mean of model stds
    sigma_map = (
        model_std.groupby(["task", "dataset"])["model_score_std"]
        .mean()
        .rename("sigma_meas")
    )

    # Fill NaN (benchmarks with single submissions per model) with cross-benchmark median
    median_sigma = sigma_map.dropna().median()
    if pd.isna(median_sigma) or median_sigma == 0:
        median_sigma = 1.0  # safe fallback
    sigma_map = sigma_map.fillna(median_sigma)

    # Replace zero sigma with median (avoid division by zero)
    sigma_map = sigma_map.replace(0.0, median_sigma)

    return sigma_map


def get_sigma_map(pwc_raw: pd.DataFrame) -> pd.Series:
    """Alias: calls estimate_sigma_measurement with fallback applied.
    Returns: Series indexed by (task, dataset), name='sigma_meas', no NaNs
    """
    sigma_map = estimate_sigma_measurement(pwc_raw)
    # Guarantee no NaNs
    median_sigma = sigma_map.dropna().median()
    if pd.isna(median_sigma) or median_sigma == 0:
        median_sigma = 1.0
    sigma_map = sigma_map.fillna(median_sigma)
    assert sigma_map.isna().sum() == 0, "sigma_map still has NaNs after fillna"
    return sigma_map
