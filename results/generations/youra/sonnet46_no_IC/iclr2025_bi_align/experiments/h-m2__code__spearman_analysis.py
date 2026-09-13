import numpy as np
import pandas as pd
import pingouin
from scipy import stats

H_E1_R_PARTIAL: float = 0.9851


def spearman_residuals(win_resid: np.ndarray, lc_resid: np.ndarray) -> dict:
    """Returns: {rho: float, p_value: float}"""
    rho, p_value = stats.spearmanr(win_resid, lc_resid)
    return {'rho': float(rho), 'p_value': float(p_value)}


def bootstrap_spearman(
    win_resid: np.ndarray,
    lc_resid: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple:
    """Returns: (ci_lower, ci_upper, boot_rhos [n_bootstrap,])"""
    rng = np.random.default_rng(seed)
    n = len(win_resid)
    boot_rhos = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        boot_rhos[i] = stats.spearmanr(win_resid[idx], lc_resid[idx])[0]
    ci_lower = float(np.percentile(boot_rhos, 2.5))
    ci_upper = float(np.percentile(boot_rhos, 97.5))
    return ci_lower, ci_upper, boot_rhos


def fwl_consistency_check(rho: float, h_e1_r_partial: float = H_E1_R_PARTIAL) -> dict:
    """Returns: {fwl_delta: float, fwl_consistent: bool}"""
    fwl_delta = abs(rho - h_e1_r_partial)
    return {'fwl_delta': float(fwl_delta), 'fwl_consistent': bool(fwl_delta < 0.02)}


def pingouin_cross_validate(df: pd.DataFrame) -> dict:
    """Returns: {pingouin_r: float, pingouin_p: float}"""
    result = pingouin.partial_corr(
        data=df,
        x='win_rate',
        y='length_controlled_winrate',
        covar='avg_length',
        method='spearman',
    )
    return {
        'pingouin_r': float(result['r'].iloc[0]),
        'pingouin_p': float(result['p_val'].iloc[0]),
    }
