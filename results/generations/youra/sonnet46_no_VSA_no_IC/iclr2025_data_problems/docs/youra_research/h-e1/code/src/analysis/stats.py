"""Variance statistics and gate check for h-e1."""
import numpy as np
from scipy.stats import spearmanr

THRESHOLDS = [0.0001, 0.0005, 0.001, 0.005, 0.01]


def compute_variance_stats(trajectories: np.ndarray, threshold: float = 0.001) -> dict:
    """Returns per_domain_std, n_domains_passing, gate_passed, threshold_sensitivity."""
    stds = np.std(trajectories, axis=1)  # (22,)
    n_passing = int(np.sum(stds > threshold))

    sensitivity = {}
    for t in THRESHOLDS:
        sensitivity[t] = int(np.sum(stds > t))

    return {
        "per_domain_std": stds,
        "n_domains_passing": n_passing,
        "gate_passed": bool(n_passing >= 10),
        "threshold_sensitivity": sensitivity,
        "max_std": float(stds.max()),
        "min_std": float(stds.min()),
        "mean_std": float(stds.mean()),
    }


def compute_spearman_matrix(all_stds: dict) -> np.ndarray:
    """Returns (N, N) Spearman rho matrix over domain-std vectors."""
    sizes = list(all_stds.keys())
    n = len(sizes)
    rho_matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            rho, _ = spearmanr(all_stds[sizes[i]], all_stds[sizes[j]])
            rho_matrix[i, j] = rho
            rho_matrix[j, i] = rho
    return rho_matrix, sizes


def check_gate(
    results: dict,
    min_domains: int = 10,
    min_model_sizes: int = 8,
) -> bool:
    """Gate: n_domains_passing >= min_domains in >= min_model_sizes."""
    passing_sizes = sum(
        1 for stats in results.values()
        if stats["n_domains_passing"] >= min_domains
    )
    return passing_sizes >= min_model_sizes
