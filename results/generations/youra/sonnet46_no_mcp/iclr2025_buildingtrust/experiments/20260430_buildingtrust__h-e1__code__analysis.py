from __future__ import annotations

import logging
from itertools import combinations

import numpy as np
import pandas as pd
import pingouin as pg
from factor_analyzer import FactorAnalyzer, calculate_kmo
from scipy.stats import norm
from sklearn.linear_model import LogisticRegressionCV
from sklearn.model_selection import LeaveOneOut, cross_val_score

from config import (
    COVARIATE,
    FA_METHOD,
    FA_ROTATION,
    GATE_PAIRS,
    GATE_THRESHOLD,
    INDICATORS,
    N_BOOTSTRAP,
    N_FACTORS,
)

logger = logging.getLogger(__name__)


def bca_bootstrap_ci(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int = N_BOOTSTRAP,
    alpha: float = 0.05,
) -> tuple[float, float]:
    res_obs = pg.partial_corr(data=df, x=x, y=y, covar=covar, method="spearman")
    rho_obs = float(res_obs["r"].values[0])

    # Use min(n_boot, 500) for PoC speed; full 10000 for production
    n_boot_actual = min(n_boot, 500)
    rng = np.random.default_rng(42)
    boot_rhos = []
    for _ in range(n_boot_actual):
        idx = rng.integers(0, len(df), size=len(df))
        df_r = df.iloc[idx].reset_index(drop=True)
        try:
            r = pg.partial_corr(data=df_r, x=x, y=y, covar=covar, method="spearman")["r"].values[0]
        except Exception:
            r = float("nan")
        boot_rhos.append(r)
    boot_rhos = np.array(boot_rhos)
    boot_rhos = boot_rhos[~np.isnan(boot_rhos)]

    z0_arg = np.mean(boot_rhos < rho_obs)
    z0_arg = np.clip(z0_arg, 1e-10, 1 - 1e-10)
    z0 = norm.ppf(z0_arg)

    jack_rhos = []
    for i in range(len(df)):
        df_j = df.drop(index=df.index[i]).reset_index(drop=True)
        try:
            r = pg.partial_corr(data=df_j, x=x, y=y, covar=covar, method="spearman")["r"].values[0]
        except Exception:
            r = float("nan")
        jack_rhos.append(r)
    jack_rhos = np.array(jack_rhos)
    jack_mean = np.nanmean(jack_rhos)
    diff = jack_mean - jack_rhos
    num = np.nansum(diff ** 3)
    den = 6.0 * np.nansum(diff ** 2) ** 1.5
    a = num / den if den != 0 else 0.0

    z_lo = norm.ppf(alpha / 2)
    z_hi = norm.ppf(1 - alpha / 2)

    def _adj(z_a):
        denom = 1 - a * (z0 + z_a)
        if abs(denom) < 1e-10:
            return 0.5
        return norm.cdf(z0 + (z0 + z_a) / denom)

    p_lo = _adj(z_lo)
    p_hi = _adj(z_hi)
    p_lo = np.clip(p_lo, 0.0, 1.0)
    p_hi = np.clip(p_hi, 0.0, 1.0)

    ci_lo = float(np.percentile(boot_rhos, 100 * p_lo))
    ci_hi = float(np.percentile(boot_rhos, 100 * p_hi))
    return ci_lo, ci_hi


def compute_partial_corr_matrix(
    df: pd.DataFrame,
    indicators: list[str] = INDICATORS,
    covar: str = COVARIATE,
) -> pd.DataFrame:
    rows = []
    for x, y in combinations(indicators, 2):
        try:
            res = pg.partial_corr(data=df, x=x, y=y, covar=covar, method="spearman")
            rho = float(res["r"].values[0])
            # pingouin uses 'p-val' in older versions, 'p_val' in newer
            p_val = float(res.get("p-val", res.get("p_val", pd.Series([float("nan")]))).values[0])
        except Exception as e:
            logger.warning(f"partial_corr({x},{y}) failed: {e}")
            rho, p_val = float("nan"), float("nan")

        try:
            ci_lo, ci_hi = bca_bootstrap_ci(df, x, y, covar)
        except Exception as e:
            logger.warning(f"bca_bootstrap_ci({x},{y}) failed: {e}")
            ci_lo, ci_hi = float("nan"), float("nan")

        rows.append({"x": x, "y": y, "rho": rho, "ci_low": ci_lo, "ci_high": ci_hi, "p_value": p_val})

    return pd.DataFrame(rows)


def run_factor_analysis(
    df: pd.DataFrame,
    indicators: list[str] = INDICATORS,
    n_factors: int = N_FACTORS,
) -> tuple[FactorAnalyzer, np.ndarray, float, float]:
    X = df[indicators].dropna()
    fa = FactorAnalyzer(n_factors=n_factors, method=FA_METHOD, rotation=FA_ROTATION)
    fa.fit(X)
    loadings = fa.loadings_  # shape [n_indicators, n_factors]
    var = fa.get_factor_variance()
    var_explained = float(var[1][0]) if len(var[1]) > 0 else float("nan")
    try:
        _, kmo_model = calculate_kmo(X)
        kmo = float(kmo_model)
    except Exception:
        kmo = float("nan")
    return fa, loadings, var_explained, kmo


def compute_tucker_congruence(loadings_a: np.ndarray, loadings_b: np.ndarray) -> float:
    a = loadings_a.flatten()
    b = loadings_b.flatten()
    num = float(np.dot(a, b))
    den = float(np.sqrt(np.dot(a, a) * np.dot(b, b)))
    if den == 0:
        return float("nan")
    return num / den


def run_loo_logistic(
    df: pd.DataFrame,
    features: list[str],
    target: str = "AdvGLUE_drop",
) -> dict:
    df_clean = df[features + [target, COVARIATE]].dropna()
    q75 = df_clean[target].quantile(0.75)
    y = (df_clean[target] >= q75).astype(int).values

    loo = LeaveOneOut()
    clf = LogisticRegressionCV(cv=5, max_iter=1000, random_state=42)

    X_full = df_clean[features].values
    try:
        scores_full = cross_val_score(clf, X_full, y, cv=loo, scoring="roc_auc")
        auc = float(np.mean(scores_full))
    except Exception as e:
        logger.warning(f"LOO full model failed: {e}")
        auc = float("nan")

    X_mmlu = df_clean[[COVARIATE]].values
    try:
        scores_mmlu = cross_val_score(clf, X_mmlu, y, cv=loo, scoring="roc_auc")
        auc_mmlu = float(np.mean(scores_mmlu))
    except Exception as e:
        logger.warning(f"LOO MMLU-only model failed: {e}")
        auc_mmlu = float("nan")

    return {"auc": auc, "auc_mmlu_only": auc_mmlu}


def evaluate_gates(
    corr_df: pd.DataFrame,
    gate_pairs: list[tuple] = GATE_PAIRS,
    threshold: float = GATE_THRESHOLD,
) -> dict:
    results = []
    for x, y in gate_pairs:
        row = corr_df[(corr_df["x"] == x) & (corr_df["y"] == y)]
        if row.empty:
            row = corr_df[(corr_df["x"] == y) & (corr_df["y"] == x)]
        if row.empty:
            results.append({"pair": (x, y), "rho": float("nan"), "ci": (float("nan"), float("nan")), "passes": False})
            continue
        rho = float(row["rho"].values[0])
        ci_lo = float(row["ci_low"].values[0])
        ci_hi = float(row["ci_high"].values[0])
        # Gate: |rho| >= threshold AND BCa CI excludes zero
        passes = (abs(rho) >= threshold) and (ci_lo > 0 or ci_hi < 0)
        results.append({"pair": (x, y), "rho": rho, "ci": (ci_lo, ci_hi), "passes": passes})

    overall_pass = all(r["passes"] for r in results)
    return {"PASS": overall_pass, "results": results}
