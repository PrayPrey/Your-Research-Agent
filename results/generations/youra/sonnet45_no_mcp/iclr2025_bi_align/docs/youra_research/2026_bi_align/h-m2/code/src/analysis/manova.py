"""
MANOVA statistical analysis module.
Tasks: task-008, task-009, task-010 - Effect size calculation and gate logic
"""

import numpy as np
from scipy.stats import f_oneway
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_cohens_d(
    group1: np.ndarray,
    group2: np.ndarray
) -> float:
    """
    Compute Cohen's d effect size.

    Args:
        group1: First group embeddings (N1, D)
        group2: Second group embeddings (N2, D)

    Returns:
        Cohen's d effect size
    """
    # Mean difference
    mean1 = np.mean(group1, axis=0)
    mean2 = np.mean(group2, axis=0)
    mean_diff = mean1 - mean2

    # Pooled standard deviation
    var1 = np.var(group1, axis=0, ddof=1)
    var2 = np.var(group2, axis=0, ddof=1)
    pooled_std = np.sqrt((var1 + var2) / 2)

    # Cohen's d per dimension
    cohens_d_per_dim = mean_diff / (pooled_std + 1e-8)

    # Aggregate: use norm of effect size vector
    cohens_d = np.linalg.norm(cohens_d_per_dim) / np.sqrt(len(cohens_d_per_dim))

    return float(cohens_d)


def compute_manova_effect_size(
    chosen_embeddings: np.ndarray,
    rejected_embeddings: np.ndarray
) -> Dict[str, float]:
    """
    Compute multivariate effect size.

    Args:
        chosen_embeddings: Chosen group (N1, D)
        rejected_embeddings: Rejected group (N2, D)

    Returns:
        Dict with cohens_d, mean_separation, f_statistic, p_value
    """
    # Cohen's d
    cohens_d = compute_cohens_d(chosen_embeddings, rejected_embeddings)

    # Mean separation (Euclidean distance between centroids)
    mean_chosen = np.mean(chosen_embeddings, axis=0)
    mean_rejected = np.mean(rejected_embeddings, axis=0)
    mean_separation = np.linalg.norm(mean_chosen - mean_rejected)

    # MANOVA F-statistic (simplified univariate version)
    f_stat, p_value = f_oneway(chosen_embeddings.flatten(), rejected_embeddings.flatten())

    results = {
        'cohens_d': float(cohens_d),
        'mean_separation': float(mean_separation),
        'f_statistic': float(f_stat),
        'p_value': float(p_value)
    }

    logger.info(f"MANOVA results: Cohen's d = {cohens_d:.3f}, p = {p_value:.6f}")

    return results


def baseline_random_separation(
    embeddings: np.ndarray,
    n_trials: int = 100,
    seed: int = 42
) -> List[float]:
    """
    Compute baseline effect sizes with random labels.

    Args:
        embeddings: All embeddings (N, D)
        n_trials: Number of random trials
        seed: Random seed

    Returns:
        List of random baseline Cohen's d values
    """
    np.random.seed(seed)
    n_samples = len(embeddings)
    baseline_ds = []

    logger.info(f"Computing random baseline ({n_trials} trials)...")

    for _ in range(n_trials):
        # Random label assignment (50/50 split)
        indices = np.random.permutation(n_samples)
        split = n_samples // 2
        group1 = embeddings[indices[:split]]
        group2 = embeddings[indices[split:split*2]]

        d = compute_cohens_d(group1, group2)
        baseline_ds.append(d)

    baseline_mean = np.mean(baseline_ds)
    baseline_std = np.std(baseline_ds)
    logger.info(f"Random baseline: mean = {baseline_mean:.3f}, std = {baseline_std:.3f}")

    return baseline_ds


def gate_decision(
    cohens_d: float,
    baseline_d: float,
    primary_threshold: float = 0.5,
    secondary_threshold: float = 0.3
) -> Tuple[str, Dict]:
    """
    Implement gate threshold checking.

    Args:
        cohens_d: Proposed method effect size
        baseline_d: Random baseline effect size
        primary_threshold: Primary gate (Cohen's d >= 0.5)
        secondary_threshold: Secondary gate (d > 0.3)

    Returns:
        (decision, details) where decision is "PASS" or "FAIL"
    """
    details = {
        'cohens_d': cohens_d,
        'baseline_d': baseline_d,
        'primary_threshold': primary_threshold,
        'secondary_threshold': secondary_threshold,
        'exceeds_baseline': cohens_d > baseline_d,
        'meets_primary': cohens_d >= primary_threshold,
        'meets_secondary': cohens_d > secondary_threshold
    }

    if cohens_d >= primary_threshold and cohens_d > secondary_threshold:
        decision = "PASS"
        logger.info(f"✅ Gate PASSED: d={cohens_d:.3f} >= {primary_threshold}")
    else:
        decision = "FAIL"
        logger.warning(f"❌ Gate FAILED: d={cohens_d:.3f} < {primary_threshold}")

    return decision, details
