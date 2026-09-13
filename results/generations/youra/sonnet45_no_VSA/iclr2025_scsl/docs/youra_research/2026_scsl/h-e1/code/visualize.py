"""Visualization generation."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys
sys.path.append('/workspace/TEST_scsl/docs/youra_research/h-e1/code')
from config import OUTPUT_CONFIG, EXPERIMENT_CONFIG

# Plot style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")


def plot_heatmap(results: dict, save_path: str):
    """
    Generate conditions × digits accuracy heatmap.

    Args:
        results: Dict with keys {baseline, flip30, flip50, flip90, rotation}
        save_path: Output file path
    """
    conditions = EXPERIMENT_CONFIG["conditions"]

    # Build matrix (5 conditions × 10 digits)
    matrix = np.zeros((5, 10))
    for i, condition in enumerate(conditions):
        matrix[i] = results[condition]["per_class"]

    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".1f",
        cmap="viridis",
        xticklabels=list(range(10)),
        yticklabels=[c.capitalize() for c in conditions],
        vmin=85,
        vmax=100,
        cbar_kws={"label": "Accuracy (%)"},
        ax=ax
    )
    ax.set_xlabel("Digit Class")
    ax.set_ylabel("Augmentation Condition")
    ax.set_title("Per-Class Accuracy Across Conditions")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_group_comparison(results: dict, save_path: str):
    """
    Generate symmetric vs asymmetric bar chart.

    Args:
        results: Dict with condition results
        save_path: Output file path
    """
    conditions = EXPERIMENT_CONFIG["conditions"]

    symmetric_means = [results[c]["symmetric_mean"] for c in conditions]
    asymmetric_means = [results[c]["asymmetric_mean"] for c in conditions]

    x = np.arange(len(conditions))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, symmetric_means, width, label="Symmetric {0,1,8}", color="steelblue")
    ax.bar(x + width/2, asymmetric_means, width, label="Asymmetric {2,3,5,6,7,9}", color="coral")

    ax.set_xlabel("Augmentation Condition")
    ax.set_ylabel("Mean Accuracy (%)")
    ax.set_title("Group-Level Accuracy Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in conditions])
    ax.legend()
    ax.set_ylim(85, 100)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_dose_response(results: dict, save_path: str):
    """
    Generate flip probability vs accuracy plot.

    Args:
        results: Dict with condition results
        save_path: Output file path
    """
    flip_probs = [0.0, 0.3, 0.5, 0.9]
    conditions = ["baseline", "flip30", "flip50", "flip90"]

    symmetric_accs = [results[c]["symmetric_mean"] for c in conditions]
    asymmetric_accs = [results[c]["asymmetric_mean"] for c in conditions]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(flip_probs, symmetric_accs, marker="o", label="Symmetric {0,1,8}",
            linewidth=2, markersize=8, color="steelblue")
    ax.plot(flip_probs, asymmetric_accs, marker="^", label="Asymmetric {2,3,5,6,7,9}",
            linewidth=2, markersize=8, color="coral")

    ax.set_xlabel("Horizontal Flip Probability")
    ax.set_ylabel("Mean Accuracy (%)")
    ax.set_title("Dose-Response: Flip Probability vs Accuracy")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(85, 100)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
