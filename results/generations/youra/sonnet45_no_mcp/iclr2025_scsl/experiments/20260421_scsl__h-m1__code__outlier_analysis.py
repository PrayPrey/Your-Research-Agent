"""
Outlier Analysis Module for h-m1
Identifies and compares outlier eigenvalues beyond Marchenko-Pastur bulk edge
"""

import numpy as np
from typing import Dict, Any, Tuple


def identify_outliers(
    eigenvalues: np.ndarray,
    bulk_edge: float
) -> Dict[str, Any]:
    """
    Identify outlier eigenvalues beyond MP bulk edge

    Args:
        eigenvalues: (100,) - Hessian eigenvalues (descending order)
        bulk_edge: float - Marchenko-Pastur threshold λ_+

    Returns:
        outlier_stats: dict with:
            - num_outliers: int
            - outlier_eigenvalues: np.ndarray
            - max_eigenvalue: float
            - mean_outlier: float
            - outlier_fraction: float
            - outlier_indices: np.ndarray
    """
    # Create outlier mask
    outlier_mask = eigenvalues > bulk_edge
    outlier_eigenvalues = eigenvalues[outlier_mask]
    outlier_indices = np.where(outlier_mask)[0]

    # Count outliers
    num_outliers = len(outlier_eigenvalues)

    # Compute statistics
    max_eigenvalue = eigenvalues[0] if len(eigenvalues) > 0 else 0.0
    mean_outlier = np.mean(outlier_eigenvalues) if num_outliers > 0 else 0.0
    outlier_fraction = num_outliers / len(eigenvalues) if len(eigenvalues) > 0 else 0.0

    return {
        'num_outliers': num_outliers,
        'outlier_eigenvalues': outlier_eigenvalues,
        'max_eigenvalue': max_eigenvalue,
        'mean_outlier': mean_outlier,
        'outlier_fraction': outlier_fraction,
        'outlier_indices': outlier_indices,
        'bulk_edge': bulk_edge
    }


def compare_outlier_concentration(
    erm_stats: Dict[str, Any],
    dro_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare outlier concentration between ERM and DRO

    Args:
        erm_stats: Outlier statistics for ERM model
        dro_stats: Outlier statistics for DRO model

    Returns:
        comparison: dict with:
            - num_outliers_ERM: int
            - num_outliers_DRO: int
            - num_outliers_diff: int (ERM - DRO)
            - max_eigenvalue_ERM: float
            - max_eigenvalue_DRO: float
            - max_eigenvalue_ratio: float (ERM / DRO)
            - mechanism_confirmed: bool (ERM > DRO)
            - percentage_increase: float
            - effect_description: str
    """
    # Extract key metrics
    num_outliers_ERM = erm_stats['num_outliers']
    num_outliers_DRO = dro_stats['num_outliers']
    max_eigenvalue_ERM = erm_stats['max_eigenvalue']
    max_eigenvalue_DRO = dro_stats['max_eigenvalue']

    # Compute differences
    num_outliers_diff = num_outliers_ERM - num_outliers_DRO

    # Compute ratios
    max_eigenvalue_ratio = max_eigenvalue_ERM / max_eigenvalue_DRO if max_eigenvalue_DRO > 0 else float('inf')

    # Determine mechanism confirmation
    mechanism_confirmed = (num_outliers_diff > 0)

    # Compute percentage increase
    percentage_increase = (num_outliers_diff / num_outliers_DRO * 100) if num_outliers_DRO > 0 else float('inf')

    # Generate effect description
    if mechanism_confirmed:
        effect_description = f"ERM has {num_outliers_diff} more outliers than DRO ({percentage_increase:.1f}% increase)"
    else:
        effect_description = "GATE FAILURE: ERM does not have more outliers than DRO"

    return {
        'num_outliers_ERM': num_outliers_ERM,
        'num_outliers_DRO': num_outliers_DRO,
        'num_outliers_diff': num_outliers_diff,
        'max_eigenvalue_ERM': max_eigenvalue_ERM,
        'max_eigenvalue_DRO': max_eigenvalue_DRO,
        'max_eigenvalue_ratio': max_eigenvalue_ratio,
        'mechanism_confirmed': mechanism_confirmed,
        'percentage_increase': percentage_increase,
        'effect_description': effect_description,
        'mean_outlier_ERM': erm_stats['mean_outlier'],
        'mean_outlier_DRO': dro_stats['mean_outlier']
    }


def compute_outlier_distribution(
    eigenvalues: np.ndarray,
    bulk_edge: float,
    num_bins: int = 20
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute histogram of outlier eigenvalue distribution

    Args:
        eigenvalues: (100,) - Hessian eigenvalues
        bulk_edge: float - MP threshold
        num_bins: int - number of histogram bins

    Returns:
        bin_edges: (num_bins+1,) - histogram bin edges
        bin_counts: (num_bins,) - counts per bin
    """
    # Extract outlier eigenvalues
    outlier_mask = eigenvalues > bulk_edge
    outlier_eigs = eigenvalues[outlier_mask]

    # If no outliers, return empty bins
    if len(outlier_eigs) == 0:
        return np.array([]), np.array([])

    # Create histogram
    bin_counts, bin_edges = np.histogram(outlier_eigs, bins=num_bins)

    return bin_edges, bin_counts


def analyze_outlier_spacing(outlier_eigenvalues: np.ndarray) -> Dict[str, float]:
    """
    Analyze spacing between consecutive outlier eigenvalues

    Args:
        outlier_eigenvalues: (K,) - outlier eigenvalues (descending)

    Returns:
        spacing_stats: dict with mean_spacing, std_spacing, max_gap
    """
    if len(outlier_eigenvalues) < 2:
        return {
            'mean_spacing': 0.0,
            'std_spacing': 0.0,
            'max_gap': 0.0,
            'min_gap': 0.0
        }

    # Compute gaps between consecutive eigenvalues (descending order)
    gaps = outlier_eigenvalues[:-1] - outlier_eigenvalues[1:]

    return {
        'mean_spacing': float(np.mean(gaps)),
        'std_spacing': float(np.std(gaps)),
        'max_gap': float(np.max(gaps)),
        'min_gap': float(np.min(gaps))
    }


def compute_statistical_significance(
    erm_outliers: np.ndarray,
    dro_outliers: np.ndarray
) -> Dict[str, float]:
    """
    Compute statistical significance of difference (descriptive for single seed)

    Args:
        erm_outliers: (K_erm,) - ERM outlier eigenvalues
        dro_outliers: (K_dro,) - DRO outlier eigenvalues

    Returns:
        stats: dict with descriptive statistics
    """
    return {
        'erm_mean': float(np.mean(erm_outliers)) if len(erm_outliers) > 0 else 0.0,
        'erm_std': float(np.std(erm_outliers)) if len(erm_outliers) > 0 else 0.0,
        'dro_mean': float(np.mean(dro_outliers)) if len(dro_outliers) > 0 else 0.0,
        'dro_std': float(np.std(dro_outliers)) if len(dro_outliers) > 0 else 0.0,
        'note': 'Single seed - descriptive statistics only'
    }


def generate_comparison_summary(comparison: Dict[str, Any]) -> str:
    """
    Generate human-readable comparison summary

    Returns:
        summary: str - formatted summary with gate check result
    """
    summary = "=" * 60 + "\n"
    summary += "OUTLIER CONCENTRATION COMPARISON\n"
    summary += "=" * 60 + "\n"
    summary += f"ERM Outliers: {comparison['num_outliers_ERM']}\n"
    summary += f"DRO Outliers: {comparison['num_outliers_DRO']}\n"
    summary += f"Difference: {comparison['num_outliers_diff']}\n"

    if comparison['percentage_increase'] != float('inf'):
        summary += f"Percentage Increase: {comparison['percentage_increase']:.1f}%\n"

    summary += f"\nMax Eigenvalue Ratio (ERM/DRO): {comparison['max_eigenvalue_ratio']:.4f}\n"
    summary += f"Mean Outlier ERM: {comparison['mean_outlier_ERM']:.4f}\n"
    summary += f"Mean Outlier DRO: {comparison['mean_outlier_DRO']:.4f}\n"

    summary += "\nGATE CHECK (MUST_WORK):\n"
    summary += f"Mechanism Confirmed: {comparison['mechanism_confirmed']}\n"
    summary += f"Result: {'PASS ✓' if comparison['mechanism_confirmed'] else 'FAIL ✗'}\n"

    summary += f"\n{comparison['effect_description']}\n"
    summary += "=" * 60 + "\n"

    return summary
