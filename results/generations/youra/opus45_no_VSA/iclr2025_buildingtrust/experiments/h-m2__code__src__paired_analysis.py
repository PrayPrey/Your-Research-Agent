"""Paired statistical tests for BSI and PC1 differences."""
import numpy as np
from scipy import stats


def paired_deltas(base_vals: np.ndarray, instruct_vals: np.ndarray) -> np.ndarray:
    return instruct_vals - base_vals


def run_paired_ttest(base_vals: np.ndarray, instruct_vals: np.ndarray) -> dict:
    if len(base_vals) < 2:
        raise ValueError("Need at least 2 pairs for t-test")
    deltas = paired_deltas(base_vals, instruct_vals)
    t_stat, p_value = stats.ttest_rel(instruct_vals, base_vals)
    mean_delta = deltas.mean()
    std_delta = deltas.std(ddof=1)
    cohens_d = mean_delta / std_delta if std_delta > 0 else 0.0
    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "mean_delta": float(mean_delta),
        "cohens_d": float(cohens_d),
    }


def run_wilcoxon(base_vals: np.ndarray, instruct_vals: np.ndarray) -> dict:
    deltas = paired_deltas(base_vals, instruct_vals)
    stat, p_value = stats.wilcoxon(deltas, alternative="greater")
    return {"stat": float(stat), "p_value": float(p_value)}


def delta_correlation(delta_bsi: np.ndarray, delta_pc1: np.ndarray) -> dict:
    r, p_value = stats.pearsonr(delta_bsi, delta_pc1)
    return {"pearson_r": float(r), "p_value": float(p_value)}
