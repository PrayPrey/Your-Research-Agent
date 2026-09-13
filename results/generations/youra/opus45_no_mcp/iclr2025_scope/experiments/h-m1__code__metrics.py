"""Metrics for H-M1: KL divergence and gate conditions"""

import numpy as np
from scipy.stats import entropy
from config import GATE_THRESHOLDS, LANDSCAPE_CONFIG


def compute_kl_divergence(eig_pre, eig_post, num_bins=None, eps=None):
    """
    KL divergence between pre/post conversion eigenvalue distributions.
    Bins eigenvalues on shared range, computes D_KL(P_pre || P_post).
    """
    if num_bins is None:
        num_bins = LANDSCAPE_CONFIG["num_bins"]
    if eps is None:
        eps = LANDSCAPE_CONFIG["kl_eps"]

    eig_pre = np.array(eig_pre)
    eig_post = np.array(eig_post)

    all_eig = np.concatenate([eig_pre, eig_post])
    bins = np.linspace(min(all_eig), max(all_eig) + eps, num_bins + 1)

    hist_pre, _ = np.histogram(eig_pre, bins=bins, density=True)
    hist_post, _ = np.histogram(eig_post, bins=bins, density=True)

    hist_pre = hist_pre + eps
    hist_post = hist_post + eps

    hist_pre = hist_pre / hist_pre.sum()
    hist_post = hist_post / hist_post.sum()

    return entropy(hist_pre, hist_post)


def spectral_norm_ratio(eig_pre, eig_post):
    """Ratio of maximum eigenvalues: max(post) / max(pre)."""
    if isinstance(eig_pre, dict):
        max_pre = eig_pre["spectral_norm"]
        max_post = eig_post["spectral_norm"]
    else:
        max_pre = max(eig_pre) if eig_pre else 1.0
        max_post = max(eig_post) if eig_post else 1.0
    return max_post / (max_pre + 1e-10)


def trace_ratio(eig_pre, eig_post):
    """Ratio of Hessian traces: trace(post) / trace(pre)."""
    if isinstance(eig_pre, dict):
        t_pre = eig_pre["trace"]
        t_post = eig_post["trace"]
    else:
        t_pre = sum(eig_pre) if eig_pre else 1.0
        t_post = sum(eig_post) if eig_post else 1.0
    return t_post / (t_pre + 1e-10)


def check_gate_conditions(sharpness_transformer, sharpness_mamba, kl_div):
    """
    Check MUST_WORK gate conditions.
    Primary: |sharpness_delta| / sharpness_transformer > 10%
    Secondary: kl_divergence > 0.1
    """
    sharpness_delta = abs(sharpness_mamba - sharpness_transformer)
    sharpness_delta_pct = sharpness_delta / (abs(sharpness_transformer) + 1e-10)

    primary_pass = sharpness_delta_pct > GATE_THRESHOLDS["sharpness_delta_pct_min"]
    secondary_pass = kl_div > GATE_THRESHOLDS["kl_divergence_min"]

    return {
        "primary_pass": primary_pass,
        "secondary_pass": secondary_pass,
        "gate_pass": primary_pass,
        "sharpness_transformer": sharpness_transformer,
        "sharpness_mamba": sharpness_mamba,
        "sharpness_delta": sharpness_delta,
        "sharpness_delta_pct": sharpness_delta_pct,
        "kl_divergence": kl_div,
    }
