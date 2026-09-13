"""Correlation analysis for H-M3"""

from scipy.stats import spearmanr
import numpy as np

from config import GATE_THRESHOLD, RANK_CONFIG
from rank import compute_model_effective_rank


def compute_spearman(sharpness_vals, rank_vals):
    """
    Compute Spearman correlation between sharpness and effective rank.
    Returns {'rho', 'p_value', 'gate_pass': rho > GATE_THRESHOLD}
    """
    if len(sharpness_vals) < 2:
        return {
            "rho": 0.0,
            "p_value": 1.0,
            "gate_pass": False,
        }

    rho, p_value = spearmanr(sharpness_vals, rank_vals)

    if np.isnan(rho):
        rho = 0.0

    return {
        "rho": float(rho),
        "p_value": float(p_value),
        "gate_pass": rho > GATE_THRESHOLD,
    }


def compute_gap_correlation(sharpness_vals, gap_vals):
    """
    Secondary Spearman correlation between sharpness and generalization gap.
    Returns {'rho', 'p_value'}
    """
    if len(sharpness_vals) < 2:
        return {"rho": 0.0, "p_value": 1.0}

    rho, p_value = spearmanr(sharpness_vals, gap_vals)

    if np.isnan(rho):
        rho = 0.0

    return {
        "rho": float(rho),
        "p_value": float(p_value),
    }


def run_threshold_sensitivity(models, sharpness_vals, thresholds=None):
    """
    A-1 ablation: recompute effective_rank + rho at each threshold.
    Returns {threshold: {'rho', 'p_value', 'ranks': dict}}
    """
    if thresholds is None:
        thresholds = RANK_CONFIG["thresholds"]

    tasks = list(models.keys())
    sharp_list = [sharpness_vals[t] for t in tasks]

    results = {}

    for threshold in thresholds:
        rank_list = []
        ranks = {}

        for t in tasks:
            rank_result = compute_model_effective_rank(models[t], threshold)
            rank_list.append(rank_result["effective_rank"])
            ranks[t] = rank_result["effective_rank"]

        corr = compute_spearman(sharp_list, rank_list)
        results[threshold] = {
            "rho": corr["rho"],
            "p_value": corr["p_value"],
            "ranks": ranks,
        }

    return results


def run_seed_sensitivity(seeds, run_fn):
    """
    A-2 ablation: repeat full pipeline per seed.
    run_fn(seed) -> {'rho': float, ...}
    Returns {'mean_rho', 'std_rho', 'per_seed': dict}
    """
    per_seed = {}
    rhos = []

    for seed in seeds:
        result = run_fn(seed)
        rho = result.get("rho", 0.0)
        per_seed[seed] = rho
        rhos.append(rho)

    return {
        "mean_rho": float(np.mean(rhos)),
        "std_rho": float(np.std(rhos)),
        "per_seed": per_seed,
    }
