"""Statistical analysis for H-C1: 3-way pairwise convergence gate."""
import numpy as np
from typing import List, Dict, Any

import config

PAIRS = [("stats", "mlp"), ("stats", "nfn"), ("mlp", "nfn")]
METHODS = ["stats", "mlp", "nfn"]


def pairwise_deltas(means: Dict[str, float]) -> Dict[str, float]:
    """Compute |R2_a - R2_b| for all method pairs."""
    deltas = {}
    for a, b in PAIRS:
        deltas[f"{a}_{b}"] = abs(means[a] - means[b])
    return deltas


def summarize_gate(results: List[Dict]) -> Dict[str, Any]:
    """Summarize results and check 3-way convergence gate."""
    means = {m: np.mean([r[f"r2_{m}"] for r in results]) for m in METHODS}
    stds = {m: np.std([r[f"r2_{m}"] for r in results]) for m in METHODS}

    deltas = pairwise_deltas(means)
    max_delta = max(deltas.values())

    sanity_pass = all(means[m] > config.R2_SANITY_MIN for m in METHODS)
    gate_pass = sanity_pass and max_delta <= config.R2_PAIR_DELTA_MAX

    return {
        "means": means,
        "stds": stds,
        "pairwise_deltas": deltas,
        "max_delta": max_delta,
        "sanity_pass": sanity_pass,
        "gate_pass": gate_pass,
        "threshold": config.R2_PAIR_DELTA_MAX,
    }
