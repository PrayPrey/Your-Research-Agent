"""Statistical analysis for H-M4 with Mann-Whitney comparison to H-M3."""

import os
import json
import numpy as np
from typing import List, Tuple
from scipy.stats import mannwhitneyu

# Import H-M4 config using importlib to avoid conflicts
import importlib.util
H_M4_PATH = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("m4_config", os.path.join(H_M4_PATH, "config.py"))
m4_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m4_config)

SEED = m4_config.SEED
N_BOOTSTRAP = m4_config.N_BOOTSTRAP
DEGRADATION_THRESHOLD = m4_config.DEGRADATION_THRESHOLD
H_M3_RESULTS_PATH = m4_config.H_M3_RESULTS_PATH


def bootstrap_ci(degradations: List[float], n_bootstrap: int = N_BOOTSTRAP, ci: float = 0.95) -> Tuple[float, float]:
    """Percentile bootstrap on the mean (inlined from H-M3)."""
    rng = np.random.default_rng(SEED)
    arr = np.array(degradations)
    means = [rng.choice(arr, size=len(arr), replace=True).mean() for _ in range(n_bootstrap)]
    alpha = (1 - ci) / 2
    return float(np.percentile(means, 100 * alpha)), float(np.percentile(means, 100 * (1 - alpha)))


def aggregate_results(transfer_results: List[dict]) -> dict:
    """Aggregate transfer results."""
    degs = [r["degradation"] for r in transfer_results]
    ci_lower, ci_upper = bootstrap_ci(degs)
    return {
        "mean_degradation": float(np.mean(degs)),
        "std_degradation": float(np.std(degs)),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "max_degradation": float(np.max(degs)),
        "min_degradation": float(np.min(degs)),
        "n_transfers": len(degs)
    }


def check_gate(agg: dict) -> bool:
    """Check H-M4 gate: mean_degradation > 0.15 (inverted from H-M3)."""
    return agg["mean_degradation"] > DEGRADATION_THRESHOLD


def compare_to_h_m3(cross_degradations: List[float], h_m3_path: str = H_M3_RESULTS_PATH) -> dict:
    """Mann-Whitney U test: cross-cluster degradations > within-cluster degradations."""
    with open(h_m3_path) as f:
        h_m3_results = json.load(f)

    within_degradations = [r["degradation"] for r in h_m3_results["transfers"]]

    # One-sided test: cross > within
    stat, p_value = mannwhitneyu(cross_degradations, within_degradations, alternative="greater")

    return {
        "statistic": float(stat),
        "p_value": float(p_value),
        "cross_mean": float(np.mean(cross_degradations)),
        "within_mean": float(np.mean(within_degradations)),
        "significant": p_value < 0.05
    }
