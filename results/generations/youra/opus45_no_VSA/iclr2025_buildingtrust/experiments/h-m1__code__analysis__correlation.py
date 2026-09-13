"""Correlation analysis between PC1 and BSI."""

import numpy as np
import pandas as pd
from scipy import stats


def fisher_z_ci(rho: float, n: int, alpha: float = 0.05) -> tuple:
    """
    Compute 95% CI for Pearson rho via Fisher z-transform.

    Returns:
        (ci_lower, ci_upper)
    """
    if n <= 3:
        raise ValueError(f"Sample size {n} too small for Fisher z CI (need n > 3)")

    rho_clipped = np.clip(rho, -0.9999, 0.9999)
    z = np.arctanh(rho_clipped)
    se = 1.0 / np.sqrt(n - 3)
    z_crit = stats.norm.ppf(1 - alpha / 2)

    ci_lower = np.tanh(z - z_crit * se)
    ci_upper = np.tanh(z + z_crit * se)

    return float(ci_lower), float(ci_upper)


def merge_pc1_bsi(pc1_df: pd.DataFrame, bsi_df: pd.DataFrame) -> pd.DataFrame:
    """Inner join PC1 and BSI dataframes on model_name."""
    merged = pd.merge(
        pc1_df, bsi_df,
        on="model_name",
        how="inner"
    )
    merged = merged.dropna(subset=["pc1_score", "bsi_score"])
    return merged


def run_correlation_analysis(
    pc1_scores: np.ndarray,
    bsi_scores: np.ndarray,
    min_samples: int = 30
) -> dict:
    """
    Compute Pearson correlation with CI and p-value.

    Args:
        pc1_scores: (M,) PC1 scores
        bsi_scores: (M,) BSI scores
        min_samples: Minimum sample size required

    Returns:
        dict with rho, p_value, ci_lower, ci_upper, n
    """
    mask = np.isfinite(pc1_scores) & np.isfinite(bsi_scores)
    pc1_clean = pc1_scores[mask]
    bsi_clean = bsi_scores[mask]

    n = len(pc1_clean)

    if n < min_samples:
        raise ValueError(f"Sample size {n} < {min_samples} required")

    rho, p_value = stats.pearsonr(pc1_clean, bsi_clean)
    ci_lower, ci_upper = fisher_z_ci(rho, n)

    return {
        "rho": float(rho),
        "p_value": float(p_value),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "n": int(n)
    }


def verify_bsi_mechanism(pc1_scores: np.ndarray, bsi_scores: np.ndarray, min_samples: int = 30) -> tuple:
    """Pre-flight verification checks."""
    if len(pc1_scores) < min_samples:
        return False, f"Insufficient samples: {len(pc1_scores)} < {min_samples}"
    if np.std(pc1_scores) < 1e-6:
        return False, "No variance in PC1 scores"
    if np.std(bsi_scores) < 1e-6:
        return False, "No variance in BSI scores"
    if np.any(~np.isfinite(pc1_scores)) or np.any(~np.isfinite(bsi_scores)):
        return False, "NaN or Inf values detected"
    return True, "OK"
