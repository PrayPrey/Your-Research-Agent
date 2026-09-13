"""Statistical correlation analysis."""
from typing import Dict, Tuple
import numpy as np
from scipy.stats import pearsonr

def compute_pairwise_correlations(
    exec: np.ndarray,
    ai: np.ndarray,
    human: np.ndarray
) -> Dict[str, Tuple[float, float]]:
    """Compute all pairwise correlations. Returns {pair: (r, p)}."""
    results = {}

    # Execution vs Human
    r, p = pearsonr(exec, human)
    results["exec_human"] = (r, p)

    # AI vs Human
    r, p = pearsonr(ai, human)
    results["ai_human"] = (r, p)

    # Execution vs AI
    r, p = pearsonr(exec, ai)
    results["exec_ai"] = (r, p)

    return results

def bootstrap_ci(
    data1: np.ndarray,
    data2: np.ndarray,
    n_iter: int = 1000,
    seed: int = 42
) -> Tuple[float, float]:
    """Bootstrap 95% CI for Pearson r."""
    np.random.seed(seed)
    n = len(data1)
    rs = []

    for _ in range(n_iter):
        indices = np.random.choice(n, n, replace=True)
        r, _ = pearsonr(data1[indices], data2[indices])
        rs.append(r)

    return np.percentile(rs, 2.5), np.percentile(rs, 97.5)

def evaluate_gate(correlations: Dict[str, Tuple[float, float]], kappa: float) -> Tuple[bool, str]:
    """Check MUST_WORK gate: all p<0.05 and kappa>0.6."""
    failures = []

    for pair, (r, p) in correlations.items():
        if p >= 0.05:
            failures.append(f"{pair}: p={p:.3f} >= 0.05")

    if kappa <= 0.6:
        failures.append(f"kappa={kappa:.3f} <= 0.6")

    if failures:
        return False, "; ".join(failures)
    else:
        return True, "All correlations significant (p<0.05) and kappa>0.6"
