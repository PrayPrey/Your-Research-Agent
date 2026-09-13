import numpy as np
import pandas as pd
import pingouin as pg
from config import CONFIG

def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    result = pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
    return float(result["r"].iloc[0]), float(result["p_val"].iloc[0])

def compute_per_model_correlations(
    df: pd.DataFrame, metric: str = "pylint_score", models: list[str] = None
) -> dict[str, tuple[float, float]]:
    if models is None:
        models = df["model_id"].unique().tolist()
    result = {}
    for m in models:
        sub = df[df["model_id"] == m]
        if len(sub) < 30:
            print(f"Warning: {m} has only {len(sub)} samples, skipping")
            continue
        r, p = partial_corr_loc(sub, metric)
        result[m] = (r, p)
    return result

def cross_model_variance(correlations: dict[str, tuple[float, float]]) -> tuple[float, float, float]:
    rs = [r for r, p in correlations.values()]
    return float(np.mean(rs)), float(np.std(rs)), float(np.min(rs))

def determine_gate_pass(
    mean_r: float, std_r: float, min_r: float,
    variance_threshold: float = CONFIG.variance_threshold,
    mean_r_threshold: float = CONFIG.mean_r_threshold,
    min_r_threshold: float = CONFIG.min_r_threshold,
) -> bool:
    return std_r < variance_threshold and mean_r > mean_r_threshold and min_r > min_r_threshold
