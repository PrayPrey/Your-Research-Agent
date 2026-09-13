"""Evaluation metrics for h-m1."""
import numpy as np


def compute_mode_sensitivity(scores: dict) -> dict:
    """Mean influence score per mode."""
    return {mode: float(np.mean(arr)) for mode, arr in scores.items()}


def build_interaction_matrix(results: dict) -> np.ndarray:
    """Build 3x3 method x mode interaction matrix.

    Args:
        results: dict[method -> dict[mode -> np.ndarray]]

    Returns:
        3x3 array, rows=methods (trak, tracin, kronfluence), cols=modes (mem, transfer, spurious)
        Values are min-max normalized per row.
    """
    methods = ["trak", "tracin", "kronfluence"]
    modes = ["mem", "transfer", "spurious"]

    matrix = np.zeros((3, 3))
    for i, method in enumerate(methods):
        sensitivities = compute_mode_sensitivity(results[method])
        for j, mode in enumerate(modes):
            matrix[i, j] = sensitivities[mode]

    # Min-max normalize per row
    for i in range(3):
        row_min, row_max = matrix[i].min(), matrix[i].max()
        if row_max > row_min:
            matrix[i] = (matrix[i] - row_min) / (row_max - row_min)
        else:
            matrix[i] = 0.5  # Constant row

    return matrix


def rank_modes(mode_scores: dict) -> tuple:
    """Rank modes by sensitivity (descending)."""
    sorted_modes = sorted(mode_scores.items(), key=lambda x: x[1], reverse=True)
    return tuple(m for m, _ in sorted_modes)


def verify_mechanism_active(results: dict) -> tuple:
    """Verify h-m1 mechanism hypothesis.

    Returns:
        (success, details_dict)
        success: True if >= 2 methods have different mode rankings
    """
    methods = ["trak", "tracin", "kronfluence"]

    # Check variance > 0 for each method
    variance_ok = {}
    for method in methods:
        all_scores = np.concatenate(list(results[method].values()))
        variance_ok[method] = float(np.var(all_scores)) > 0

    # Get rankings
    rankings = {}
    for method in methods:
        sens = compute_mode_sensitivity(results[method])
        rankings[method] = rank_modes(sens)

    # Count unique rankings
    unique_rankings = len(set(rankings.values()))
    ranking_diff = unique_rankings >= 2

    details = {
        "variance_ok": variance_ok,
        "rankings": rankings,
        "unique_rankings": unique_rankings,
        "ranking_diff": ranking_diff
    }

    success = all(variance_ok.values()) and ranking_diff
    return success, details
