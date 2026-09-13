"""
Visualization functions for experiment results.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12


def plot_rho_distribution(
    factual_rho: np.ndarray,
    creative_rho: np.ndarray,
    save_path: Path
) -> None:
    """
    Generate violin plot comparing ρ_j distributions.

    Args:
        factual_rho: (N,) array of factual ρ_j values
        creative_rho: (N,) array of creative ρ_j values
        save_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Prepare data
    data = []
    labels = []
    for val in factual_rho:
        data.append(val)
        labels.append('Factual')
    for val in creative_rho:
        data.append(val)
        labels.append('Creative')

    # Create violin plot
    positions = [1, 2]
    parts = ax.violinplot(
        [factual_rho, creative_rho],
        positions=positions,
        showmeans=True,
        showmedians=True
    )

    # Customize colors
    colors = ['#1f77b4', '#ff7f0e']
    for pc, color in zip(parts['bodies'], colors):
        pc.set_facecolor(color)
        pc.set_alpha(0.7)

    # Add labels
    ax.set_xticks(positions)
    ax.set_xticklabels(['Factual', 'Creative'])
    ax.set_ylabel('ρ_j (Claim-type Mass Ratio)')
    ax.set_title('ρ_j Distribution: Factual vs Creative Domains')

    # Add median values as text
    median_factual = np.median(factual_rho)
    median_creative = np.median(creative_rho)
    ax.text(1, median_factual, f'{median_factual:.3f}', ha='center', va='bottom')
    ax.text(2, median_creative, f'{median_creative:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    logger.info(f"Saved ρ_j distribution plot to {save_path}")


def plot_nli_heatmap(
    factual_scores: np.ndarray,
    creative_scores: np.ndarray,
    save_path: Path
) -> None:
    """
    Generate heatmap of NLI score distributions.

    Args:
        factual_scores: (N_factual, 3) array
        creative_scores: (N_creative, 3) array
        save_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(8, 4))

    # Compute mean scores for each domain
    factual_mean = factual_scores.mean(axis=0)
    creative_mean = creative_scores.mean(axis=0)

    # Prepare data for heatmap
    data = np.array([factual_mean, creative_mean])

    # Create heatmap
    sns.heatmap(
        data,
        annot=True,
        fmt='.3f',
        cmap='viridis',
        xticklabels=['Contradiction', 'Entailment', 'Neutral'],
        yticklabels=['Factual', 'Creative'],
        ax=ax,
        cbar_kws={'label': 'Mean Probability'}
    )

    ax.set_title('NLI Score Distribution by Domain')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    logger.info(f"Saved NLI heatmap to {save_path}")


def plot_autocorrelation(
    factual_autocorr: List[float],
    creative_autocorr: List[float],
    save_path: Path
) -> None:
    """
    Generate line plot comparing autocorrelation.

    Args:
        factual_autocorr: List of autocorr coefficients
        creative_autocorr: List of autocorr coefficients
        save_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    lags = range(1, len(factual_autocorr) + 1)

    # Plot lines
    ax.plot(lags, factual_autocorr, 'o-', color='#1f77b4', label='Factual', linewidth=2)
    ax.plot(lags, creative_autocorr, 'o-', color='#ff7f0e', label='Creative', linewidth=2)

    # Add horizontal reference lines
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=0.4, color='red', linestyle=':', alpha=0.5, label='Creative Threshold (0.4)')
    ax.axhline(y=0.2, color='blue', linestyle=':', alpha=0.5, label='Factual Threshold (0.2)')

    ax.set_xlabel('Lag')
    ax.set_ylabel('Autocorrelation Coefficient')
    ax.set_title('Autocorrelation Comparison: Factual vs Creative')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    logger.info(f"Saved autocorrelation plot to {save_path}")


def plot_sample_scatter(
    factual_rho: np.ndarray,
    creative_rho: np.ndarray,
    save_path: Path
) -> None:
    """
    Generate scatter plot of per-sample ρ_j values.

    Args:
        factual_rho: (N,) array
        creative_rho: (N,) array
        save_path: Output file path
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create indices
    factual_indices = np.arange(len(factual_rho))
    creative_indices = np.arange(len(creative_rho))

    # Plot scatter
    ax.scatter(factual_indices, factual_rho, alpha=0.6, color='#1f77b4', label='Factual', s=20)
    ax.scatter(creative_indices, creative_rho, alpha=0.6, color='#ff7f0e', label='Creative', s=20)

    # Add median lines
    ax.axhline(y=np.median(factual_rho), color='#1f77b4', linestyle='--', alpha=0.7, linewidth=2)
    ax.axhline(y=np.median(creative_rho), color='#ff7f0e', linestyle='--', alpha=0.7, linewidth=2)

    ax.set_xlabel('Sample Index')
    ax.set_ylabel('ρ_j Value')
    ax.set_title('Per-Sample ρ_j Values by Domain')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    logger.info(f"Saved sample scatter plot to {save_path}")
