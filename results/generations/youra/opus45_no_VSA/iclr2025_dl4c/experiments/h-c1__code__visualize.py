"""Visualization for H-C1 experiment."""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from config import Config


def plot_interaction_vs_entropy(results: dict, cfg: Config) -> Path:
    """Plot interaction effect vs feedback entropy (required gate figure)."""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Extract data points
    conditions = results.get("conditions", {})
    entropies = []
    interactions = []
    labels = []

    for cond, data in conditions.items():
        if "entropy" in data and "interaction" in data:
            entropies.append(data["entropy"])
            interactions.append(data["interaction"])
            labels.append(cond)

    if not entropies:
        # Fallback: use summary data
        entropies = [results.get("entropy_low", 1.0), results.get("entropy_high", 2.5)]
        interactions = [results.get("interaction_low", 0), results.get("interaction_high", 0)]
        labels = ["Low Diversity", "High Diversity"]

    colors = ['blue' if 'High' in l else 'red' for l in labels]
    ax.scatter(entropies, interactions, s=100, c=colors, alpha=0.7)

    for i, label in enumerate(labels):
        ax.annotate(label, (entropies[i], interactions[i]), textcoords="offset points",
                    xytext=(5, 5), fontsize=9)

    # Draw threshold lines
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Zero interaction')
    ax.axvline(x=2.5, color='green', linestyle='--', alpha=0.5, label='H=2.5 bits threshold')

    ax.set_xlabel('Feedback Entropy H(ErrorClass) [bits]', fontsize=12)
    ax.set_ylabel('Interaction Effect (Refine - Single)', fontsize=12)
    ax.set_title('H-C1: Interaction Effect vs Feedback Diversity', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    output_path = cfg.figures_dir / "interaction_vs_entropy.png"
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    return output_path


def plot_entropy_histogram(results: dict, cfg: Config) -> Path:
    """Plot entropy distribution across conditions."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = results.get("conditions", {})
    high_entropies = [d["entropy"] for c, d in conditions.items() if "High" in c and "entropy" in d]
    low_entropies = [d["entropy"] for c, d in conditions.items() if "Low" in c and "entropy" in d]

    x = np.array([0])
    width = 0.35

    bars1 = ax.bar(x - width/2, [np.mean(high_entropies) if high_entropies else 0],
                   width, label='High Diversity', color='blue', alpha=0.7)
    bars2 = ax.bar(x + width/2, [np.mean(low_entropies) if low_entropies else 0],
                   width, label='Low Diversity', color='red', alpha=0.7)

    ax.axhline(y=2.5, color='green', linestyle='--', label='Target H=2.5')
    ax.axhline(y=1.5, color='orange', linestyle='--', label='Target H=1.5')

    ax.set_ylabel('Entropy [bits]', fontsize=12)
    ax.set_title('Feedback Entropy by Diversity Condition', fontsize=14)
    ax.set_xticks([0])
    ax.set_xticklabels(['RL Training'])
    ax.legend()

    output_path = cfg.figures_dir / "entropy_histogram.png"
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    return output_path


def create_all_figures(results: dict, cfg: Config) -> list[Path]:
    """Create all required figures."""
    figures = []

    # Required: interaction vs entropy scatter
    fig1 = plot_interaction_vs_entropy(results, cfg)
    figures.append(fig1)

    # Optional: entropy histogram
    fig2 = plot_entropy_histogram(results, cfg)
    figures.append(fig2)

    return figures
