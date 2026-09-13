"""Correlation analysis functions"""

from scipy.stats import spearmanr
import numpy as np
from typing import Tuple

def compute_spearman_correlation(
    alignment_values: np.ndarray,
    wga_values: np.ndarray
) -> Tuple[float, float]:
    """
    Compute Spearman correlation between A(w) and WGA.

    Args:
        alignment_values: Array of A(w) values, shape (M,)
        wga_values: Array of WGA values, shape (M,)

    Returns:
        rho: Spearman correlation coefficient
        p_value: Statistical significance (H0: rho = 0)

    Raises:
        ValueError: If arrays have different lengths
    """
    if len(alignment_values) != len(wga_values):
        raise ValueError(f"Arrays must have same length: {len(alignment_values)} vs {len(wga_values)}")

    # Handle edge cases
    if len(alignment_values) < 3:
        raise ValueError("Need at least 3 samples for correlation")

    rho, p_value = spearmanr(alignment_values, wga_values)

    return float(rho), float(p_value)
