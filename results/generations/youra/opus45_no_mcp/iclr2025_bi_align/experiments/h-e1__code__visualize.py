"""Visualization module for experiment results."""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
import os


def plot_gate_metric(silhouette_score: float, threshold: float, out_path: str) -> None:
    """Plot silhouette score vs gate threshold."""
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ["green" if silhouette_score > threshold else "red", "gray"]
    bars = ax.bar(["Achieved", "Threshold"], [silhouette_score, threshold], color=colors)

    ax.axhline(y=threshold, color="red", linestyle="--", label=f"Gate: {threshold}")
    ax.set_ylabel("Silhouette Score")
    ax.set_title(f"Gate Check: {'PASS' if silhouette_score > threshold else 'FAIL'}")
    ax.set_ylim(0, max(silhouette_score, threshold) * 1.2)

    for bar, val in zip(bars, [silhouette_score, threshold]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_calibration_histogram(scores: np.ndarray, out_path: str) -> None:
    """Plot histogram of calibration inversion scores."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(scores.flatten(), bins=50, edgecolor="black", alpha=0.7)
    ax.axvline(x=0.1, color="red", linestyle="--", label="Inversion threshold (0.1)")
    ax.axvline(x=0, color="gray", linestyle="-", alpha=0.5)

    ax.set_xlabel("Calibration Inversion Score")
    ax.set_ylabel("Number of Tasks")
    ax.set_title("Distribution of Calibration Inversion Scores")
    ax.legend()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cluster_scatter(scores: np.ndarray, labels: np.ndarray, out_path: str) -> None:
    """Plot scatter of tasks colored by cluster."""
    fig, ax = plt.subplots(figsize=(10, 6))

    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

    for i, label in enumerate(unique_labels):
        mask = labels == label
        ax.scatter(np.where(mask)[0], scores[mask].flatten(),
                   c=[colors[i]], label=f"Cluster {label}", alpha=0.6, s=20)

    ax.set_xlabel("Task Index")
    ax.set_ylabel("Calibration Inversion Score")
    ax.set_title("Tasks Colored by Cluster Membership")
    ax.legend()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cluster_profiles(scores: np.ndarray, labels: np.ndarray, out_path: str) -> None:
    """Plot boxplot of calibration scores per cluster."""
    fig, ax = plt.subplots(figsize=(10, 6))

    unique_labels = sorted(np.unique(labels))
    data = [scores[labels == l].flatten() for l in unique_labels]

    bp = ax.boxplot(data, labels=[f"Cluster {l}\n(n={len(d)})" for l, d in zip(unique_labels, data)])
    ax.set_xlabel("Cluster")
    ax.set_ylabel("Calibration Inversion Score")
    ax.set_title("Calibration Score Distribution per Cluster")
    ax.axhline(y=0.1, color="red", linestyle="--", alpha=0.5, label="Inversion threshold")
    ax.legend()

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_cross_model_agreement(labels_by_model: Dict[str, np.ndarray], out_path: str) -> None:
    """Plot heatmap of cluster label agreement across models."""
    fig, ax = plt.subplots(figsize=(10, 8))

    models = list(labels_by_model.keys())
    n_models = len(models)
    agreement_matrix = np.zeros((n_models, n_models))

    for i, m1 in enumerate(models):
        for j, m2 in enumerate(models):
            l1, l2 = labels_by_model[m1], labels_by_model[m2]
            agreement = np.mean(l1 == l2)
            agreement_matrix[i, j] = agreement

    im = ax.imshow(agreement_matrix, cmap="YlGn", vmin=0, vmax=1)

    ax.set_xticks(range(n_models))
    ax.set_yticks(range(n_models))
    short_names = [m.split("/")[-1][:15] for m in models]
    ax.set_xticklabels(short_names, rotation=45, ha="right")
    ax.set_yticklabels(short_names)

    for i in range(n_models):
        for j in range(n_models):
            ax.text(j, i, f"{agreement_matrix[i, j]:.2f}", ha="center", va="center")

    ax.set_title("Cross-Model Cluster Agreement")
    plt.colorbar(im, ax=ax, label="Agreement Rate")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
