"""Plotting functions for coupling analysis"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300

def plot_coupling_scatter(
    alignment_values: np.ndarray,
    wga_values: np.ndarray,
    rho: float,
    p_value: float,
    save_path: str
) -> None:
    """
    Generate scatter plot: A(w) vs WGA with regression.

    Args:
        alignment_values: Shape (M,)
        wga_values: Shape (M,)
        rho: Spearman correlation
        p_value: Statistical significance
        save_path: Output path for figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter plot with color gradient by position along path
    colors = np.linspace(0, 1, len(alignment_values))
    scatter = ax.scatter(
        alignment_values, wga_values,
        c=colors, cmap='viridis', s=100, alpha=0.7, edgecolors='black', linewidth=0.5
    )

    # Regression line
    z = np.polyfit(alignment_values, wga_values, 1)
    p = np.poly1d(z)
    ax.plot(
        alignment_values, p(alignment_values),
        "r--", alpha=0.8, linewidth=2, label='Linear fit'
    )

    # Annotations
    ax.text(
        0.05, 0.95,
        f'ρ = {rho:.3f}\np = {p_value:.4f}',
        transform=ax.transAxes,
        fontsize=14,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    )

    ax.set_xlabel('Curvature Alignment A(w)', fontsize=14)
    ax.set_ylabel('Worst-Group Accuracy (WGA)', fontsize=14)
    ax.set_title('Geometry-Phenotype Coupling (H-M4)', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12)

    cbar = plt.colorbar(scatter, ax=ax, label='Position along path (0=ERM, 1=DRO)')
    cbar.ax.tick_params(labelsize=10)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_trajectory(
    alphas: np.ndarray,
    alignment_values: np.ndarray,
    wga_values: np.ndarray,
    save_path: str
) -> None:
    """
    Generate trajectory plot: α vs A(w) and WGA (dual axes).

    Args:
        alphas: Interpolation values, shape (M,)
        alignment_values: A(w) values, shape (M,)
        wga_values: WGA values, shape (M,)
        save_path: Output path
    """
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Left axis: A(w)
    color = 'tab:blue'
    ax1.set_xlabel('Interpolation α (0=ERM, 1=DRO)', fontsize=14)
    ax1.set_ylabel('Curvature Alignment A(w)', color=color, fontsize=14)
    line1 = ax1.plot(alphas, alignment_values, color=color, marker='o',
                     linewidth=2, markersize=6, label='A(w)')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, alpha=0.3)

    # Right axis: WGA
    ax2 = ax1.twinx()
    color = 'tab:orange'
    ax2.set_ylabel('Worst-Group Accuracy (WGA)', color=color, fontsize=14)
    line2 = ax2.plot(alphas, wga_values, color=color, marker='s',
                     linewidth=2, markersize=6, label='WGA')
    ax2.tick_params(axis='y', labelcolor=color)

    # Title
    ax1.set_title('Metric Evolution Along Mode-Connected Path', fontsize=16, fontweight='bold')

    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=12)

    fig.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_comparison(
    fge_rho: float,
    fge_p: float,
    linear_rho: float,
    linear_p: float,
    save_path: str
) -> None:
    """
    Generate comparison plot: FGE vs Linear correlation.

    Args:
        fge_rho: FGE Spearman correlation
        fge_p: FGE p-value
        linear_rho: Linear Spearman correlation
        linear_p: Linear p-value
        save_path: Output path
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = ['FGE Path', 'Linear Path']
    rhos = [fge_rho, linear_rho]
    p_values = [fge_p, linear_p]

    # Bar plot
    bars = ax.bar(methods, rhos, color=['steelblue', 'coral'], alpha=0.8, edgecolor='black')

    # Add p-values as text
    for i, (bar, p_val) in enumerate(zip(bars, p_values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'p={p_val:.4f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Spearman Correlation ρ', fontsize=14)
    ax.set_title('Path Comparison: FGE vs Linear', fontsize=16, fontweight='bold')
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.axhline(y=-0.6, color='red', linestyle=':', linewidth=2, alpha=0.7, label='Success threshold')
    ax.legend(fontsize=12)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_group_accuracy(
    alphas: np.ndarray,
    group_accuracies: np.ndarray,
    save_path: str
) -> None:
    """
    Generate 4-group accuracy along path.

    Args:
        alphas: Interpolation values, shape (M,)
        group_accuracies: Group accuracies, shape (M, 4)
        save_path: Output path
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    group_names = ['Group 0', 'Group 1', 'Group 2', 'Group 3']
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']

    for g in range(4):
        ax.plot(alphas, group_accuracies[:, g], marker='o',
                linewidth=2, markersize=5, label=group_names[g], color=colors[g])

    ax.set_xlabel('Interpolation α (0=ERM, 1=DRO)', fontsize=14)
    ax.set_ylabel('Group Accuracy', fontsize=14)
    ax.set_title('Per-Group Accuracy Along Path', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
