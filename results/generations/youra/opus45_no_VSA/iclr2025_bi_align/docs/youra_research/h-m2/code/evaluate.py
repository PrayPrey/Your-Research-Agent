import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGURES_DIR = "figures"
DISAGREEMENT_THRESHOLD = 0.20
PARTIAL_THRESHOLD = 0.10


def ensure_figures_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_gate_bar(disagreement_rate, out_path):
    """Bar chart showing disagreement rate vs threshold."""
    ensure_figures_dir()
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.bar(["Disagreement Rate"], [disagreement_rate], color="steelblue")
    ax.axhline(y=DISAGREEMENT_THRESHOLD, color="green", linestyle="--", label=f"PASS threshold ({DISAGREEMENT_THRESHOLD})")
    ax.axhline(y=PARTIAL_THRESHOLD, color="orange", linestyle="--", label=f"PARTIAL threshold ({PARTIAL_THRESHOLD})")

    ax.set_ylabel("Rate")
    ax.set_ylim(0, max(0.5, disagreement_rate * 1.2))
    ax.legend()
    ax.set_title("BAI-Reward Disagreement Rate")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_scatter_quadrants(bai_z, reward_z, q_bounds, out_path):
    """Scatter plot with quadrant boundaries."""
    ensure_figures_dir()
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(bai_z, reward_z, alpha=0.3, s=10)
    ax.axvline(x=q_bounds["q25_bai"], color="gray", linestyle=":", alpha=0.7)
    ax.axvline(x=q_bounds["q75_bai"], color="gray", linestyle=":", alpha=0.7)
    ax.axhline(y=q_bounds["q25_rw"], color="gray", linestyle=":", alpha=0.7)
    ax.axhline(y=q_bounds["q75_rw"], color="gray", linestyle=":", alpha=0.7)

    ax.set_xlabel("BAI (z-score)")
    ax.set_ylabel("Reward (z-score)")
    ax.set_title("BAI vs Reward Scores with Quartile Boundaries")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_density_heatmap(bai_z, reward_z, out_path):
    """2D histogram heatmap."""
    ensure_figures_dir()
    fig, ax = plt.subplots(figsize=(8, 6))

    h = ax.hist2d(bai_z, reward_z, bins=50, cmap="viridis")
    plt.colorbar(h[3], ax=ax, label="Count")

    ax.set_xlabel("BAI (z-score)")
    ax.set_ylabel("Reward (z-score)")
    ax.set_title("BAI vs Reward Density")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_distributions(bai_scores, reward_scores, out_path):
    """Side-by-side histograms."""
    ensure_figures_dir()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].hist(bai_scores, bins=50, color="steelblue", alpha=0.7)
    axes[0].set_xlabel("BAI Score")
    axes[0].set_ylabel("Count")
    axes[0].set_title("BAI Score Distribution")

    axes[1].hist(reward_scores, bins=50, color="coral", alpha=0.7)
    axes[1].set_xlabel("Reward Score")
    axes[1].set_ylabel("Count")
    axes[1].set_title("Reward Score Distribution")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def top_disagreement_examples(responses, bai_z, reward_z, n=10):
    """Get top-n disagreement examples."""
    diff = np.abs(bai_z - reward_z)
    indices = np.argsort(diff)[::-1][:n]

    examples = []
    for idx in indices:
        examples.append({
            "response": responses[idx][:200] + "..." if len(responses[idx]) > 200 else responses[idx],
            "bai_z": float(bai_z[idx]),
            "reward_z": float(reward_z[idx]),
            "diff": float(diff[idx]),
        })

    return examples
