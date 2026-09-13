"""Calibration score computation for inversion detection."""

import numpy as np
from typing import Dict


def compute_inversion_score(correct_logprob_norm: float, max_wrong_logprob_norm: float) -> float:
    """Compute calibration inversion score: max_wrong - correct."""
    return max_wrong_logprob_norm - correct_logprob_norm


def is_calibration_inverted(inversion_score: float, threshold: float = 0.1) -> bool:
    """Check if task shows calibration inversion (P(wrong) > P(correct) + threshold)."""
    return inversion_score > threshold


def build_calibration_vectors(inference_results: Dict[str, Dict]) -> np.ndarray:
    """Build calibration vector array for clustering.

    Returns:
        X: shape (n_tasks, 1) - inversion scores for clustering
    """
    scores = []
    for task_id, result in inference_results.items():
        score = compute_inversion_score(
            result["correct_logprob_norm"],
            result["max_wrong_logprob_norm"]
        )
        scores.append(score)

    return np.array(scores).reshape(-1, 1)
