"""Visualizer: Generate 4 figures for H-M1 reward density analysis."""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]
FIGURES_DIR = "h-m1/figures"


def plot_early_phase_bar(
    phase_stats: dict,
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Bar chart of mean reward density (steps 0-2500) per condition with std error bars."""
    os.makedirs(figures_dir, exist_ok=True)
    conditions = [c for c in CONDITIONS if c in phase_stats]
    means = [phase_stats[c]["early"]["mean"] for c in conditions]
    stds = [phase_stats[c]["early"]["std"] for c in conditions]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(conditions, means, yerr=stds, capsize=5, color=["#2196F3", "#FF9800", "#4CAF50", "#F44336"])
    ax.set_xlabel("Condition")
    ax.set_ylabel("Mean Reward Density (steps 0-2500)")
    ax.set_title("Early Phase Reward Density by Condition")
    ax.set_ylim(0, 1.1)
    plt.tight_layout()

    out_path = os.path.join(figures_dir, "reward_density_early_phase_bar.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_timeseries(
    logs: dict,
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Line plot of reward density at each 500-step checkpoint for all 4 conditions."""
    from loader import compute_early_phase_density, compute_late_phase_density
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = {"curriculum": "#2196F3", "uniform": "#FF9800", "easy_only": "#4CAF50", "hard_only": "#F44336"}
    checkpoints = list(range(500, 5001, 500))

    for condition in CONDITIONS:
        if condition not in logs:
            continue
        df = logs[condition]
        early = compute_early_phase_density(df)
        late = compute_late_phase_density(df)
        all_vals = np.concatenate([early, late])
        x = checkpoints[:len(all_vals)]
        ax.plot(x, all_vals, label=condition, color=colors.get(condition), marker="o", markersize=4)

    ax.axvline(x=2500, color="gray", linestyle="--", alpha=0.7, label="Curriculum step (2500)")
    ax.set_xlabel("Training Step")
    ax.set_ylabel("Mean Reward Density (per 500-step window)")
    ax.set_title("Reward Density Timeseries (All Conditions)")
    ax.legend()
    ax.set_ylim(0, 1.1)
    plt.tight_layout()

    out_path = os.path.join(figures_dir, "reward_density_timeseries.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_wilcoxon_boxplot(
    curriculum_vals: np.ndarray,
    uniform_vals: np.ndarray,
    p_value: float,
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Boxplot of curriculum vs uniform early-phase values with p-value annotation."""
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.boxplot([curriculum_vals, uniform_vals], labels=["curriculum", "uniform"])
    ax.set_ylabel("Reward Density (steps 0-2500)")
    ax.set_title(f"Wilcoxon one-tailed p={p_value:.4f}")
    ax.set_ylim(0, 1.1)
    # Annotate significance
    significance = "p < 0.05 ✓" if p_value < 0.05 else "p ≥ 0.05 ✗"
    ax.text(0.5, 0.95, significance, transform=ax.transAxes,
            ha="center", va="top", fontsize=11,
            color="green" if p_value < 0.05 else "red")
    plt.tight_layout()

    out_path = os.path.join(figures_dir, "reward_density_wilcoxon_boxplot.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path


def plot_phase_comparison(
    phase_stats: dict,
    figures_dir: str = FIGURES_DIR,
) -> str:
    """Side-by-side bar chart of early vs late phase reward density per condition."""
    os.makedirs(figures_dir, exist_ok=True)
    conditions = [c for c in CONDITIONS if c in phase_stats]
    x = np.arange(len(conditions))
    width = 0.35

    early_means = [phase_stats[c]["early"]["mean"] for c in conditions]
    late_means = [phase_stats[c]["late"]["mean"] for c in conditions]
    early_stds = [phase_stats[c]["early"]["std"] for c in conditions]
    late_stds = [phase_stats[c]["late"]["std"] for c in conditions]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, early_means, width, yerr=early_stds, capsize=4,
           label="Early phase (steps 0-2500)", color="#2196F3")
    ax.bar(x + width / 2, late_means, width, yerr=late_stds, capsize=4,
           label="Late phase (steps 2501-5000)", color="#FF9800")
    ax.set_xticks(x)
    ax.set_xticklabels(conditions)
    ax.set_xlabel("Condition")
    ax.set_ylabel("Mean Reward Density")
    ax.set_title("Early vs Late Phase Reward Density by Condition")
    ax.legend()
    ax.set_ylim(0, 1.2)
    plt.tight_layout()

    out_path = os.path.join(figures_dir, "reward_density_phase_comparison.png")
    plt.savefig(out_path, dpi=150)
    plt.close()
    return out_path
