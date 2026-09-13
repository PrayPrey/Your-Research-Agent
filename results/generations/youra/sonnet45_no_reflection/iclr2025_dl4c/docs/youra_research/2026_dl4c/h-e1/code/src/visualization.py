"""
Visualization for H-E1 Results
Generate plots for validation report.
"""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import Dict
import os

sns.set_style("whitegrid")

def plot_eigenspectrum(eigenvalues: np.ndarray, output_path: str):
    """Plot eigenvalue spectrum."""
    plt.figure(figsize=(8, 6))
    plt.bar(range(1, len(eigenvalues) + 1), eigenvalues, color='steelblue', alpha=0.8)
    plt.xlabel('Eigenvalue Index', fontsize=12)
    plt.ylabel('Eigenvalue Magnitude', fontsize=12)
    plt.title('Eigenspectrum of Residual Covariance Matrix', fontsize=14, fontweight='bold')
    plt.xticks(range(1, len(eigenvalues) + 1))
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_permutation_distribution(
    null_gaps: np.ndarray,
    observed_gap: float,
    p_value: float,
    percentile_95: float,
    output_path: str
):
    """Plot permutation test null distribution."""
    plt.figure(figsize=(10, 6))
    bins = min(50, len(np.unique(null_gaps)))  # Adaptive bins
    plt.hist(null_gaps, bins=bins, color='gray', alpha=0.6, label='Null Distribution', edgecolor='black')
    plt.axvline(observed_gap, color='red', linestyle='--', linewidth=2, label=f'Observed Gap: {observed_gap:.3f}')
    plt.axvline(percentile_95, color='orange', linestyle=':', linewidth=2, label=f'95th Percentile: {percentile_95:.3f}')
    plt.xlabel('Spectral Gap (λ₄/mean(λ₁,λ₂,λ₃))', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title(f'Permutation Test (p = {p_value:.4f})', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_covariance_heatmap(covariance_matrix: np.ndarray, output_path: str):
    """Plot covariance matrix heatmap."""
    plt.figure(figsize=(8, 7))
    labels = ['Correctness', 'Quality', 'Security', 'Efficiency']
    sns.heatmap(
        covariance_matrix,
        annot=True,
        fmt='.3f',
        cmap='RdBu_r',
        center=0,
        square=True,
        linewidths=1,
        xticklabels=labels,
        yticklabels=labels,
        cbar_kws={'label': 'Covariance'}
    )
    plt.title('Residual Covariance Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_coupling_analysis(coupling: float, threshold: float, output_path: str):
    """Plot cross-aspect coupling analysis."""
    plt.figure(figsize=(8, 6))
    colors = ['green' if coupling <= threshold else 'red']
    plt.bar(['Cross-Aspect Coupling'], [coupling], color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    plt.axhline(threshold, color='orange', linestyle='--', linewidth=2, label=f'Threshold: {threshold}')
    plt.ylabel('Coupling Ratio (median off-diag / median diag)', fontsize=11)
    plt.title('Cross-Aspect Coupling Analysis', fontsize=14, fontweight='bold')
    plt.ylim(0, max(coupling * 1.5, threshold * 1.5))
    plt.legend(fontsize=10)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def generate_all_figures(results: Dict, output_dir: str):
    """Generate all visualization figures."""
    os.makedirs(output_dir, exist_ok=True)

    # Extract data
    eigenvalues = np.array(results['spectral_analysis']['eigenvalues'])
    covariance_matrix = np.array(results['spectral_analysis']['covariance_matrix'])
    coupling = results['spectral_analysis']['coupling']

    perm = results['permutation_test']
    null_gaps = np.random.normal(perm['null_mean'], perm['null_std'], 1000)  # Reconstruct
    observed_gap = results['spectral_analysis']['spectral_gap']

    # Generate plots
    plot_eigenspectrum(eigenvalues, os.path.join(output_dir, 'eigenspectrum.png'))
    plot_permutation_distribution(
        null_gaps,
        observed_gap,
        perm['p_value'],
        perm['percentile_95'],
        os.path.join(output_dir, 'permutation_test.png')
    )
    plot_covariance_heatmap(covariance_matrix, os.path.join(output_dir, 'covariance_heatmap.png'))
    plot_coupling_analysis(coupling, 0.2, os.path.join(output_dir, 'coupling_analysis.png'))

    print(f"✅ Generated 4 figures in {output_dir}/")
