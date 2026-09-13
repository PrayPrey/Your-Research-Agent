"""H-M2 Visualization: Generate figures for execution depth analysis."""

import logging
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from depth_tracer import DepthResult

logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def plot_gate_metrics(metrics: Dict, figures_dir: str) -> None:
    """Bar chart showing target p=0.05 vs actual p-value and mean depths.

    Args:
        metrics: Analysis metrics dict
        figures_dir: Directory to save figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: P-value comparison
    ax1 = axes[0]
    p_actual = metrics["p_value"]
    p_threshold = metrics["p_threshold"]

    bars = ax1.bar(["Threshold", "Actual"], [p_threshold, p_actual],
                   color=["gray", "green" if p_actual < p_threshold else "red"])
    ax1.axhline(y=p_threshold, color="red", linestyle="--", linewidth=2, label=f"Threshold (p={p_threshold})")
    ax1.set_ylabel("P-value")
    ax1.set_title("Gate Condition: P-value")
    ax1.set_ylim(0, max(p_threshold * 2, p_actual * 1.5))

    # Add value labels
    for bar, val in zip(bars, [p_threshold, p_actual]):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                 f"{val:.4f}", ha='center', va='bottom', fontsize=10)

    # Right: Mean depth comparison
    ax2 = axes[1]
    rl_mean = metrics["rl_statistics"]["mean"]
    dpo_mean = metrics["dpo_statistics"]["mean"]
    rl_ci = (metrics["rl_statistics"]["ci_lower"], metrics["rl_statistics"]["ci_upper"])
    dpo_ci = (metrics["dpo_statistics"]["ci_lower"], metrics["dpo_statistics"]["ci_upper"])

    x = np.array([0, 1])
    bars = ax2.bar(x, [rl_mean, dpo_mean], color=["#2ecc71", "#e74c3c"], width=0.6)

    # Error bars (95% CI)
    rl_err = [[rl_mean - rl_ci[0]], [rl_ci[1] - rl_mean]]
    dpo_err = [[dpo_mean - dpo_ci[0]], [dpo_ci[1] - dpo_mean]]
    ax2.errorbar(0, rl_mean, yerr=rl_err, fmt='none', color='black', capsize=5)
    ax2.errorbar(1, dpo_mean, yerr=dpo_err, fmt='none', color='black', capsize=5)

    ax2.set_xticks(x)
    ax2.set_xticklabels(["RL", "DPO"])
    ax2.set_ylabel("Mean Execution Depth")
    ax2.set_title(f"Mean Depth Comparison (Cohen's d = {metrics['cohens_d']:.3f})")

    # Add value labels
    for bar, val in zip(bars, [rl_mean, dpo_mean]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f"{val:.3f}", ha='center', va='bottom', fontsize=10)

    # Overall gate result
    gate_str = "PASS" if metrics["gate_pass"] else "FAIL"
    fig.suptitle(f"H-M2 Gate Metrics (Gate: {gate_str})", fontsize=14, fontweight='bold')

    plt.tight_layout()
    save_path = os.path.join(figures_dir, "gate_metrics.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved gate metrics figure to {save_path}")


def plot_depth_distribution(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """Violin/box plot comparing RL and DPO depth distributions.

    Args:
        rl_results: DepthResult list for RL
        dpo_results: DepthResult list for DPO
        figures_dir: Directory to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    rl_depths = [r.execution_depth for r in rl_results]
    dpo_depths = [r.execution_depth for r in dpo_results]

    data = {
        "Depth": rl_depths + dpo_depths,
        "Model": ["RL"] * len(rl_depths) + ["DPO"] * len(dpo_depths),
    }

    # Violin plot with embedded box plot
    parts = ax.violinplot([rl_depths, dpo_depths], positions=[0, 1], showmeans=True, showmedians=True)

    # Color the violins
    colors = ["#2ecc71", "#e74c3c"]
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i])
        pc.set_alpha(0.7)

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["RL", "DPO"])
    ax.set_ylabel("Execution Depth")
    ax.set_title("Execution Depth Distribution by Alignment Method")

    # Add stats annotation
    rl_mean, dpo_mean = np.mean(rl_depths), np.mean(dpo_depths)
    rl_std, dpo_std = np.std(rl_depths), np.std(dpo_depths)
    ax.text(0.02, 0.98, f"RL: mean={rl_mean:.3f}, std={rl_std:.3f}, n={len(rl_depths)}",
            transform=ax.transAxes, verticalalignment='top', fontsize=9)
    ax.text(0.02, 0.92, f"DPO: mean={dpo_mean:.3f}, std={dpo_std:.3f}, n={len(dpo_depths)}",
            transform=ax.transAxes, verticalalignment='top', fontsize=9)

    plt.tight_layout()
    save_path = os.path.join(figures_dir, "depth_distribution.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved depth distribution figure to {save_path}")


def plot_depth_by_error_type(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """Grouped bar chart showing mean depth by error type.

    Args:
        rl_results: DepthResult list for RL
        dpo_results: DepthResult list for DPO
        figures_dir: Directory to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    error_types = ["syntax", "runtime", "assertion", "other"]

    rl_means = []
    dpo_means = []
    rl_counts = []
    dpo_counts = []

    for et in error_types:
        rl_subset = [r.execution_depth for r in rl_results if r.error_type == et]
        dpo_subset = [r.execution_depth for r in dpo_results if r.error_type == et]

        rl_means.append(np.mean(rl_subset) if rl_subset else 0)
        dpo_means.append(np.mean(dpo_subset) if dpo_subset else 0)
        rl_counts.append(len(rl_subset))
        dpo_counts.append(len(dpo_subset))

    x = np.arange(len(error_types))
    width = 0.35

    bars1 = ax.bar(x - width/2, rl_means, width, label='RL', color='#2ecc71')
    bars2 = ax.bar(x + width/2, dpo_means, width, label='DPO', color='#e74c3c')

    ax.set_xticks(x)
    ax.set_xticklabels([f"{et}\n(RL:{rc}, DPO:{dc})" for et, rc, dc in zip(error_types, rl_counts, dpo_counts)])
    ax.set_ylabel("Mean Execution Depth")
    ax.set_title("Mean Execution Depth by Error Type")
    ax.legend()

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2, height + 0.01,
                       f"{height:.2f}", ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    save_path = os.path.join(figures_dir, "depth_by_error_type.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved depth by error type figure to {save_path}")


def plot_depth_cdf(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """CDF of execution depth for RL vs DPO.

    Args:
        rl_results: DepthResult list for RL
        dpo_results: DepthResult list for DPO
        figures_dir: Directory to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    rl_depths = sorted([r.execution_depth for r in rl_results])
    dpo_depths = sorted([r.execution_depth for r in dpo_results])

    # Compute CDFs
    rl_cdf = np.arange(1, len(rl_depths) + 1) / len(rl_depths)
    dpo_cdf = np.arange(1, len(dpo_depths) + 1) / len(dpo_depths)

    ax.plot(rl_depths, rl_cdf, label='RL', color='#2ecc71', linewidth=2)
    ax.plot(dpo_depths, dpo_cdf, label='DPO', color='#e74c3c', linewidth=2)

    ax.set_xlabel("Execution Depth")
    ax.set_ylabel("Cumulative Probability")
    ax.set_title("CDF of Execution Depth")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(figures_dir, "depth_cdf.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved depth CDF figure to {save_path}")


def plot_depth_scatter(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    figures_dir: str,
) -> None:
    """Scatter plot of execution depth vs total lines, colored by model.

    Args:
        rl_results: DepthResult list for RL
        dpo_results: DepthResult list for DPO
        figures_dir: Directory to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    rl_total = [r.total_lines for r in rl_results]
    rl_depth = [r.execution_depth for r in rl_results]
    dpo_total = [r.total_lines for r in dpo_results]
    dpo_depth = [r.execution_depth for r in dpo_results]

    ax.scatter(rl_total, rl_depth, alpha=0.5, label='RL', color='#2ecc71', s=20)
    ax.scatter(dpo_total, dpo_depth, alpha=0.5, label='DPO', color='#e74c3c', s=20)

    ax.set_xlabel("Total Executable Lines")
    ax.set_ylabel("Execution Depth")
    ax.set_title("Execution Depth vs Code Length")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    save_path = os.path.join(figures_dir, "depth_scatter.png")
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"Saved depth scatter figure to {save_path}")


def generate_all_figures(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    metrics: Dict,
    figures_dir: str,
) -> None:
    """Generate all visualization figures.

    Args:
        rl_results: DepthResult list for RL
        dpo_results: DepthResult list for DPO
        metrics: Analysis metrics dict
        figures_dir: Directory to save figures
    """
    os.makedirs(figures_dir, exist_ok=True)

    logger.info("Generating visualization figures...")

    plot_gate_metrics(metrics, figures_dir)
    plot_depth_distribution(rl_results, dpo_results, figures_dir)
    plot_depth_by_error_type(rl_results, dpo_results, figures_dir)
    plot_depth_cdf(rl_results, dpo_results, figures_dir)
    plot_depth_scatter(rl_results, dpo_results, figures_dir)

    logger.info(f"All figures saved to {figures_dir}")
