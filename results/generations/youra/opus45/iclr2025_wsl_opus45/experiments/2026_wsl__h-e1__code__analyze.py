"""
Grassmann Distance Computation and Statistical Analysis for H-E1

Computes pairwise Grassmann distances between LoRA adapter B matrix column spaces
and performs statistical tests for the existence hypothesis.
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
from scipy.linalg import subspace_angles
from scipy.stats import mannwhitneyu
from safetensors import safe_open

from config import (
    TASK_CATEGORIES,
    LORA_CONFIG,
    ANALYSIS_CONFIG,
    ADAPTER_DIR,
    RESULTS_DIR,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_b_matrices(adapter_path: str) -> dict:
    """
    Load PEFT adapter safetensors and extract all lora_B weight tensors.

    Args:
        adapter_path: Path to adapter directory

    Returns:
        Dict mapping layer_name -> B_matrix (numpy array)
    """
    # Find adapter weights file
    adapter_file = os.path.join(adapter_path, "adapter_model.safetensors")
    if not os.path.exists(adapter_file):
        # Try bin format
        adapter_file = os.path.join(adapter_path, "adapter_model.bin")
        if not os.path.exists(adapter_file):
            raise FileNotFoundError(f"No adapter weights found in {adapter_path}")

    b_matrices = {}

    if adapter_file.endswith(".safetensors"):
        with safe_open(adapter_file, framework="numpy") as f:
            for key in f.keys():
                if "lora_B" in key and "weight" in key:
                    # Extract layer name from key
                    # e.g., "base_model.model.model.layers.0.self_attn.q_proj.lora_B.weight"
                    layer_name = key.replace(".lora_B.weight", "")
                    b_matrices[layer_name] = f.get_tensor(key)
    else:
        import torch
        weights = torch.load(adapter_file, map_location="cpu")
        for key, tensor in weights.items():
            if "lora_B" in key and "weight" in key:
                layer_name = key.replace(".lora_B.weight", "")
                b_matrices[layer_name] = tensor.numpy()

    return b_matrices


def compute_orthonormal_basis(B: np.ndarray) -> np.ndarray:
    """
    QR decomposition of B to get orthonormal basis for column space.

    Args:
        B: LoRA B matrix [d_out, r]

    Returns:
        Q: Orthonormal basis [d_out, r]
    """
    Q, _ = np.linalg.qr(B)
    return Q


def grassmann_distance(B1: np.ndarray, B2: np.ndarray) -> float:
    """
    Compute Grassmann geodesic distance between column spaces of B1 and B2.

    Uses principal angles: distance = sqrt(sum(theta_i^2))

    Args:
        B1, B2: LoRA B matrices [d_out, r]

    Returns:
        Grassmann distance (scalar)
    """
    # Get orthonormal bases
    Q1 = compute_orthonormal_basis(B1)
    Q2 = compute_orthonormal_basis(B2)

    # Compute principal angles using scipy
    thetas = subspace_angles(Q1, Q2)

    # Grassmann geodesic distance
    return float(np.sqrt(np.sum(thetas ** 2)))


def compute_pairwise_matrix(
    adapter_paths: list,
    aggregate: str = "mean"
) -> tuple:
    """
    Compute pairwise Grassmann distances aggregated across all target layers.

    Args:
        adapter_paths: List of paths to adapter directories
        aggregate: Aggregation method ("mean" or "sum")

    Returns:
        Tuple of (distance_matrix, adapter_meta)
        - distance_matrix: [n_adapters, n_adapters] symmetric, zero diagonal
        - adapter_meta: List of {adapter_path, task, seed, category}
    """
    n = len(adapter_paths)
    distance_matrix = np.zeros((n, n))
    adapter_meta = []

    # Extract metadata and B matrices for all adapters
    logger.info(f"Loading B matrices from {n} adapters...")
    all_b_matrices = []

    for path in adapter_paths:
        # Parse task and seed from path
        # Expected format: .../adapters/{task}_seed{seed}/
        dirname = os.path.basename(path.rstrip("/"))
        parts = dirname.rsplit("_seed", 1)
        task = parts[0]
        seed = int(parts[1]) if len(parts) > 1 else 0

        category = TASK_CATEGORIES.get(task, "unknown")

        adapter_meta.append({
            "adapter_path": path,
            "task": task,
            "seed": seed,
            "category": category,
        })

        # Extract B matrices
        b_matrices = extract_b_matrices(path)
        all_b_matrices.append(b_matrices)

    # Get common layer names
    layer_names = list(all_b_matrices[0].keys())
    logger.info(f"Found {len(layer_names)} LoRA layers")

    # Compute pairwise distances
    logger.info("Computing pairwise Grassmann distances...")
    for i in range(n):
        if i % 20 == 0:
            logger.info(f"  Progress: {i}/{n}")
        for j in range(i + 1, n):
            # Compute distance for each layer
            layer_distances = []
            for layer_name in layer_names:
                B_i = all_b_matrices[i][layer_name]
                B_j = all_b_matrices[j][layer_name]
                d = grassmann_distance(B_i, B_j)
                layer_distances.append(d)

            # Aggregate across layers
            if aggregate == "mean":
                agg_distance = np.mean(layer_distances)
            else:
                agg_distance = np.sum(layer_distances)

            distance_matrix[i, j] = agg_distance
            distance_matrix[j, i] = agg_distance

    return distance_matrix, adapter_meta


def split_within_between(
    distance_matrix: np.ndarray,
    adapter_meta: list
) -> tuple:
    """
    Split upper-triangle distances into within-cluster and between-cluster.

    Cluster = TASK_CATEGORIES value ("reasoning" or "nlu").

    Args:
        distance_matrix: [n, n] symmetric distance matrix
        adapter_meta: List of adapter metadata dicts

    Returns:
        Tuple of (within_distances, between_distances) as 1D arrays
    """
    n = len(adapter_meta)
    within_distances = []
    between_distances = []

    for i in range(n):
        for j in range(i + 1, n):
            cat_i = adapter_meta[i]["category"]
            cat_j = adapter_meta[j]["category"]

            if cat_i == cat_j:
                within_distances.append(distance_matrix[i, j])
            else:
                between_distances.append(distance_matrix[i, j])

    return np.array(within_distances), np.array(between_distances)


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    Compute pooled-variance Cohen's d effect size.

    Args:
        group1, group2: Sample arrays

    Returns:
        Cohen's d value
    """
    n1, n2 = len(group1), len(group2)
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)

    # Pooled standard deviation
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))

    if pooled_std == 0:
        return 0.0

    return (np.mean(group1) - np.mean(group2)) / pooled_std


def _bootstrap_ci(
    within: np.ndarray,
    between: np.ndarray,
    n_boot: int = 10000,
    alpha: float = 0.05,
) -> tuple:
    """
    Bootstrap 95% CI for (between_mean - within_mean).

    Args:
        within: Within-cluster distances
        between: Between-cluster distances
        n_boot: Number of bootstrap iterations
        alpha: Significance level (default 0.05 for 95% CI)

    Returns:
        Tuple of (lower, upper) CI bounds
    """
    np.random.seed(42)  # For reproducibility
    diffs = []

    for _ in range(n_boot):
        within_sample = np.random.choice(within, size=len(within), replace=True)
        between_sample = np.random.choice(between, size=len(between), replace=True)
        diff = np.mean(between_sample) - np.mean(within_sample)
        diffs.append(diff)

    diffs = np.array(diffs)
    lower = np.percentile(diffs, 100 * alpha / 2)
    upper = np.percentile(diffs, 100 * (1 - alpha / 2))

    return float(lower), float(upper)


def run_statistical_tests(
    within: np.ndarray,
    between: np.ndarray
) -> dict:
    """
    Run statistical tests for hypothesis validation.

    Tests:
    - Mann-Whitney U (alternative='less') - within < between
    - Cohen's d effect size
    - 95% bootstrap CI

    Args:
        within: Within-cluster distances
        between: Between-cluster distances

    Returns:
        Dict with p_value, cohens_d, ci_95, within_mean, between_mean, passed
    """
    # Mann-Whitney U test: H0 = distributions are equal, H1 = within < between
    stat, p_value = mannwhitneyu(within, between, alternative='less')

    # Cohen's d: positive if between > within (expected direction)
    cohens_d = compute_cohens_d(between, within)

    # 95% CI for difference
    ci_lower, ci_upper = _bootstrap_ci(
        within, between,
        n_boot=ANALYSIS_CONFIG.get("n_bootstrap", 10000),
        alpha=1 - ANALYSIS_CONFIG.get("ci_level", 0.95)
    )

    # Compute means
    within_mean = float(np.mean(within))
    between_mean = float(np.mean(between))

    # Check gate criteria
    p_threshold = ANALYSIS_CONFIG["p_threshold"]
    d_threshold = ANALYSIS_CONFIG["cohens_d_threshold"]

    passed = (
        p_value < p_threshold and
        cohens_d > d_threshold and
        within_mean < between_mean
    )

    results = {
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "ci_95": [ci_lower, ci_upper],
        "within_mean": within_mean,
        "between_mean": between_mean,
        "within_std": float(np.std(within)),
        "between_std": float(np.std(between)),
        "within_n": len(within),
        "between_n": len(between),
        "effect_direction": "within < between" if within_mean < between_mean else "within >= between",
        "passed": passed,
        "gate_criteria": {
            "p_threshold": p_threshold,
            "cohens_d_threshold": d_threshold,
        }
    }

    return results


def run_analysis(hypothesis_folder: str) -> dict:
    """
    Top-level analysis: discover adapters, compute distances, run stats.

    Saves results to {hypothesis_folder}/results/:
    - pairwise_distances.npy
    - within_distances.npy
    - between_distances.npy
    - statistical_results.json

    Args:
        hypothesis_folder: Base folder for hypothesis

    Returns:
        Stats dict from run_statistical_tests
    """
    adapter_dir = os.path.join(hypothesis_folder, "adapters")
    results_dir = os.path.join(hypothesis_folder, "results")
    os.makedirs(results_dir, exist_ok=True)

    # Discover all adapter directories
    adapter_paths = []
    for item in sorted(os.listdir(adapter_dir)):
        item_path = os.path.join(adapter_dir, item)
        if os.path.isdir(item_path) and "_seed" in item:
            adapter_paths.append(item_path)

    logger.info(f"Found {len(adapter_paths)} adapters")

    if len(adapter_paths) == 0:
        raise ValueError(f"No adapters found in {adapter_dir}")

    # Compute pairwise distance matrix
    distance_matrix, adapter_meta = compute_pairwise_matrix(adapter_paths)

    # Split within/between
    within, between = split_within_between(distance_matrix, adapter_meta)

    logger.info(f"Within-cluster pairs: {len(within)}")
    logger.info(f"Between-cluster pairs: {len(between)}")

    # Run statistical tests
    stats = run_statistical_tests(within, between)

    # Save results
    np.save(os.path.join(results_dir, "pairwise_distances.npy"), distance_matrix)
    np.save(os.path.join(results_dir, "within_distances.npy"), within)
    np.save(os.path.join(results_dir, "between_distances.npy"), between)

    # Save adapter metadata
    with open(os.path.join(results_dir, "adapter_metadata.json"), "w") as f:
        json.dump(adapter_meta, f, indent=2)

    # Save statistical results
    with open(os.path.join(results_dir, "statistical_results.json"), "w") as f:
        json.dump(stats, f, indent=2)

    # Print summary
    logger.info("=" * 60)
    logger.info("STATISTICAL ANALYSIS RESULTS")
    logger.info("=" * 60)
    logger.info(f"Within-cluster mean:  {stats['within_mean']:.4f} (+/- {stats['within_std']:.4f})")
    logger.info(f"Between-cluster mean: {stats['between_mean']:.4f} (+/- {stats['between_std']:.4f})")
    logger.info(f"Effect direction:     {stats['effect_direction']}")
    logger.info(f"Mann-Whitney U p:     {stats['p_value']:.6f}")
    logger.info(f"Cohen's d:            {stats['cohens_d']:.4f}")
    logger.info(f"95% CI:               [{stats['ci_95'][0]:.4f}, {stats['ci_95'][1]:.4f}]")
    logger.info(f"GATE PASSED:          {stats['passed']}")
    logger.info("=" * 60)

    return stats


if __name__ == "__main__":
    from config import HYPOTHESIS_FOLDER

    print(f"Running analysis for: {HYPOTHESIS_FOLDER}")
    stats = run_analysis(HYPOTHESIS_FOLDER)
    print(f"Gate passed: {stats['passed']}")
