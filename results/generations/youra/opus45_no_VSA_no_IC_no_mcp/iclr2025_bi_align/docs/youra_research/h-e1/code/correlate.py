"""Correlation analysis for H-E1 benchmark correlation experiment."""

import numpy as np
from scipy.stats import pearsonr
from itertools import combinations
from config import CORR_THRESHOLD


def compute_pairwise_correlations(scores: dict) -> dict:
    """Compute pairwise Pearson correlations between benchmarks."""
    benchmarks = list(scores.keys())
    correlations = {}

    for b1, b2 in combinations(benchmarks, 2):
        # Truncate to min length for correlation
        n = min(len(scores[b1]), len(scores[b2]))
        r, p = pearsonr(scores[b1][:n], scores[b2][:n])
        correlations[f"{b1}_vs_{b2}"] = {"r": float(r), "p": float(p)}

    return correlations


def check_gate(correlations: dict, threshold: float = CORR_THRESHOLD) -> bool:
    """Check if all correlations are below threshold."""
    return all(abs(c["r"]) < threshold for c in correlations.values())
