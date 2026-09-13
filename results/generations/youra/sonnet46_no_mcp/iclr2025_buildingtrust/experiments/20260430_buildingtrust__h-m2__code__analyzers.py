from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config


def _bca_bootstrap_partial(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """BCa CI for partial Spearman rho via pg.partial_corr. Returns (ci_lo, ci_hi)."""

    def _stat(d: pd.DataFrame) -> float:
        res = pg.partial_corr(data=d, x=x, y=y, covar=covar, method="spearman")
        return float(res["r"].values[0])

    rho_obs = _stat(df)
    n = len(df)
    rng = np.random.default_rng(seed)

    # Bootstrap distribution
    boot_stats = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        d_b = df.iloc[idx].reset_index(drop=True)
        try:
            boot_stats.append(_stat(d_b))
        except Exception:
            boot_stats.append(np.nan)

    arr = np.array(boot_stats)
    valid = arr[~np.isnan(arr)]
    if len(valid) == 0:
        return (float("nan"), float("nan"))

    # z0: bias correction
    z0 = norm.ppf(np.mean(valid < rho_obs))

    # Jackknife acceleration
    jack_stats = []
    for i in range(n):
        d_j = df.drop(index=df.index[i]).reset_index(drop=True)
        try:
            jack_stats.append(_stat(d_j))
        except Exception:
            jack_stats.append(np.nan)

    jack_arr = np.array(jack_stats)
    jack_valid = jack_arr[~np.isnan(jack_arr)]
    jack_mean = np.mean(jack_valid)
    num = np.sum((jack_mean - jack_valid) ** 3)
    den = 6.0 * (np.sum((jack_mean - jack_valid) ** 2) ** 1.5)
    a = num / den if den != 0 else 0.0

    z_lo = norm.ppf(alpha / 2)
    z_hi = norm.ppf(1 - alpha / 2)

    def _adj(z_val: float) -> float:
        inner = z0 + z_val
        return norm.cdf(z0 + inner / (1.0 - a * inner))

    p_lo = _adj(z_lo)
    p_hi = _adj(z_hi)
    ci_lo = float(np.percentile(valid, p_lo * 100))
    ci_hi = float(np.percentile(valid, p_hi * 100))
    return (ci_lo, ci_hi)


def compute_partial_rho_advglue(
    df: pd.DataFrame,
    n_boot: int,
    seed: int,
) -> dict:
    """Partial Spearman rho for AdvGLUE and ANLI with BCa CIs."""
    # AdvGLUE arm
    res_adv = pg.partial_corr(
        data=df, x=config.PARTIAL_X, y=config.PARTIAL_Y_ADV,
        covar=config.COVARIATE, method="spearman"
    )
    rho_adv = float(res_adv["r"].values[0])
    ci_lo_adv, ci_hi_adv = _bca_bootstrap_partial(
        df, config.PARTIAL_X, config.PARTIAL_Y_ADV, config.COVARIATE, n_boot, seed
    )
    ci_excl = (ci_lo_adv > 0 or ci_hi_adv < 0)
    passes = abs(rho_adv) >= config.PARTIAL_RHO_THRESHOLD and ci_excl

    # ANLI arm (seed+1 for independence)
    res_anli = pg.partial_corr(
        data=df, x=config.PARTIAL_X, y=config.PARTIAL_Y_ANLI,
        covar=config.COVARIATE, method="spearman"
    )
    rho_anli = float(res_anli["r"].values[0])
    ci_lo_anli, ci_hi_anli = _bca_bootstrap_partial(
        df, config.PARTIAL_X, config.PARTIAL_Y_ANLI, config.COVARIATE, n_boot, seed + 1
    )

    return {
        "rho_partial_advglue": rho_adv,
        "bca_ci_low": ci_lo_adv,
        "bca_ci_high": ci_hi_adv,
        "ci_excludes_zero": ci_excl,
        "passes_threshold": passes,
        "rho_partial_anli": rho_anli,
        "anli_bca_ci_low": ci_lo_anli,
        "anli_bca_ci_high": ci_hi_anli,
    }


def _run_loo_logistic(
    X: np.ndarray,
    y: np.ndarray,
    seed: int,
) -> np.ndarray:
    """LOO cross-validation with LogisticRegression. Returns y_proba of shape (N,)."""
    loo = LeaveOneOut()
    y_proba = np.zeros(len(y))
    for train_idx, test_idx in loo.split(X):
        X_tr, X_te = X[train_idx], X[test_idx]
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        X_te_s = scaler.transform(X_te)
        clf = LogisticRegression(
            C=config.LR_C, max_iter=config.LR_MAX_ITER, random_state=seed
        )
        clf.fit(X_tr_s, y[train_idx])
        y_proba[test_idx] = clf.predict_proba(X_te_s)[:, 1]
    return y_proba


def compute_loo_auc(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    seed: int,
) -> dict:
    """LOO-AUC for given feature set."""
    X = df[feature_cols].values
    y = df[target_col].values.astype(int)
    if len(np.unique(y)) < 2:
        raise ValueError(
            f"target_col '{target_col}' has fewer than 2 classes: {np.unique(y)}"
        )
    y_proba = _run_loo_logistic(X, y, seed)
    auc = roc_auc_score(y, y_proba)
    return {
        "auc": float(auc),
        "y_proba": y_proba,
        "y_true": y,
        "feature_cols": feature_cols,
    }


def compute_delta_auc_bootstrap(
    df: pd.DataFrame,
    composite_cols: list[str],
    baseline_cols: list[str],
    target_col: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Bootstrap CI for delta LOO-AUC (composite minus baseline)."""
    # Observed LOO-AUC (full data)
    comp_result = compute_loo_auc(df, composite_cols, target_col, seed)
    base_result = compute_loo_auc(df, baseline_cols, target_col, seed)
    auc_c = comp_result["auc"]
    auc_b = base_result["auc"]
    delta_obs = auc_c - auc_b

    # Percentile bootstrap for CI on delta
    rng = np.random.default_rng(seed)
    boot_deltas: list[float] = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(df), size=len(df))
        df_b = df.iloc[idx].reset_index(drop=True)
        y_b = df_b[target_col].values.astype(int)
        if len(np.unique(y_b)) < 2:
            boot_deltas.append(float("nan"))
            continue
        try:
            auc_bc = compute_loo_auc(df_b, composite_cols, target_col, seed)["auc"]
            auc_bb = compute_loo_auc(df_b, baseline_cols, target_col, seed)["auc"]
            boot_deltas.append(auc_bc - auc_bb)
        except Exception:
            boot_deltas.append(float("nan"))

    arr = np.array(boot_deltas)
    valid = arr[~np.isnan(arr)]
    if len(valid) < n_boot * 0.9:
        warnings.warn(
            f"Only {len(valid)}/{n_boot} valid bootstrap samples "
            f"({100*len(valid)/n_boot:.1f}%)"
        )
    ci_lo = float(np.percentile(valid, 2.5))
    ci_hi = float(np.percentile(valid, 97.5))

    passes_delta = (delta_obs >= config.DELTA_AUC_THRESHOLD) and (ci_lo > 0)
    passes_auc = auc_c >= config.AUC_THRESHOLD

    return {
        "auc_composite": auc_c,
        "auc_baseline": auc_b,
        "delta_auc": delta_obs,
        "delta_auc_ci": [ci_lo, ci_hi],
        "ci_excludes_zero": ci_lo > 0,
        "passes_delta_threshold": passes_delta,
        "passes_auc_threshold": passes_auc,
    }


def evaluate_gate(auc_result: dict, delta_result: dict) -> bool:
    """PASS iff auc_composite >= AUC_THRESHOLD AND delta_auc >= DELTA_AUC_THRESHOLD AND ci_lo > 0."""
    return (
        delta_result["passes_auc_threshold"]
        and delta_result["passes_delta_threshold"]
    )
