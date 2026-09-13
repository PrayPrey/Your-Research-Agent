import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.cluster.hierarchy import dendrogram
from pathlib import Path
from typing import List, Dict


def plot_dendrogram(
    linkage_matrix: np.ndarray,
    labels: List[str],
    optimal_k: int,
    output_path: Path
):
    plt.figure(figsize=(10, 6))
    dendrogram(linkage_matrix, labels=labels)
    plt.title(f"Hierarchical Clustering Dendrogram (optimal k={optimal_k})")
    plt.xlabel("Benchmark")
    plt.ylabel("Distance")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_silhouette_vs_k(silhouette_scores: Dict[int, float], output_path: Path):
    plt.figure(figsize=(8, 5))
    k_values = sorted(silhouette_scores.keys())
    scores = [silhouette_scores[k] for k in k_values]
    plt.plot(k_values, scores, marker='o')
    plt.axhline(y=0.5, color='r', linestyle='--', label='threshold=0.5')
    plt.xlabel("Number of clusters (k)")
    plt.ylabel("Silhouette score")
    plt.title("Silhouette Score vs Cluster Count")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_consistency_matrix(
    consistency_matrix: np.ndarray,
    labels: List[str],
    output_path: Path
):
    plt.figure(figsize=(8, 6))
    sns.heatmap(consistency_matrix, annot=True, fmt='.1f', cmap='YlGnBu',
                xticklabels=labels, yticklabels=labels, vmin=0, vmax=100)
    plt.title("Bootstrap Consistency Matrix (%)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
