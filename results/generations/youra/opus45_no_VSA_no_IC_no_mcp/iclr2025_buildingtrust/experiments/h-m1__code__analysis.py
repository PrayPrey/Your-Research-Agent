"""Statistical analysis for H-M1: ECE correlations and moderation test."""

import numpy as np
from scipy.stats import pearsonr, norm


def residualize(v: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Remove linear effect of z from v."""
    coef = np.polyfit(z, v, deg=1)
    fitted = np.polyval(coef, z)
    return v - fitted


def partial_corr(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> tuple:
    """Partial correlation between x and y controlling for z."""
    rx = residualize(x, z)
    ry = residualize(y, z)
    r, p = pearsonr(rx, ry)
    return float(r), float(p)


def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> tuple:
    """
    Fisher's z-test to compare two correlation coefficients.
    Returns (z_statistic, p_value_two_tailed).
    """
    r1 = np.clip(r1, -0.999, 0.999)
    r2 = np.clip(r2, -0.999, 0.999)

    z1 = 0.5 * np.log((1 + r1) / (1 - r1))
    z2 = 0.5 * np.log((1 + r2) / (1 - r2))

    se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
    z_stat = (z1 - z2) / se
    p_value = 2 * (1 - norm.cdf(abs(z_stat)))

    return float(z_stat), float(p_value)


def correlate_ece_with_metrics(
    ece_scores: np.ndarray,
    truthfulqa_scores: np.ndarray,
    advglue_scores: np.ndarray,
    log_params: np.ndarray,
) -> dict:
    """
    Test H-M1: ECE should negatively correlate with both metrics.
    Gate conditions: r < -0.2 and p < 0.10 for both.
    """
    r_tqa, p_tqa = partial_corr(ece_scores, truthfulqa_scores, log_params)
    r_adv, p_adv = partial_corr(ece_scores, advglue_scores, log_params)

    from config import THRESHOLDS
    r_thresh = THRESHOLDS["ece_correlation_r"]
    p_thresh = THRESHOLDS["ece_correlation_p"]

    return {
        "ece_vs_truthfulqa": {"r": r_tqa, "p": p_tqa, "passes": r_tqa < r_thresh and p_tqa < p_thresh},
        "ece_vs_advglue": {"r": r_adv, "p": p_adv, "passes": r_adv < r_thresh and p_adv < p_thresh},
        "gate_passed": (r_tqa < r_thresh and p_tqa < p_thresh) and (r_adv < r_thresh and p_adv < p_thresh),
    }


def tertile_moderation_test(
    ece_scores: np.ndarray,
    truthfulqa_scores: np.ndarray,
    advglue_scores: np.ndarray,
) -> dict:
    """
    Test moderation: low-ECE group should show stronger
    TruthfulQA-AdvGLUE correlation than high-ECE group.
    Success: Fisher z-test p < 0.05, low_r > high_r.
    """
    n = len(ece_scores)
    sorted_idx = np.argsort(ece_scores)
    tertile_size = n // 3

    low_idx = sorted_idx[:tertile_size]
    high_idx = sorted_idx[-tertile_size:]

    r_low, _ = pearsonr(truthfulqa_scores[low_idx], advglue_scores[low_idx])
    r_high, _ = pearsonr(truthfulqa_scores[high_idx], advglue_scores[high_idx])

    z_stat, p_value = fisher_z_test(r_low, len(low_idx), r_high, len(high_idx))

    from config import THRESHOLDS
    fisher_p_thresh = THRESHOLDS["fisher_p"]

    return {
        "low_ece_correlation": float(r_low),
        "high_ece_correlation": float(r_high),
        "difference": float(r_low - r_high),
        "fisher_z": float(z_stat),
        "fisher_p": float(p_value),
        "moderation_detected": bool(r_low > r_high and p_value < fisher_p_thresh),
        "n_per_tertile": tertile_size,
    }
