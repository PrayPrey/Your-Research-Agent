"""Correlation analysis for H-M2 experiment."""

import numpy as np
from scipy import stats
from config import GATE_R_THRESHOLD, GATE_P_THRESHOLD, MIN_SAMPLE_SIZE


def compute_correlation(human_scores: list, ai_scores: list) -> dict:
    """Compute Pearson and Spearman correlation with statistics."""
    human_arr = np.array(human_scores)
    ai_arr = np.array(ai_scores)

    n = len(human_arr)

    r, p_value = stats.pearsonr(human_arr, ai_arr)
    rho, rho_p = stats.spearmanr(human_arr, ai_arr)

    return {
        'n': n,
        'pearson_r': float(r),
        'pearson_p': float(p_value),
        'spearman_rho': float(rho),
        'spearman_p': float(rho_p),
        'human_mean': float(np.mean(human_arr)),
        'human_sd': float(np.std(human_arr)),
        'ai_mean': float(np.mean(ai_arr)),
        'ai_sd': float(np.std(ai_arr)),
    }


def check_gate(results: dict, r_thresh: float = GATE_R_THRESHOLD, p_thresh: float = GATE_P_THRESHOLD) -> dict:
    """Check if correlation passes SHOULD_WORK gate."""
    r = results['pearson_r']
    p = results['pearson_p']
    n = results['n']

    passes = abs(r) > r_thresh and p < p_thresh and n >= MIN_SAMPLE_SIZE

    return {
        'gate_pass': passes,
        'r_threshold': r_thresh,
        'p_threshold': p_thresh,
        'n_threshold': MIN_SAMPLE_SIZE,
        'r_margin': abs(r) - r_thresh,
        'verdict': 'PASS' if passes else 'FAIL'
    }
