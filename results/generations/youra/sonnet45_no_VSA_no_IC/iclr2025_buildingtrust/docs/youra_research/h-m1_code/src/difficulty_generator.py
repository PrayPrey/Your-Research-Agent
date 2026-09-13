"""Difficulty score generation independent of dimension labels."""

import numpy as np
from scipy.stats import pearsonr


def generate_difficulty_scores(n_samples: int, seed: int = 42) -> np.ndarray:
    """Generate instance difficulty scores independent of dimension labels.

    Args:
        n_samples: Number of samples
        seed: Random seed for reproducibility

    Returns:
        [n_samples] float array in [0, 1], Normal(0.5, 0.15) clipped
    """
    np.random.seed(seed)
    scores = np.random.normal(0.5, 0.15, n_samples)
    return np.clip(scores, 0.0, 1.0)


def validate_independence(
    difficulty: np.ndarray,
    dimension_labels: dict[str, np.ndarray],
    threshold: float = 0.2
) -> bool:
    """Validate difficulty is independent of all dimension labels.

    Args:
        difficulty: [N] difficulty scores
        dimension_labels: {dimension: [N] binary array}
        threshold: Max allowed |correlation|

    Returns:
        True if all |corr(difficulty, dim)| < threshold
    """
    for dim, labels in dimension_labels.items():
        corr, _ = pearsonr(difficulty, labels)
        if abs(corr) >= threshold:
            print(f"FAIL: |corr(difficulty, {dim})| = {abs(corr):.4f} >= {threshold}")
            return False
        print(f"PASS: |corr(difficulty, {dim})| = {abs(corr):.4f} < {threshold}")
    return True
