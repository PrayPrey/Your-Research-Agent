"""H-M4 Correlation Analyzer: Spearman correlation with CI and outlier detection."""
import numpy as np
from scipy.stats import spearmanr
from typing import Dict, List, Tuple, Any

from config import H_M4_Config


def compute_spearman(hedging_counts: List[int], confidence_scores: List[float]) -> Dict[str, float]:
    """Compute Spearman rank correlation.

    Returns:
        Dict with spearman_r, p_value, n_samples.
    """
    r, p = spearmanr(hedging_counts, confidence_scores)
    return {
        'spearman_r': float(r),
        'p_value': float(p),
        'n_samples': len(hedging_counts)
    }


def compute_confidence_interval(
    hedging_counts: List[int],
    confidence_scores: List[float],
    n_boot: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> Tuple[float, float]:
    """Compute bootstrap 95% CI for Spearman r.

    Returns:
        (ci_low, ci_high) tuple.
    """
    rng = np.random.default_rng(seed)
    x = np.array(hedging_counts)
    y = np.array(confidence_scores)
    n = len(x)

    rs = []
    for _ in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        r, _ = spearmanr(x[idx], y[idx])
        if not np.isnan(r):
            rs.append(r)

    if len(rs) == 0:
        return (0.0, 0.0)

    ci_low = np.percentile(rs, 100 * alpha / 2)
    ci_high = np.percentile(rs, 100 * (1 - alpha / 2))
    return (float(ci_low), float(ci_high))


def detect_outliers(
    hedging_counts: List[int],
    confidence_scores: List[float]
) -> Dict[str, Any]:
    """IQR-based outlier detection on confidence scores.

    Returns:
        Dict with outlier_count, outlier_indices, bounds.
    """
    y = np.array(confidence_scores)
    q1 = np.percentile(y, 25)
    q3 = np.percentile(y, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier_mask = (y < lower) | (y > upper)
    outlier_indices = np.where(outlier_mask)[0].tolist()

    return {
        'outlier_count': len(outlier_indices),
        'outlier_indices': outlier_indices,
        'bounds': {'lower': float(lower), 'upper': float(upper)}
    }


def compute_gate_metrics(
    stats: Dict[str, float],
    ci: Tuple[float, float],
    n: int,
    config: H_M4_Config
) -> Dict[str, Any]:
    """Combine stats into gate pass/fail dict.

    Args:
        stats: Dict from compute_spearman
        ci: Confidence interval tuple
        n: Sample count
        config: H_M4_Config with thresholds

    Returns:
        Dict with gate_1_pass, gate_2_pass, gate_3_pass, all_gates_pass.
    """
    r = stats['spearman_r']
    p = stats['p_value']

    gate_1_pass = r < config.gate_r_threshold
    gate_2_pass = p < config.gate_p_threshold
    gate_3_pass = n >= config.min_samples

    return {
        'spearman_r': r,
        'p_value': p,
        'n_samples': n,
        'confidence_interval': list(ci),
        'gate_1_r_pass': gate_1_pass,
        'gate_1_threshold': config.gate_r_threshold,
        'gate_2_p_pass': gate_2_pass,
        'gate_2_threshold': config.gate_p_threshold,
        'gate_3_n_pass': gate_3_pass,
        'gate_3_threshold': config.min_samples,
        'all_gates_pass': gate_1_pass and gate_2_pass and gate_3_pass
    }
