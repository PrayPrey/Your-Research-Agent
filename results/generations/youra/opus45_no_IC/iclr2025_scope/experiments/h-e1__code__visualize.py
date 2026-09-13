"""Visualization suite for H-E1 experiment results."""

import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples
from pathlib import Path
from config import TASKS, COMPRESSION_CONFIGS, TASK_CATEGORIES


def plot_gate_metrics(gap_df: dict, k_star: int, significant: bool, save_path: Path):
    """Mandatory gate chart: k* value + gap criterion."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    ax1 = axes[0]
    ax1.bar(["k*"], [k_star], color="green" if k_star > 1 else "red")
    ax1.axhline(y=1, color="gray", linestyle="--", label="Threshold (k > 1)")
    ax1.set_ylabel("Optimal Clusters")
    ax1.set_title(f"Gap Statistic: k* = {k_star}")
    ax1.set_ylim(0, max(k_star + 1, 3))
    ax1.legend()

    ax2 = axes[1]
    status = "PASS" if significant else "FAIL"
    color = "green" if significant else "red"
    ax2.bar(["Gate Status"], [1], color=color)
    ax2.set_ylabel("")
    ax2.set_title(f"MUST_WORK Gate: {status}")
    ax2.set_yticks([])
    ax2.text(0, 0.5, status, ha="center", va="center", fontsize=20, fontweight="bold", color="white")

    plt.tight_layout()
    plt.savefig(save_path / "gate_metrics.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: gate_metrics.png")


def plot_gap_curve(gap_df: dict, k_star: int, save_path: Path):
    """Gap statistic curve with error bars."""
    k_values = gap_df["n_clusters"]
    gaps = gap_df["gap_value"]
    sks = gap_df["sk"]

    plt.figure(figsize=(8, 5))
    plt.errorbar(k_values, gaps, yerr=sks, marker="o", capsize=5, capthick=2)
    plt.axvline(x=k_star, color="red", linestyle="--", label=f"k* = {k_star}")
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Gap Statistic")
    plt.title("Gap Statistic vs Number of Clusters")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path / "gap_curve.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: gap_curve.png")


def plot_response_heatmap(response_matrix: np.ndarray, save_path: Path):
    """Response matrix heatmap (21 tasks x 6 configs)."""
    plt.figure(figsize=(10, 12))
    plt.imshow(response_matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1.2)
    plt.colorbar(label="Accuracy Retention")

    config_names = [c["name"] for c in COMPRESSION_CONFIGS]
    plt.xticks(range(len(config_names)), config_names, rotation=45, ha="right")
    plt.yticks(range(len(TASKS)), TASKS)

    plt.xlabel("Compression Configuration")
    plt.ylabel("Task")
    plt.title("Response Matrix: Task × Compression Config")
    plt.tight_layout()
    plt.savefig(save_path / "response_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: response_heatmap.png")


def plot_cluster_pca(response_matrix: np.ndarray, cluster_labels: dict, save_path: Path):
    """2D PCA visualization of task clusters."""
    labels = [cluster_labels[task] for task in TASKS]
    n_clusters = max(labels) + 1

    pca = PCA(n_components=2)
    coords = pca.fit_transform(response_matrix)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10", s=100)

    for i, task in enumerate(TASKS):
        plt.annotate(task, (coords[i, 0], coords[i, 1]), fontsize=8, alpha=0.7)

    plt.colorbar(scatter, label="Cluster")
    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)")
    plt.title(f"Task Clusters (k={n_clusters}) - PCA Projection")
    plt.grid(True, alpha=0.3)
    plt.savefig(save_path / "cluster_pca.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: cluster_pca.png")


def plot_silhouette(response_matrix: np.ndarray, cluster_labels: dict, save_path: Path):
    """Silhouette plot per cluster."""
    labels = np.array([cluster_labels[task] for task in TASKS])
    n_clusters = max(labels) + 1

    if n_clusters <= 1:
        plt.figure(figsize=(8, 5))
        plt.text(0.5, 0.5, "Silhouette not applicable for k=1", ha="center", va="center")
        plt.savefig(save_path / "silhouette.png", dpi=150, bbox_inches="tight")
        plt.close()
        return

    sample_silhouette = silhouette_samples(response_matrix, labels)

    plt.figure(figsize=(8, 6))
    y_lower = 10

    for i in range(n_clusters):
        cluster_silhouette = sample_silhouette[labels == i]
        cluster_silhouette.sort()
        size = cluster_silhouette.shape[0]
        y_upper = y_lower + size

        plt.fill_betweenx(np.arange(y_lower, y_upper), 0, cluster_silhouette, alpha=0.7)
        plt.text(-0.05, y_lower + 0.5 * size, str(i))
        y_lower = y_upper + 10

    avg_silhouette = sample_silhouette.mean()
    plt.axvline(x=avg_silhouette, color="red", linestyle="--", label=f"Avg: {avg_silhouette:.3f}")
    plt.xlabel("Silhouette Coefficient")
    plt.ylabel("Cluster")
    plt.title("Silhouette Plot")
    plt.legend()
    plt.savefig(save_path / "silhouette.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: silhouette.png")


def main():
    """Generate all visualizations."""
    base_dir = Path(__file__).parent.parent
    figures_dir = base_dir / "figures"
    figures_dir.mkdir(exist_ok=True)

    response_matrix = np.load(base_dir / "response_matrix.npy")
    with open(base_dir / "gap_results.json") as f:
        gap_results = json.load(f)
    with open(base_dir / "cluster_labels.json") as f:
        cluster_labels = json.load(f)

    k_star = gap_results["k_star"]
    significant = gap_results["significant"]
    gap_df = gap_results["gap_df"]

    print("Generating visualizations...")
    plot_gate_metrics(gap_df, k_star, significant, figures_dir)
    plot_gap_curve(gap_df, k_star, figures_dir)
    plot_response_heatmap(response_matrix, figures_dir)
    plot_cluster_pca(response_matrix, cluster_labels, figures_dir)
    plot_silhouette(response_matrix, cluster_labels, figures_dir)

    print(f"\nAll figures saved to: {figures_dir}")


if __name__ == "__main__":
    main()
