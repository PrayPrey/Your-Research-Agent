"""CorrelationAnalyzer: Spearman correlation + bootstrap CI + P3 control."""

import json
import os
from typing import NamedTuple

import numpy as np
from scipy.stats import spearmanr

import config


class CorrelationResult(NamedTuple):
    """Result of Spearman correlation analysis."""
    spearman_rho: float
    p_value: float
    ci_low: float
    ci_high: float
    n_pairs: int
    gate_passed: bool   # rho > 0.3 AND p < 0.05


class P3ControlResult(NamedTuple):
    """Result of P3 control analysis (within-task vs within-cluster)."""
    within_task_mean: float
    within_cluster_mean: float
    ratio: float                # within_task_mean / within_cluster_mean
    control_passed: bool        # ratio < 0.5


def compute_spearman_correlation(
    grassmann_matrix: np.ndarray,
    taxonomy_matrix: np.ndarray,
    n_bootstrap: int = 1000,
    random_seed: int = 42,
) -> CorrelationResult:
    """
    Flatten upper triangles of both matrices, compute Spearman rho + p-value
    + bootstrap 95% CI.

    Args:
        grassmann_matrix: (N, N) Grassmann distance matrix
        taxonomy_matrix: (N, N) taxonomy distance matrix
        n_bootstrap: Number of bootstrap iterations
        random_seed: Random seed for reproducibility

    Returns:
        CorrelationResult with gate_passed = (rho > 0.3 and p < 0.05)
    """
    g_flat = _flatten_upper_triangle(grassmann_matrix)
    t_flat = _flatten_upper_triangle(taxonomy_matrix)

    # Compute Spearman correlation
    rho, p_value = spearmanr(g_flat, t_flat)

    # Bootstrap CI for rho
    ci_low, ci_high = _bootstrap_spearman_ci(
        g_flat, t_flat, n_bootstrap, random_seed
    )

    # Gate evaluation
    rho_threshold = config.ANALYSIS_CONFIG["spearman_rho_threshold"]
    p_threshold = config.ANALYSIS_CONFIG["p_threshold"]
    gate_passed = (rho > rho_threshold) and (p_value < p_threshold)

    return CorrelationResult(
        spearman_rho=float(rho),
        p_value=float(p_value),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        n_pairs=len(g_flat),
        gate_passed=gate_passed,
    )


def compute_p3_control(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
    ratio_threshold: float = 0.5,
) -> P3ControlResult:
    """
    Extract within-task distances (same task, different seeds) and
    within-cluster distances (same category, different tasks).

    Args:
        grassmann_matrix: (N, N) Grassmann distance matrix
        adapter_meta: List of {task, seed, category, ...}
        ratio_threshold: P3 control threshold (default 0.5)

    Returns:
        P3ControlResult with control_passed = (within_task_mean < threshold * within_cluster_mean)
    """
    within_task = _extract_within_task_distances(grassmann_matrix, adapter_meta)
    within_cluster = _extract_within_cluster_distances(grassmann_matrix, adapter_meta)

    within_task_mean = float(np.mean(within_task))
    within_cluster_mean = float(np.mean(within_cluster))

    # Avoid division by zero
    if within_cluster_mean == 0:
        ratio = float('inf')
        control_passed = False
    else:
        ratio = within_task_mean / within_cluster_mean
        control_passed = ratio < ratio_threshold

    return P3ControlResult(
        within_task_mean=within_task_mean,
        within_cluster_mean=within_cluster_mean,
        ratio=ratio,
        control_passed=control_passed,
    )


def _flatten_upper_triangle(matrix: np.ndarray) -> np.ndarray:
    """
    Return 1D array of upper triangle values (k=1, excluding diagonal).

    Args:
        matrix: (N, N) symmetric matrix

    Returns:
        1D array of length N*(N-1)/2
    """
    n = matrix.shape[0]
    triu_indices = np.triu_indices(n, k=1)
    return matrix[triu_indices]


def _bootstrap_spearman_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_bootstrap: int = 1000,
    random_seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """
    Bootstrap CI for Spearman rho by resampling paired (x,y) rows.

    Args:
        x: Flattened Grassmann distances
        y: Flattened taxonomy distances
        n_bootstrap: Number of bootstrap iterations
        random_seed: Random seed
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        (ci_low, ci_high): 95% confidence interval bounds
    """
    rng = np.random.default_rng(random_seed)
    n = len(x)
    rhos = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        rho_boot, _ = spearmanr(x[idx], y[idx])
        if not np.isnan(rho_boot):
            rhos.append(rho_boot)

    if len(rhos) == 0:
        return (np.nan, np.nan)

    ci_low = float(np.percentile(rhos, 100 * alpha / 2))
    ci_high = float(np.percentile(rhos, 100 * (1 - alpha / 2)))

    return ci_low, ci_high


def _extract_within_task_distances(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
) -> np.ndarray:
    """
    Extract distances for pairs where same task, different seeds.

    Args:
        grassmann_matrix: (N, N) distance matrix
        adapter_meta: List of {task, seed, category, ...}

    Returns:
        1D array of within-task distances
    """
    n = len(adapter_meta)
    distances = []

    for i in range(n):
        for j in range(i + 1, n):
            if adapter_meta[i]['task'] == adapter_meta[j]['task']:
                distances.append(grassmann_matrix[i, j])

    return np.array(distances)


def _extract_within_cluster_distances(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
) -> np.ndarray:
    """
    Extract distances for pairs where same category but different tasks.

    Args:
        grassmann_matrix: (N, N) distance matrix
        adapter_meta: List of {task, seed, category, ...}

    Returns:
        1D array of within-cluster distances
    """
    n = len(adapter_meta)
    distances = []

    for i in range(n):
        for j in range(i + 1, n):
            # Same category, different task
            if (adapter_meta[i]['category'] == adapter_meta[j]['category']
                    and adapter_meta[i]['task'] != adapter_meta[j]['task']):
                distances.append(grassmann_matrix[i, j])

    return np.array(distances)


def save_correlation_results(
    corr: CorrelationResult,
    p3: P3ControlResult,
    results_dir: str,
    filename: str = "correlation_results.json",
) -> None:
    """
    Save correlation and P3 results to JSON file.

    Args:
        corr: CorrelationResult object
        p3: P3ControlResult object
        results_dir: Directory to save to
        filename: Output filename
    """
    os.makedirs(results_dir, exist_ok=True)

    results = {
        "spearman_correlation": {
            "rho": float(corr.spearman_rho),
            "p_value": float(corr.p_value),
            "ci_low": float(corr.ci_low),
            "ci_high": float(corr.ci_high),
            "n_pairs": int(corr.n_pairs),
            "gate_passed": bool(corr.gate_passed),
            "thresholds": {
                "rho_threshold": float(config.ANALYSIS_CONFIG["spearman_rho_threshold"]),
                "p_threshold": float(config.ANALYSIS_CONFIG["p_threshold"]),
            }
        },
        "p3_control": {
            "within_task_mean": float(p3.within_task_mean),
            "within_cluster_mean": float(p3.within_cluster_mean),
            "ratio": float(p3.ratio),
            "control_passed": bool(p3.control_passed),
            "threshold": float(config.ANALYSIS_CONFIG["p3_ratio_threshold"]),
        },
        "overall_gate_passed": bool(corr.gate_passed and p3.control_passed),
    }

    out_path = os.path.join(results_dir, filename)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
