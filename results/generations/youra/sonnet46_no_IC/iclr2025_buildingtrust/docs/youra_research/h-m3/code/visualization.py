"""Visualization module for H-M3: 5 figures from clustering results."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram

from config import (
    DIMENSIONS, PREDICTED_RLHF_SENSITIVE, PREDICTED_RLHF_INSENSITIVE,
    PRIMARY_SILHOUETTE_THRESHOLD, SECONDARY_ALIGNMENT_THRESHOLD,
    FIG_SIZE_DEFAULT, FIG_SIZE_HEATMAP, FIG_SIZE_DENDROGRAM, FIG_SIZE_MDS,
    FIG_DPI, CMAP_DIVERGING, CMAP_CLUSTER,
    FIG_GATE_METRICS, FIG_DENDROGRAM, FIG_RHO_HEATMAP,
    FIG_SILHOUETTE_COMPARISON, FIG_MDS_PROJECTION,
)


def plot_gate_metrics(results: dict, figures_dir: str) -> str:
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZE_DEFAULT)

    sil = results["silhouette_ward"]
    axes[0].bar(["Ward k=2\nSilhouette"], [sil], color=CMAP_CLUSTER[0], alpha=0.8)
    axes[0].axhline(PRIMARY_SILHOUETTE_THRESHOLD, color='red', linestyle='--', label=f'Threshold={PRIMARY_SILHOUETTE_THRESHOLD}')
    axes[0].set_ylim(0, 1)
    axes[0].set_ylabel("Silhouette Score")
    axes[0].set_title("Primary Gate")
    axes[0].legend()
    axes[0].text(0, sil + 0.02, f"{sil:.3f}", ha='center', fontsize=12, fontweight='bold')

    align = results["membership_alignment"]
    axes[1].bar(["Membership\nAlignment"], [align], color=CMAP_CLUSTER[1], alpha=0.8)
    axes[1].axhline(SECONDARY_ALIGNMENT_THRESHOLD, color='red', linestyle='--', label=f'Threshold={SECONDARY_ALIGNMENT_THRESHOLD}')
    axes[1].set_ylim(0, 4.5)
    axes[1].set_ylabel("Alignment Count (out of 4)")
    axes[1].set_title("Secondary Gate")
    axes[1].legend()
    axes[1].text(0, align + 0.05, f"{align}/4", ha='center', fontsize=12, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(figures_dir, FIG_GATE_METRICS)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
    return path


def plot_dendrogram(Z: np.ndarray, dims: list, labels: np.ndarray, figures_dir: str) -> str:
    fig, ax = plt.subplots(figsize=FIG_SIZE_DENDROGRAM)

    leaf_colors = {}
    for i, dim in enumerate(dims):
        if dim in PREDICTED_RLHF_SENSITIVE:
            leaf_colors[i + 1] = 'green'
        elif dim in PREDICTED_RLHF_INSENSITIVE:
            leaf_colors[i + 1] = 'red'
        else:
            leaf_colors[i + 1] = 'gray'

    dendrogram(Z, labels=dims, ax=ax, color_threshold=0, above_threshold_color='gray')

    # Color leaf labels
    xlbls = ax.get_xmajorticklabels()
    for lbl in xlbls:
        dim = lbl.get_text()
        if dim in PREDICTED_RLHF_SENSITIVE:
            lbl.set_color('green')
        elif dim in PREDICTED_RLHF_INSENSITIVE:
            lbl.set_color('red')
        else:
            lbl.set_color('gray')

    # Annotate 2-cluster cut
    last_merge = Z[-1, 2]
    second_last = Z[-2, 2]
    cut_height = (last_merge + second_last) / 2
    ax.axhline(cut_height, color='blue', linestyle='--', alpha=0.7, label=f'k=2 cut (h={cut_height:.3f})')

    ax.set_title("Ward Hierarchical Clustering Dendrogram\nH-M3: Trustworthiness Dimensions")
    ax.set_ylabel("Ward Distance")
    ax.legend()

    patches = [
        mpatches.Patch(color='green', label='RLHF-sensitive (predicted)'),
        mpatches.Patch(color='red', label='RLHF-insensitive (predicted)'),
        mpatches.Patch(color='gray', label='Ambiguous'),
    ]
    ax.legend(handles=patches, loc='upper right', fontsize=8)

    plt.tight_layout()
    path = os.path.join(figures_dir, FIG_DENDROGRAM)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
    return path


def plot_rho_heatmap(rho: np.ndarray, dims: list, labels: np.ndarray, figures_dir: str) -> str:
    # Reorder by cluster
    order = np.argsort(labels)
    rho_ord = rho[np.ix_(order, order)]
    dims_ord = [dims[i] for i in order]

    fig, ax = plt.subplots(figsize=FIG_SIZE_HEATMAP)
    im = sns.heatmap(
        rho_ord, ax=ax,
        xticklabels=dims_ord, yticklabels=dims_ord,
        cmap=CMAP_DIVERGING, center=0, vmin=-1, vmax=1,
        annot=True, fmt=".2f", annot_kws={"size": 8},
        linewidths=0.5,
    )

    # Cluster boundary
    cluster_sizes = [np.sum(labels[order] == c) for c in sorted(set(labels))]
    boundary = cluster_sizes[0]
    ax.axhline(boundary, color='black', linewidth=2)
    ax.axvline(boundary, color='black', linewidth=2)

    ax.set_title("Partial Spearman Correlation Matrix\nReordered by Ward Cluster (H-M3)")
    plt.tight_layout()
    path = os.path.join(figures_dir, FIG_RHO_HEATMAP)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
    return path


def plot_silhouette_comparison(results: dict, figures_dir: str) -> str:
    methods = ['Ward', 'Average', 'Complete']
    scores = [
        results["silhouette_ward"],
        results["silhouette_average"],
        results["silhouette_complete"],
    ]
    colors = [CMAP_CLUSTER[0], '#4CAF50', '#9C27B0']

    fig, ax = plt.subplots(figsize=FIG_SIZE_DEFAULT)
    bars = ax.bar(methods, scores, color=colors, alpha=0.8)
    ax.axhline(PRIMARY_SILHOUETTE_THRESHOLD, color='red', linestyle='--',
               label=f'Primary threshold={PRIMARY_SILHOUETTE_THRESHOLD}')
    ax.set_ylim(0, 1)
    ax.set_ylabel("Silhouette Score (k=2)")
    ax.set_title("Silhouette Score by Linkage Method\nH-M3: Robustness Check")
    ax.legend()

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{score:.3f}", ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(figures_dir, FIG_SILHOUETTE_COMPARISON)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
    return path


def plot_mds_projection(coords: np.ndarray, dims: list, labels: np.ndarray, figures_dir: str) -> str:
    fig, ax = plt.subplots(figsize=FIG_SIZE_MDS)

    for i, (dim, lbl) in enumerate(zip(dims, labels)):
        color = CMAP_CLUSTER[lbl]
        ax.scatter(coords[i, 0], coords[i, 1], color=color, s=150, zorder=3)
        ax.annotate(dim, (coords[i, 0], coords[i, 1]),
                    textcoords="offset points", xytext=(8, 4), fontsize=9)

    patches = [
        mpatches.Patch(color=CMAP_CLUSTER[0], label=f'Cluster 0'),
        mpatches.Patch(color=CMAP_CLUSTER[1], label=f'Cluster 1'),
    ]
    ax.legend(handles=patches)
    ax.set_xlabel("MDS Dimension 1")
    ax.set_ylabel("MDS Dimension 2")
    ax.set_title("MDS 2D Projection of Trustworthiness Dimensions\nH-M3: Cluster Visualization")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(figures_dir, FIG_MDS_PROJECTION)
    fig.savefig(path, dpi=FIG_DPI, bbox_inches='tight')
    plt.close(fig)
    return path


def generate_all_figures(results: dict, figures_dir: str) -> list:
    os.makedirs(figures_dir, exist_ok=True)
    paths = []
    paths.append(plot_gate_metrics(results, figures_dir))
    paths.append(plot_dendrogram(results["Z"], results["dims"], results["labels"], figures_dir))
    paths.append(plot_rho_heatmap(results["rho"], results["dims"], results["labels"], figures_dir))
    paths.append(plot_silhouette_comparison(results, figures_dir))
    paths.append(plot_mds_projection(results["mds_coords"], results["dims"], results["labels"], figures_dir))
    return paths
