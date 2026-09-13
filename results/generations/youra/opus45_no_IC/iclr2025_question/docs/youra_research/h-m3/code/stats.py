"""Statistical analysis for H-M3."""

import numpy as np
from typing import List, Tuple
from config import SEED, N_BOOTSTRAP, DEGRADATION_THRESHOLD, CI_UPPER_THRESHOLD


def bootstrap_ci(degradations: List[float], n_bootstrap: int = N_BOOTSTRAP, ci: float = 0.95) -> Tuple[float, float]:
    """Percentile bootstrap on the mean."""
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
    """Check SHOULD_WORK gate."""
    return agg["mean_degradation"] <= DEGRADATION_THRESHOLD and agg["ci_upper"] < CI_UPPER_THRESHOLD
