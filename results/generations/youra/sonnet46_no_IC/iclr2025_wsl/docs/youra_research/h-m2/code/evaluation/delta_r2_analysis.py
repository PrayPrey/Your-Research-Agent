"""ΔR² statistics for H-M2 ablation."""
import numpy as np
from scipy import stats
from math import sqrt


def compute_delta_r2_stats(r2_scale: list, r2_perm: list) -> dict:
    """ΔR² statistics over N seeds."""
    delta = np.array(r2_scale) - np.array(r2_perm)
    n = len(delta)
    mean = float(np.mean(delta))
    std = float(np.std(delta, ddof=1)) if n > 1 else 0.0
    ci_half = 1.96 * std / sqrt(n) if n > 0 else 0.0
    if n > 1:
        t_stat, p_value = stats.ttest_1samp(delta, popmean=0)
    else:
        t_stat, p_value = float('nan'), float('nan')
    gate = 'PASS' if mean >= 0.05 else 'DOCUMENT'
    return {
        'delta_r2': delta.tolist(),
        'mean': mean,
        'std': std,
        'ci_low': mean - ci_half,
        'ci_high': mean + ci_half,
        't_stat': float(t_stat),
        'p_value': float(p_value),
        'gate': gate,
    }


def evaluate_should_work_gate(delta_r2_mean: float, gate_threshold: float = 0.05) -> str:
    return 'PASS' if delta_r2_mean >= gate_threshold else 'DOCUMENT'
