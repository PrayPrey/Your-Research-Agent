"""
Visualization Module for h-m1 Outlier Analysis
Generates all required figures for outlier concentration comparison
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from pathlib import Path


def plot_outlier_comparison(erm_stats: Dict, dro_stats: Dict, save_path: str, config: Dict = None):
    """
    Bar chart: num_outliers_ERM vs num_outliers_DRO (GATE METRIC)

    This is the primary gate metric visualization
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    methods = ['ERM', 'Group-DRO']
    values = [erm_stats['num_outliers'], dro_stats['num_outliers']]
    colors = ['red', 'blue'] if config is None else [config.get('erm', 'red'), config.get('dro', 'blue')]

    ax.bar(methods, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Number of Outlier Eigenvalues (λ > λ₊)', fontsize=12)
    ax.set_title('Hessian Outlier Concentration: ERM vs Group-DRO', fontsize=14, fontweight='bold')
    ax.set_ylim([0, max(values) * 1.2])
    ax.grid(axis='y', alpha=0.3)

    # Add values on bars
    for i, v in enumerate(values):
        ax.text(i, v + max(values) * 0.02, str(v), ha='center', va='bottom',
                fontsize=14, fontweight='bold')

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_spectra_comparison(
    eigenvalues_erm: np.ndarray,
    eigenvalues_dro: np.ndarray,
    bulk_edge_erm: float,
    bulk_edge_dro: float,
    save_path: str,
    config: Dict = None
):
    """Side-by-side eigenvalue spectra with bulk edge overlays"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ERM spectrum
    ax1.plot(range(len(eigenvalues_erm)), eigenvalues_erm, 'o-', color='red', alpha=0.6,
             markersize=4, label='ERM Eigenvalues')
    ax1.axhline(y=bulk_edge_erm, color='darkred', linestyle='--', linewidth=2,
                label=f'Bulk Edge (λ₊ = {bulk_edge_erm:.4f})')
    ax1.set_xlabel('Eigenvalue Index', fontsize=11)
    ax1.set_ylabel('Eigenvalue Magnitude', fontsize=11)
    ax1.set_title('ERM Eigenvalue Spectrum', fontsize=13, fontweight='bold')
    ax1.set_yscale('log')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # DRO spectrum
    ax2.plot(range(len(eigenvalues_dro)), eigenvalues_dro, 'o-', color='blue', alpha=0.6,
             markersize=4, label='DRO Eigenvalues')
    ax2.axhline(y=bulk_edge_dro, color='darkblue', linestyle='--', linewidth=2,
                label=f'Bulk Edge (λ₊ = {bulk_edge_dro:.4f})')
    ax2.set_xlabel('Eigenvalue Index', fontsize=11)
    ax2.set_ylabel('Eigenvalue Magnitude', fontsize=11)
    ax2.set_title('Group-DRO Eigenvalue Spectrum', fontsize=13, fontweight='bold')
    ax2.set_yscale('log')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_outlier_distributions(
    erm_outliers: np.ndarray,
    dro_outliers: np.ndarray,
    save_path: str,
    config: Dict = None
):
    """Histogram comparison of outlier eigenvalue distributions"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # ERM outlier distribution
    if len(erm_outliers) > 0:
        ax1.hist(erm_outliers, bins=15, color='red', alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Eigenvalue Magnitude', fontsize=11)
        ax1.set_ylabel('Count', fontsize=11)
        ax1.set_title(f'ERM Outlier Distribution (n={len(erm_outliers)})', fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

    # DRO outlier distribution
    if len(dro_outliers) > 0:
        ax2.hist(dro_outliers, bins=15, color='blue', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Eigenvalue Magnitude', fontsize=11)
        ax2.set_ylabel('Count', fontsize=11)
        ax2.set_title(f'DRO Outlier Distribution (n={len(dro_outliers)})', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_mp_fit_quality(
    eigenvalues: np.ndarray,
    bulk_edge: float,
    sigma_sq: float,
    gamma: float,
    model_name: str,
    save_path: str
):
    """Q-Q plot for MP fit validation"""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Marchenko-Pastur PDF for reference
    lambda_minus = sigma_sq * (1 - np.sqrt(gamma))**2
    lambda_plus = sigma_sq * (1 + np.sqrt(gamma))**2

    # Plot eigenvalue histogram
    ax.hist(eigenvalues, bins=30, density=True, alpha=0.6, color='gray',
            edgecolor='black', label='Eigenvalue Histogram')

    # Mark bulk edge
    ax.axvline(x=bulk_edge, color='red', linestyle='--', linewidth=2,
               label=f'Bulk Edge λ₊ = {bulk_edge:.4f}')
    ax.axvline(x=lambda_minus, color='green', linestyle=':', linewidth=1.5,
               label=f'MP λ₋ = {lambda_minus:.4f}')

    ax.set_xlabel('Eigenvalue Magnitude', fontsize=11)
    ax.set_ylabel('Density', fontsize=11)
    ax.set_title(f'MP Fit Quality - {model_name}\n(σ²={sigma_sq:.4f}, γ={gamma:.4f})',
                 fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def plot_eigenvalue_decay(
    eigenvalues_erm: np.ndarray,
    eigenvalues_dro: np.ndarray,
    save_path: str
):
    """Cumulative eigenvalue decay curves"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Cumulative sum
    cum_erm = np.cumsum(eigenvalues_erm)
    cum_dro = np.cumsum(eigenvalues_dro)

    # Normalize
    cum_erm_norm = cum_erm / cum_erm[-1]
    cum_dro_norm = cum_dro / cum_dro[-1]

    ax.plot(range(len(cum_erm_norm)), cum_erm_norm, 'o-', color='red',
            alpha=0.7, markersize=3, label='ERM')
    ax.plot(range(len(cum_dro_norm)), cum_dro_norm, 's-', color='blue',
            alpha=0.7, markersize=3, label='Group-DRO')

    ax.set_xlabel('Eigenvalue Index', fontsize=11)
    ax.set_ylabel('Cumulative Fraction of Total Curvature', fontsize=11)
    ax.set_title('Eigenvalue Decay Curves', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {save_path}")


def generate_all_figures(
    erm_eigenvalues: np.ndarray,
    dro_eigenvalues: np.ndarray,
    erm_outlier_stats: Dict,
    dro_outlier_stats: Dict,
    erm_bulk_edge: float,
    dro_bulk_edge: float,
    erm_sigma_sq: float,
    erm_gamma: float,
    dro_sigma_sq: float,
    dro_gamma: float,
    figures_dir: str,
    viz_config: Dict = None
):
    """Generate all visualization figures"""
    print("\n[Generating Visualizations]")

    # Figure 1: Gate Metric - Outlier Comparison (CRITICAL)
    plot_outlier_comparison(
        erm_outlier_stats,
        dro_outlier_stats,
        f"{figures_dir}/fig1_outlier_comparison.png",
        viz_config.get('colors', {}) if viz_config else None
    )

    # Figure 2: Spectra Comparison
    plot_spectra_comparison(
        erm_eigenvalues,
        dro_eigenvalues,
        erm_bulk_edge,
        dro_bulk_edge,
        f"{figures_dir}/fig2_spectra_comparison.png",
        viz_config
    )

    # Figure 3: Outlier Distributions
    plot_outlier_distributions(
        erm_outlier_stats['outlier_eigenvalues'],
        dro_outlier_stats['outlier_eigenvalues'],
        f"{figures_dir}/fig3_outlier_distributions.png",
        viz_config
    )

    # Figure 4: MP Fit Quality - ERM
    plot_mp_fit_quality(
        erm_eigenvalues,
        erm_bulk_edge,
        erm_sigma_sq,
        erm_gamma,
        'ERM',
        f"{figures_dir}/fig4_mp_fit_quality_erm.png"
    )

    # Figure 5: MP Fit Quality - DRO
    plot_mp_fit_quality(
        dro_eigenvalues,
        dro_bulk_edge,
        dro_sigma_sq,
        dro_gamma,
        'Group-DRO',
        f"{figures_dir}/fig5_mp_fit_quality_dro.png"
    )

    # Figure 6: Eigenvalue Decay
    plot_eigenvalue_decay(
        erm_eigenvalues,
        dro_eigenvalues,
        f"{figures_dir}/fig6_eigenvalue_decay.png"
    )

    print("✓ All figures generated successfully")
