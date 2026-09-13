# Baseline comparison module for h-e1
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from config import N_PERMUTATIONS, RANDOM_SEED
from analysis import compute_quartile_effect


def null_baseline(df: pd.DataFrame, n_permutations: int = N_PERMUTATIONS) -> dict:
    """Permutation test: shuffle metadata scores to get null distribution."""
    np.random.seed(RANDOM_SEED)
    effects = []

    for _ in range(n_permutations):
        df_perm = df.copy()
        df_perm["metadata_score"] = np.random.permutation(df["metadata_score"].values)
        effect = compute_quartile_effect(df_perm)
        if effect["relative_reduction"] is not None:
            effects.append(effect["relative_reduction"])

    if len(effects) < 5:
        return {"null_mean": None, "null_std": None, "null_95_upper": None}

    return {
        "null_mean": float(np.mean(effects)),
        "null_std": float(np.std(effects)),
        "null_95_upper": float(np.percentile(effects, 95))
    }


def size_baseline(df: pd.DataFrame) -> tuple:
    """Use dataset size as predictor instead of metadata (alternative baseline)."""
    df = df.copy()
    df["algo_family"] = df["algo_family"].astype("category")

    if df["dataset_id"].nunique() < 2:
        model = smf.ols(
            "iqr ~ log_n_instances + stability + log_popularity + C(algo_family)",
            data=df
        )
    else:
        model = smf.mixedlm(
            "iqr ~ log_n_instances + stability + log_popularity + C(algo_family)",
            data=df,
            groups=df["dataset_id"]
        )

    result = model.fit(reml=False) if hasattr(model, "fit") else model.fit()

    coef = result.params.get("log_n_instances", 0.0)
    pval = result.pvalues.get("log_n_instances", 1.0)
    return float(coef), float(pval)
