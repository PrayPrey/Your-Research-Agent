"""Visualization module for entropy distributions, ROC curves, and calibration.

This module generates plots for experiment results.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


def plot_entropy_distributions(
    entropies: np.ndarray,
    labels: np.ndarray,
    output_path: str
):
    """Plot overlaid entropy distributions for correct vs hallucinated tokens.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels
    output_path : str
        Output file path
    """
    correct_entropies = entropies[labels == 0]
    hallucinated_entropies = entropies[labels == 1]

    plt.figure(figsize=(10, 6))

    # Histograms
    plt.hist(
        correct_entropies,
        bins=50,
        alpha=0.6,
        label=f'Correct (n={len(correct_entropies)})',
        density=True,
        color='blue'
    )
    plt.hist(
        hallucinated_entropies,
        bins=50,
        alpha=0.6,
        label=f'Hallucinated (n={len(hallucinated_entropies)})',
        density=True,
        color='red'
    )

    plt.xlabel('Entropy')
    plt.ylabel('Density')
    plt.title('Entropy Distribution: Correct vs Hallucinated Tokens')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved distribution plot to {output_path}")


def plot_roc_curve(
    fpr: list,
    tpr: list,
    auroc: float,
    output_path: str
):
    """Plot ROC curve.

    Parameters
    ----------
    fpr : list
        False positive rates
    tpr : list
        True positive rates
    auroc : float
        AUROC value
    output_path : str
        Output file path
    """
    plt.figure(figsize=(8, 8))

    plt.plot(fpr, tpr, linewidth=2, label=f'Entropy (AUROC = {auroc:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random (AUROC = 0.500)')

    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve: Entropy-Based Hallucination Detection')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved ROC curve to {output_path}")


def plot_calibration_curve(
    bin_entropies: list,
    error_rates: list,
    spearman_rho: float,
    output_path: str
):
    """Plot calibration curve.

    Parameters
    ----------
    bin_entropies : list
        Mean entropy per bin
    error_rates : list
        Error rate per bin
    spearman_rho : float
        Spearman correlation
    output_path : str
        Output file path
    """
    plt.figure(figsize=(10, 6))

    plt.plot(
        bin_entropies,
        error_rates,
        marker='o',
        linewidth=2,
        markersize=8,
        label=f'Calibration (ρ = {spearman_rho:.3f})'
    )

    plt.xlabel('Entropy')
    plt.ylabel('Error Rate (Hallucination Rate)')
    plt.title('Calibration Curve: Entropy vs Error Rate')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved calibration curve to {output_path}")


def generate_all_visualizations(
    entropies: np.ndarray,
    labels: np.ndarray,
    results: dict,
    output_dir: str
):
    """Generate all visualizations.

    Parameters
    ----------
    entropies : np.ndarray
        Entropy values
    labels : np.ndarray
        Binary labels
    results : dict
        Evaluation results
    output_dir : str
        Output directory
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Distribution plot
    plot_entropy_distributions(
        entropies,
        labels,
        f"{output_dir}/distributions.png"
    )

    # ROC curve
    plot_roc_curve(
        results['roc_curve']['fpr'],
        results['roc_curve']['tpr'],
        results['auroc']['auroc'],
        f"{output_dir}/roc_curve.png"
    )

    # Calibration curve
    plot_calibration_curve(
        results['calibration']['bin_entropies'],
        results['calibration']['error_rates'],
        results['calibration']['spearman_rho'],
        f"{output_dir}/calibration.png"
    )

    print(f"All visualizations saved to {output_dir}")
