"""Visualization for H-E1 experiment."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from config import Config


def plot_2x2_bar(results: dict[str, float], cfg: Config) -> Path:
    """Plot 2x2 factorial bar chart."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = ["CE-Single", "CE-Refine", "RL-Single", "RL-Refine"]
    values = [results.get(c, 0) for c in conditions]
    colors = ["#4CAF50", "#81C784", "#2196F3", "#64B5F6"]

    bars = ax.bar(conditions, values, color=colors, edgecolor="black")

    ax.set_ylabel("pass@1", fontsize=12)
    ax.set_xlabel("Condition", fontsize=12)
    ax.set_title("2×2 Factorial: Training × Inference", fontsize=14)
    ax.set_ylim(0, max(values) * 1.2 if values else 1.0)

    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    out_path = cfg.figures_dir / "2x2_bar.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_interaction(results: dict[str, float], cfg: Config) -> Path:
    """Plot interaction effect (lines)."""
    fig, ax = plt.subplots(figsize=(8, 6))

    x = ["Single", "Refine"]
    ce_vals = [results.get("CE-Single", 0), results.get("CE-Refine", 0)]
    rl_vals = [results.get("RL-Single", 0), results.get("RL-Refine", 0)]

    ax.plot(x, ce_vals, "o-", label="CE Training", color="#4CAF50", linewidth=2, markersize=10)
    ax.plot(x, rl_vals, "s-", label="RL Training", color="#2196F3", linewidth=2, markersize=10)

    ax.set_ylabel("pass@1", fontsize=12)
    ax.set_xlabel("Inference Mode", fontsize=12)
    ax.set_title("Interaction: Training × Refinement", fontsize=14)
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    # Compute and display interaction
    ce_gain = ce_vals[1] - ce_vals[0]
    rl_gain = rl_vals[1] - rl_vals[0]
    interaction = rl_gain - ce_gain

    ax.text(0.95, 0.05, f"Interaction: {interaction:+.4f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=11, bbox=dict(boxstyle="round", facecolor="wheat"))

    plt.tight_layout()
    out_path = cfg.figures_dir / "interaction.png"
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def generate_all_figures(results: dict[str, float], cfg: Config) -> list[Path]:
    """Generate all required figures."""
    figures = []
    figures.append(plot_2x2_bar(results, cfg))
    figures.append(plot_interaction(results, cfg))
    return figures
