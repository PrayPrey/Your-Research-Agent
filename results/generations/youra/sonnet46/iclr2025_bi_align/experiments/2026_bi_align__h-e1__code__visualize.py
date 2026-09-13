"""
visualize.py - Visualization functions for h-e1 experiment.

Generates 6 figures saved to figures/ at 300 DPI.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from typing import Dict


def _ensure_figures_dir(figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)


def plot_gate_metrics(results: Dict, figures_dir: str) -> None:
    """Two-panel figure: C_sem bar with CI + grouped cosine bars.

    Left: C_sem bar with error bar (CI) + dashed zero line.
    Right: Three grouped bars for actual/topic/random cosine means.
    Colors: actual=blue, topic=orange, random=grey, C_sem=green.
    """
    _ensure_figures_dir(figures_dir)

    c_sem = results["c_sem"]
    c_sem_ci = results["c_sem_ci"]
    cos_actual = results["cos_actual_mean"]
    cos_topic = results["cos_topic_mean"]
    cos_random = results["cos_random_mean"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left panel: C_sem with CI
    ci_lower = float(c_sem) - float(c_sem_ci[0])
    ci_upper = float(c_sem_ci[1]) - float(c_sem)
    ax1.bar(["C_sem"], [c_sem], color="green", alpha=0.7, width=0.4)
    ax1.errorbar(
        ["C_sem"], [c_sem],
        yerr=[[ci_lower], [ci_upper]],
        fmt="none", color="black", capsize=8, linewidth=2
    )
    ax1.axhline(0, color="black", linestyle="--", linewidth=1.5)
    ax1.set_ylabel("C_sem")
    ax1.set_title("Semantic Accommodation Index (C_sem)")
    text_y = float(c_sem) * 1.1 if abs(float(c_sem)) > 1e-6 else 0.001
    ax1.text(0, text_y, f"C_sem={c_sem:.4f}", ha="center", fontsize=10)

    # Right panel: grouped cosine similarity bars
    categories = ["cos_actual", "cos_topic", "cos_random"]
    values = [cos_actual, cos_topic, cos_random]
    colors = ["blue", "orange", "grey"]
    bars = ax2.bar(categories, values, color=colors, alpha=0.7)
    ax2.set_ylabel("Mean Cosine Similarity")
    ax2.set_title("Cosine Similarities by Condition")
    for bar, val in zip(bars, values):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.001,
            f"{val:.4f}", ha="center", va="bottom", fontsize=9
        )

    plt.tight_layout()
    path = os.path.join(figures_dir, "gate_metrics.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_partner_specificity(results: Dict, figures_dir: str) -> None:
    """Bar chart of 3 cosine similarity levels."""
    _ensure_figures_dir(figures_dir)

    categories = ["Actual (A_t)", "Topic-matched", "Random shuffle"]
    values = [
        results["cos_actual_mean"],
        results["cos_topic_mean"],
        results["cos_random_mean"],
    ]
    colors = ["blue", "orange", "grey"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(categories, values, color=colors, alpha=0.8)
    ax.set_ylabel("Mean Cosine Similarity with H_{t+1}")
    ax.set_title("Partner Specificity: Cosine Similarity Levels")
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.001,
            f"{val:.4f}", ha="center", va="bottom", fontsize=10
        )

    plt.tight_layout()
    path = os.path.join(figures_dir, "partner_specificity.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_bootstrap_dist(bootstrap_samples: np.ndarray, figures_dir: str) -> None:
    """Histogram of bootstrap C_sem distribution."""
    _ensure_figures_dir(figures_dir)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(bootstrap_samples, bins=50, color="green", alpha=0.7, edgecolor="white")
    ax.axvline(0, color="red", linestyle="--", linewidth=2, label="Zero")
    ax.axvline(
        np.percentile(bootstrap_samples, 2.5),
        color="orange", linestyle="--", linewidth=1.5, label="95% CI"
    )
    ax.axvline(
        np.percentile(bootstrap_samples, 97.5),
        color="orange", linestyle="--", linewidth=1.5
    )
    ax.set_xlabel("Bootstrap C_sem")
    ax.set_ylabel("Count")
    ax.set_title("Bootstrap Distribution of C_sem")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "bootstrap_dist.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_cosine_distributions(
    cos_actual: np.ndarray,
    cos_topic: np.ndarray,
    cos_random: np.ndarray,
    figures_dir: str,
) -> None:
    """KDE overlay of cosine similarity distributions."""
    _ensure_figures_dir(figures_dir)

    fig, ax = plt.subplots(figsize=(8, 5))
    for arr, color, label in [
        (cos_actual, "blue", "Actual"),
        (cos_topic, "orange", "Topic-matched"),
        (cos_random, "grey", "Random"),
    ]:
        try:
            kde = gaussian_kde(arr)
            x_range = np.linspace(arr.min() - 0.1, arr.max() + 0.1, 200)
            ax.plot(x_range, kde(x_range), color=color, label=label, linewidth=2)
            ax.fill_between(x_range, kde(x_range), alpha=0.2, color=color)
        except Exception:
            ax.hist(arr, bins=50, color=color, alpha=0.4, label=label, density=True)

    ax.set_xlabel("Cosine Similarity")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of Cosine Similarities")
    ax.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "cosine_distributions.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_residualization_check(
    cos_dict_before: Dict,
    cos_dict_after: Dict,
    figures_dir: str,
) -> None:
    """Before/after residualization scatter for cos_actual."""
    _ensure_figures_dir(figures_dir)

    before = cos_dict_before.get("cos_actual", np.array([]))
    after = cos_dict_after.get("cos_actual", np.array([]))

    if len(before) == 0 or len(after) == 0:
        return

    # Sample up to 2000 points for plot readability
    n = min(len(before), 2000)
    idx = np.random.choice(len(before), n, replace=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.scatter(before[idx], after[idx], alpha=0.3, s=5, color="blue")
    ax1.set_xlabel("Before Residualization")
    ax1.set_ylabel("After Residualization")
    ax1.set_title("Cos_actual: Before vs After Residualization")

    ax2.hist(before[idx], bins=50, alpha=0.5, label="Before", color="blue")
    ax2.hist(after[idx], bins=50, alpha=0.5, label="After", color="orange")
    ax2.set_xlabel("Cosine Similarity")
    ax2.set_ylabel("Count")
    ax2.set_title("Distribution Change from Residualization")
    ax2.legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "residualization_check.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_knn_quality(prompt_embeddings: np.ndarray, figures_dir: str) -> None:
    """KNN quality visualization: distribution of nearest neighbor distances."""
    _ensure_figures_dir(figures_dir)

    from sklearn.neighbors import NearestNeighbors

    # Sample for speed
    n = min(len(prompt_embeddings), 2000)
    idx = np.random.choice(len(prompt_embeddings), n, replace=False)
    sample = prompt_embeddings[idx]

    nn = NearestNeighbors(n_neighbors=6, metric="cosine", n_jobs=1)
    nn.fit(sample)
    distances, _ = nn.kneighbors(sample)

    # distances[:, 0] is self (0), use 1: for actual neighbors
    neighbor_dists = distances[:, 1:].flatten()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(neighbor_dists, bins=50, color="purple", alpha=0.7)
    ax.set_xlabel("Cosine Distance to Nearest Neighbor")
    ax.set_ylabel("Count")
    ax.set_title(f"KNN Quality (k=5, n={n} samples)\nMean dist={neighbor_dists.mean():.4f}")

    plt.tight_layout()
    path = os.path.join(figures_dir, "knn_quality.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
