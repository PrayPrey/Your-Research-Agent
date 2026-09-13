import pandas as pd
from scipy.stats import pointbiserialr
import pingouin as pg
from config import CONFIG

def point_biserial(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    r, p = pointbiserialr(df["passed"], df[metric])
    return float(r), float(p)

def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]:
    result = pg.partial_corr(data=df, x=metric, y="passed", covar="loc", method="pearson")
    return float(result["r"].iloc[0]), float(result["p_val"].iloc[0])

def compute_all_correlations(
    df: pd.DataFrame,
    metrics: list[str] = ["pylint_score", "mypy_errors", "radon_cc"],
) -> dict[str, dict[str, float]]:
    results = {}
    for m in metrics:
        r_raw, p_raw = point_biserial(df, m)
        r_partial, p_partial = partial_corr_loc(df, m)
        results[m] = {"r_raw": r_raw, "p_raw": p_raw, "r_partial": r_partial, "p_partial": p_partial}
    return results

def determine_pass(
    results: dict[str, dict[str, float]],
    threshold: float = CONFIG.corr_threshold,
    alpha: float = CONFIG.alpha,
) -> tuple[bool, str, float, float]:
    best_metric = max(results.keys(), key=lambda m: abs(results[m]["r_partial"]))
    best_r = results[best_metric]["r_partial"]
    best_p = results[best_metric]["p_partial"]
    passed = abs(best_r) >= threshold and best_p < alpha
    return passed, best_metric, best_r, best_p
