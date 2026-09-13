from __future__ import annotations

import numpy as np
import pandas as pd
import pingouin as pg
from scipy.stats import spearmanr, norm

from config import (
    PRIMARY_THRESHOLD, INTERNAL_THRESHOLD,
    DISCRIMINANT_THRESHOLD, DECODING_INVARIANCE_THRESHOLD,
)


def _bca_bootstrap_spearman(
    df: pd.DataFrame,
    x: str,
    y: str,
    n_boot: int,
    seed: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """BCa CI for unconditional spearmanr. Returns (ci_lo, ci_hi)."""
    rho_obs = float(spearmanr(df[x], df[y]).statistic)

    rng = np.random.default_rng(seed)
    boot_rhos = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(df), size=len(df))
        df_r = df.iloc[idx].reset_index(drop=True)
        try:
            boot_rhos.append(float(spearmanr(df_r[x], df_r[y]).statistic))
        except Exception:
            boot_rhos.append(np.nan)

    boot_arr = np.array(boot_rhos)
    boot_arr = boot_arr[~np.isnan(boot_arr)]

    z0 = norm.ppf(np.clip(np.mean(boot_arr < rho_obs), 1e-10, 1 - 1e-10))

    jack_rhos = []
    for i in range(len(df)):
        df_j = df.drop(index=df.index[i]).reset_index(drop=True)
        try:
            jack_rhos.append(float(spearmanr(df_j[x], df_j[y]).statistic))
        except Exception:
            jack_rhos.append(np.nan)

    jack_arr = np.array(jack_rhos)
    jack_mean = np.nanmean(jack_arr)
    diff = jack_mean - jack_arr
    denom = 6.0 * np.nansum(diff ** 2) ** 1.5
    a = np.nansum(diff ** 3) / denom if denom != 0 else 0.0

    z_lo = norm.ppf(alpha / 2)
    z_hi = norm.ppf(1 - alpha / 2)

    def _adj(z_val: float) -> float:
        inner = z0 + z_val
        return float(norm.cdf(z0 + inner / (1.0 - a * inner)))

    p_lo = np.clip(_adj(z_lo), 0.0, 1.0)
    p_hi = np.clip(_adj(z_hi), 0.0, 1.0)

    ci_lo = float(np.percentile(boot_arr, 100 * p_lo))
    ci_hi = float(np.percentile(boot_arr, 100 * p_hi))
    return ci_lo, ci_hi


def _bca_bootstrap_partial(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """BCa CI for pg.partial_corr Spearman. Returns (ci_lo, ci_hi)."""
    def _stat(d: pd.DataFrame) -> float:
        res = pg.partial_corr(data=d, x=x, y=y, covar=covar, method="spearman")
        return float(res["r"].values[0])

    rho_obs = _stat(df)

    rng = np.random.default_rng(seed)
    boot_rhos = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(df), size=len(df))
        df_r = df.iloc[idx].reset_index(drop=True)
        try:
            boot_rhos.append(_stat(df_r))
        except Exception:
            boot_rhos.append(np.nan)

    boot_arr = np.array(boot_rhos)
    boot_arr = boot_arr[~np.isnan(boot_arr)]

    z0 = norm.ppf(np.clip(np.mean(boot_arr < rho_obs), 1e-10, 1 - 1e-10))

    jack_rhos = []
    for i in range(len(df)):
        df_j = df.drop(index=df.index[i]).reset_index(drop=True)
        try:
            jack_rhos.append(_stat(df_j))
        except Exception:
            jack_rhos.append(np.nan)

    jack_arr = np.array(jack_rhos)
    jack_mean = np.nanmean(jack_arr)
    diff = jack_mean - jack_arr
    denom = 6.0 * np.nansum(diff ** 2) ** 1.5
    a = np.nansum(diff ** 3) / denom if denom != 0 else 0.0

    z_lo = norm.ppf(alpha / 2)
    z_hi = norm.ppf(1 - alpha / 2)

    def _adj(z_val: float) -> float:
        inner = z0 + z_val
        return float(norm.cdf(z0 + inner / (1.0 - a * inner)))

    p_lo = np.clip(_adj(z_lo), 0.0, 1.0)
    p_hi = np.clip(_adj(z_hi), 0.0, 1.0)

    ci_lo = float(np.percentile(boot_arr, 100 * p_lo))
    ci_hi = float(np.percentile(boot_arr, 100 * p_hi))
    return ci_lo, ci_hi


def compute_internal_consistency(
    df: pd.DataFrame,
    x: str,
    y: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Spearman rho(ECE, Brier) + BCa CI.
    Returns: {rho, pval, bca_ci_low, bca_ci_high, passes_threshold}
    """
    rho, pval = spearmanr(df[x], df[y])
    ci_lo, ci_hi = _bca_bootstrap_spearman(df, x, y, n_boot, seed)
    return {
        "rho": float(rho),
        "pval": float(pval),
        "bca_ci_low": ci_lo,
        "bca_ci_high": ci_hi,
        "passes_threshold": float(rho) >= INTERNAL_THRESHOLD,
    }


def compute_partial_corr_bca(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Primary gate: partial rho(ECE, TruthfulQA_pct | MMLU_acc) with BCa CI.
    Returns: {rho_partial, pval, bca_ci_low, bca_ci_high, ci_excludes_zero, passes_threshold}
    """
    res = pg.partial_corr(data=df, x=x, y=y, covar=covar, method="spearman")
    rho_partial = float(res["r"].values[0])
    pval_col = "p-val" if "p-val" in res.columns else "p_val"
    pval = float(res[pval_col].values[0]) if pval_col in res.columns else float("nan")

    ci_lo, ci_hi = _bca_bootstrap_partial(df, x, y, covar, n_boot, seed)
    ci_excludes_zero = bool(ci_lo > 0 or ci_hi < 0)
    passes = bool(abs(rho_partial) >= PRIMARY_THRESHOLD and ci_excludes_zero)

    return {
        "rho_partial": rho_partial,
        "pval": pval,
        "bca_ci_low": ci_lo,
        "bca_ci_high": ci_hi,
        "ci_excludes_zero": ci_excludes_zero,
        "passes_threshold": passes,
    }


def compute_confound_magnitude(raw_rho: float, partial_rho: float) -> dict:
    """Confound decomposition.
    Returns: {raw_rho, partial_rho, survival_fraction, confound_fraction, interpretation}
    """
    if abs(raw_rho) < 1e-9:
        survival = float("nan")
        confound = float("nan")
        interpretation = "raw_rho near zero — confound magnitude undefined"
    else:
        survival = abs(partial_rho) / abs(raw_rho)
        confound = 1.0 - survival
        if survival >= 0.50:
            interpretation = "MMLU explains <50% of raw correlation (capability-independent link confirmed)"
        else:
            interpretation = "MMLU explains >=50% of raw correlation (potential capability confound)"

    return {
        "raw_rho": raw_rho,
        "partial_rho": partial_rho,
        "survival_fraction": survival,
        "confound_fraction": confound,
        "interpretation": interpretation,
    }


def compute_discriminant_validity(
    df: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> dict:
    """partial rho(ECE, HumanEval | MMLU). passes = abs(rho) < DISCRIMINANT_THRESHOLD.
    Returns: {rho_partial, bca_ci_low, bca_ci_high, passes_threshold}
    """
    res = pg.partial_corr(data=df, x=x, y=y, covar=covar, method="spearman")
    rho_partial = float(res["r"].values[0])
    ci_lo, ci_hi = _bca_bootstrap_partial(df, x, y, covar, n_boot, seed)

    return {
        "rho_partial": rho_partial,
        "bca_ci_low": ci_lo,
        "bca_ci_high": ci_hi,
        "passes_threshold": bool(abs(rho_partial) < DISCRIMINANT_THRESHOLD),
    }


def compute_decoding_invariance(
    df_greedy: pd.DataFrame,
    df_t07: pd.DataFrame,
    x: str,
    y: str,
    covar: str,
    n_boot: int,
    seed: int,
) -> dict:
    """Repeat primary partial corr on T=0.7. skipped=True if df_t07 empty.
    Returns: {rho_greedy, rho_t07, delta_rho, passes_threshold, skipped}
    """
    if df_t07 is None or len(df_t07) == 0:
        return {
            "rho_greedy": float("nan"),
            "rho_t07": float("nan"),
            "delta_rho": float("nan"),
            "passes_threshold": False,
            "skipped": True,
        }

    res_g = compute_partial_corr_bca(df_greedy, x, y, covar, n_boot, seed)
    res_t = compute_partial_corr_bca(df_t07, x, y, covar, n_boot, seed + 1)

    rho_g = res_g["rho_partial"]
    rho_t = res_t["rho_partial"]
    passes = bool(abs(rho_t) >= DECODING_INVARIANCE_THRESHOLD)

    return {
        "rho_greedy": rho_g,
        "rho_t07": rho_t,
        "delta_rho": rho_t - rho_g,
        "passes_threshold": passes,
        "skipped": False,
    }


def evaluate_gate(partial_result: dict, threshold: float) -> bool:
    """Returns True iff abs(rho_partial) >= threshold AND ci_excludes_zero."""
    return bool(
        abs(partial_result["rho_partial"]) >= threshold
        and partial_result["ci_excludes_zero"]
    )
