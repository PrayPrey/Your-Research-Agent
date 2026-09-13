import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import percentileofscore


def fit_coefficient(df: pd.DataFrame) -> float:
    """Fit mixedlm (OLS fallback if <2 groups), return metadata_score coef."""
    formula = "iqr ~ metadata_score + stability + log_popularity"
    if df["dataset_id"].nunique() < 2:
        result = smf.ols(formula, df).fit()
    else:
        result = smf.mixedlm(formula, df, groups=df["dataset_id"]).fit(reml=False, disp=False)
    return result.params["metadata_score"]


def run_permutation_test(df: pd.DataFrame, n_perms: int = 1000, seed: int = 42) -> dict:
    """Shuffle metadata_score n_perms times, refit, return stats dict."""
    rng = np.random.default_rng(seed)
    true_coef = fit_coefficient(df)

    perm_coefs = np.zeros(n_perms)
    for i in range(n_perms):
        df_p = df.copy()
        df_p["metadata_score"] = rng.permutation(df_p["metadata_score"].values)
        perm_coefs[i] = fit_coefficient(df_p)

    p_value = np.mean(np.abs(perm_coefs) >= np.abs(true_coef))
    percentile_rank = percentileofscore(perm_coefs, true_coef, kind="strict")
    effect_ratio = np.percentile(np.abs(perm_coefs), 95) / np.abs(true_coef) if true_coef != 0 else float("inf")

    return {
        "true_coef": float(true_coef),
        "perm_coefs": perm_coefs,
        "p_value": float(p_value),
        "percentile_rank": float(percentile_rank),
        "effect_ratio": float(effect_ratio),
    }
