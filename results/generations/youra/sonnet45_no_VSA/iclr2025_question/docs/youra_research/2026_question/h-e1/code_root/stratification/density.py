"""Boundary density computation and stratification."""

import numpy as np
from typing import Dict


def compute_boundary_density(S: np.ndarray, epsilon: float, window: float = 0.1) -> float:
    """Compute boundary density score for a question.
    
    Args:
        S: N×N similarity matrix
        epsilon: Clustering threshold
        window: Boundary region half-width
    
    Returns:
        Boundary density ∈ [0, 1]
    """
    # Extract upper triangle (excluding diagonal)
    upper_tri = S[np.triu_indices_from(S, k=1)]
    
    # Count similarities near threshold
    near_threshold = np.abs(upper_tri - epsilon) <= window
    
    return near_threshold.sum() / len(upper_tri) if len(upper_tri) > 0 else 0.0


def stratify_terciles(boundary_densities: np.ndarray) -> Dict[str, np.ndarray]:
    """Stratify questions into LOW/MID/HIGH terciles.
    
    Args:
        boundary_densities: [Q] array of BD scores
    
    Returns:
        Dictionary of boolean masks for each stratum
    """
    p33 = np.percentile(boundary_densities, 33.33)
    p67 = np.percentile(boundary_densities, 66.67)
    
    strata = {
        'LOW': boundary_densities < p33,
        'MID': (boundary_densities >= p33) & (boundary_densities < p67),
        'HIGH': boundary_densities >= p67
    }
    
    return strata
