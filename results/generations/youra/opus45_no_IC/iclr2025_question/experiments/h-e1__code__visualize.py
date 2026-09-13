"""Visualization for H-E1 Benchmark Clustering Experiment."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_samples
from config import FIGURES_DIR, SILHOUETTE_THRESHOLD, LINKAGE_METHOD, BENCHMARKS

os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_js_heatmap(js_matrix: np.ndarray, names: list, out_path: str = None) -> None:
    """Plot 6x6 JS-divergence heatmap."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "js_heatmap.png")

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        js_matrix,
        annot=True,
        fmt=".3f",
        xticklabels=names,
        yticklabels=names,
        cmap="YlOrRd",
        square=True,
    )
    plt.title("JS-Divergence Between Benchmark Entropy Distributions")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_dendrogram(js_matrix: np.ndarray, names: list, out_path: str = None) -> None:
    """Plot hierarchical clustering dendrogram."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "dendrogram.png")

    condensed = squareform(js_matrix, checks=False)
    Z = linkage(condensed, method=LINKAGE_METHOD)

    plt.figure(figsize=(12, 6))
    dendrogram(Z, labels=names, leaf_rotation=45)
    plt.title("Benchmark Clustering Dendrogram (Ward Linkage)")
    plt.ylabel("JS-Divergence")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_entropy_violin(entropies: Dict[str, np.ndarray], out_path: str = None) -> None:
    """Plot per-benchmark entropy distribution violin plot."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "entropy_violin.png")

    data = []
    labels = []
    for name in BENCHMARKS:
        if name in entropies:
            data.extend(entropies[name].tolist())
            labels.extend([name] * len(entropies[name]))

    plt.figure(figsize=(14, 6))
    sns.violinplot(x=labels, y=data, inner="box")
    plt.xticks(rotation=45)
    plt.xlabel("Benchmark")
    plt.ylabel("Semantic Entropy")
    plt.title("Entropy Distribution per Benchmark")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_silhouette(js_matrix: np.ndarray, labels: np.ndarray, out_path: str = None) -> None:
    """Plot per-sample silhouette coefficients."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "silhouette.png")

    sample_silhouettes = silhouette_samples(js_matrix, labels, metric="precomputed")

    plt.figure(figsize=(10, 6))
    colors = plt.cm.tab10(labels - 1)
    plt.barh(range(len(sample_silhouettes)), sample_silhouettes, color=colors)
    plt.axvline(x=np.mean(sample_silhouettes), color="red", linestyle="--", label=f"Mean: {np.mean(sample_silhouettes):.3f}")
    plt.xlabel("Silhouette Coefficient")
    plt.ylabel("Sample Index")
    plt.title("Per-Sample Silhouette Coefficients")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_gate_metric(silhouette: float, threshold: float = SILHOUETTE_THRESHOLD, out_path: str = None) -> None:
    """Plot silhouette score vs threshold bar chart."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "gate_metric.png")

    passed = silhouette > threshold
    color = "green" if passed else "red"
    status = "PASS" if passed else "FAIL"

    plt.figure(figsize=(8, 6))
    bars = plt.bar(["Silhouette Score", "Threshold"], [silhouette, threshold], color=[color, "gray"])
    plt.axhline(y=threshold, color="orange", linestyle="--", linewidth=2, label=f"Threshold: {threshold}")
    plt.ylabel("Score")
    plt.title(f"Gate Metric: Silhouette > {threshold} → {status}")
    plt.ylim(0, 1)

    for bar, val in zip(bars, [silhouette, threshold]):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{val:.3f}", ha="center", fontsize=12)

    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
