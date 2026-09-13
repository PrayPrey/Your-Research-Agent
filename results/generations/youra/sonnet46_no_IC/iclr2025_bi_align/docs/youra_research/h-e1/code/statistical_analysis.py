import math
import numpy as np
import pandas as pd
import pingouin
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


def compute_vif(df: pd.DataFrame) -> dict:
    X = df[['win_rate', 'avg_length']].copy()
    X_with_const = sm.add_constant(X)
    vif_win = variance_inflation_factor(X_with_const.values, 1)
    vif_len = variance_inflation_factor(X_with_const.values, 2)
    if math.isinf(vif_win) or math.isinf(vif_len):
        any_high = True
    else:
        any_high = any(v >= 5.0 for v in [vif_win, vif_len])
    return {'win_rate': float(vif_win), 'avg_length': float(vif_len), 'any_high_vif': any_high}


def spearman_partial_corr(df: pd.DataFrame) -> dict:
    result = pingouin.partial_corr(
        data=df,
        x='win_rate',
        y='length_controlled_winrate',
        covar='avg_length',
        method='spearman',
        alternative='greater'
    )
    r = float(result['r'].iloc[0])
    p = float(result['p_val'].iloc[0])
    ci = result['CI95'].iloc[0]
    n = int(result['n'].iloc[0])
    return {'r_partial': r, 'p_val': p, 'ci95': list(ci), 'n': n}


def bootstrap_partial_corr(df: pd.DataFrame, n_bootstrap: int = 1000, random_state: int = 42):
    rng = np.random.default_rng(random_state)
    boot_rs = []
    n = len(df)
    skipped = 0
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        sample = df.iloc[idx].reset_index(drop=True)
        result = pingouin.partial_corr(
            data=sample,
            x='win_rate',
            y='length_controlled_winrate',
            covar='avg_length',
            method='spearman'
        )
        r = float(result['r'].iloc[0])
        if not np.isnan(r):
            boot_rs.append(r)
        else:
            skipped += 1
    if skipped > 0:
        print(f"Bootstrap: skipped {skipped} degenerate resamples")
    arr = np.array(boot_rs)
    ci_lower = float(np.percentile(arr, 2.5))
    ci_upper = float(np.percentile(arr, 97.5))
    return ci_lower, ci_upper, boot_rs
