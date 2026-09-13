import numpy as np
import pandas as pd


def regress_out(y: np.ndarray, x: np.ndarray) -> tuple:
    """OLS-regress x out of y. Returns (residuals [N,], r_squared)."""
    X_mat = np.column_stack([np.ones(len(x)), x])
    coefs = np.linalg.lstsq(X_mat, y, rcond=None)[0]
    residuals = y - X_mat @ coefs
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return residuals, float(r_squared)


def compute_residuals(df: pd.DataFrame) -> dict:
    """
    Regress avg_length out of win_rate and length_controlled_winrate.
    Returns: {win_rate_resid, lc_resid, r2_win, r2_lc, n}
    """
    avg_len = df['avg_length'].values
    win_resid, r2_win = regress_out(df['win_rate'].values, avg_len)
    lc_resid, r2_lc = regress_out(df['length_controlled_winrate'].values, avg_len)
    print(f"R²(win_rate ~ avg_length) = {r2_win:.4f}")
    print(f"R²(lc_winrate ~ avg_length) = {r2_lc:.4f}")
    return {
        'win_rate_resid': win_resid,
        'lc_resid': lc_resid,
        'r2_win': r2_win,
        'r2_lc': r2_lc,
        'n': len(avg_len),
    }
