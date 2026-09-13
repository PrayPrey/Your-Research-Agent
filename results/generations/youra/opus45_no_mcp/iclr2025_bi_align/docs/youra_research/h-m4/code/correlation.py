"""Correlation analysis for H-M4."""

import numpy as np
from scipy.stats import pointbiserialr, pearsonr
from sklearn.linear_model import LinearRegression

from config import H_M4_Config

cfg = H_M4_Config()


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Pooled-std standardized mean difference."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    pooled_std = np.sqrt(
        ((n1 - 1) * np.std(group1, ddof=1)**2 + (n2 - 1) * np.std(group2, ddof=1)**2)
        / (n1 + n2 - 2)
    )
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


def compute_partial_correlation(x: np.ndarray, y: np.ndarray, confounds: np.ndarray) -> tuple:
    """Residualize x, y on confounds via linear regression, then pearsonr."""
    x_resid = x - LinearRegression().fit(confounds, x).predict(confounds)
    y_resid = y - LinearRegression().fit(confounds, y).predict(confounds)
    return pearsonr(x_resid, y_resid)


def compute_correlations(cluster_labels: np.ndarray, scores: np.ndarray, confounds: np.ndarray) -> dict:
    """Compute all correlation metrics."""
    r_pb, p_pb = pointbiserialr(cluster_labels, scores)

    scores_inv = scores[cluster_labels == 1]
    scores_norm = scores[cluster_labels == 0]
    d = compute_cohens_d(scores_inv, scores_norm)

    partial_r, partial_p = compute_partial_correlation(
        cluster_labels.astype(float), scores.astype(float), confounds
    )

    return {
        "point_biserial_r": float(r_pb),
        "point_biserial_p": float(p_pb),
        "cohens_d": float(d),
        "partial_r": float(partial_r),
        "partial_p": float(partial_p)
    }


def check_gate(metrics: dict) -> bool:
    """Gate condition: (r > 0.4) OR (d > 0.3 AND partial_r > 0.3)."""
    r = abs(metrics["point_biserial_r"])
    d = abs(metrics["cohens_d"])
    pr = abs(metrics["partial_r"])
    return (r > cfg.r_threshold) or (d > cfg.d_threshold and pr > cfg.partial_r_threshold)
