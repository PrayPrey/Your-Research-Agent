"""H-E1: Visualization - bar chart and t-SNE."""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

from config import N_CLUSTERS, RANDOM_SEED


def plot_cluster_task_bar(
    cluster_ids: np.ndarray,
    task_labels: np.ndarray,
    task_names: list[str],
    out_path: str,
) -> None:
    """Plot per-cluster task composition as stacked bar chart."""
    n_tasks = len(task_names)
    composition = np.zeros((N_CLUSTERS, n_tasks))

    for c in range(N_CLUSTERS):
        mask = cluster_ids == c
        if mask.sum() == 0:
            continue
        for t in range(n_tasks):
            composition[c, t] = ((task_labels[mask] == t).sum())

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(N_CLUSTERS)
    bottom = np.zeros(N_CLUSTERS)

    for t in range(n_tasks):
        ax.bar(x, composition[:, t], bottom=bottom, label=task_names[t])
        bottom += composition[:, t]

    ax.set_xlabel("Cluster")
    ax.set_ylabel("Sample Count")
    ax.set_title("Per-Cluster Task Composition")
    ax.legend(loc="upper right")
    ax.set_xticks(x)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_tsne(
    embeddings: np.ndarray,
    task_labels: np.ndarray,
    task_names: list[str],
    out_path: str,
) -> None:
    """2D t-SNE projection colored by task label."""
    tsne = TSNE(n_components=2, random_state=RANDOM_SEED, perplexity=30)
    proj = tsne.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=(10, 8))

    for t, name in enumerate(task_names):
        mask = task_labels == t
        ax.scatter(proj[mask, 0], proj[mask, 1], label=name, alpha=0.6, s=20)

    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    ax.set_title("t-SNE of BERT [CLS] Embeddings by Task")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
