"""
H-E2 Visualization: MST and bootstrap figures.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import networkx as nx
from typing import Dict, List

DPI = 300
COLOR_RLHF_SENSITIVE = "tomato"
COLOR_RLHF_INSENSITIVE = "steelblue"
COLOR_LEAF_HIGHLIGHT = "gold"
COLOR_EDGE_DEFAULT = "gray"
COLOR_MST_EDGE_OVERLAY = "black"

MST_MIN_SET_THRESHOLD = 4
BOOTSTRAP_STABILITY_THRESHOLD = 0.90

FIG_SIZES = {
    "gate_bar": (8, 5),
    "mst_graph": (8, 7),
    "bootstrap_heatmap": (8, 7),
    "distance_heatmap": (8, 7),
    "mst_comparison": (14, 6),
}

HEATMAP_CMAP = "YlOrRd"

# H-E1 cluster membership (from H-E1 results: RLHF-sensitive = safety, machine_ethics, truthfulness, fairness, privacy; insensitive = robustness)
RLHF_SENSITIVE_DIMS = {"safety", "machine_ethics", "truthfulness", "fairness", "privacy"}


def _dim_color(dim: str) -> str:
    return COLOR_RLHF_SENSITIVE if dim in RLHF_SENSITIVE_DIMS else COLOR_RLHF_INSENSITIVE


def plot_gate_bar(results: Dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=FIG_SIZES["gate_bar"])
    metrics = [results["mst_min_set_size"], results["bootstrap_topology_stability"]]
    thresholds = [MST_MIN_SET_THRESHOLD, BOOTSTRAP_STABILITY_THRESHOLD]
    labels = ["MST Min Set Size\n(threshold ≤4)", "Bootstrap Topology\nStability (threshold ≥0.90)"]
    colors_bar = ["tomato" if metrics[0] <= thresholds[0] else "steelblue",
                  "tomato" if metrics[1] >= thresholds[1] else "steelblue"]

    bars = ax.bar(labels, metrics, color=colors_bar, alpha=0.8)
    ax.axhline(thresholds[0], color="red", linestyle="--", linewidth=1.5, label="Threshold (min_set<=4)", xmin=0, xmax=0.5)
    ax.axhline(thresholds[1], color="red", linestyle="--", linewidth=1.5, label="Threshold (stability>=0.90)", xmin=0.5, xmax=1.0)

    for bar, val in zip(bars, metrics):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, f"{val:.3f}",
                ha="center", va="bottom", fontsize=12, fontweight="bold")

    gate_str = "PASS" if results["gate_passed"] else "FAIL"
    ax.set_title(f"H-E2 Gate Metrics — {gate_str}", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(max(metrics) * 1.3, 1.1))
    ax.set_ylabel("Value")
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_mst_graph(results: Dict, dim_names: List[str], out_path: str) -> None:
    G = nx.Graph()
    G.add_nodes_from(dim_names)
    for u, v, w in results["mst_edges"]:
        G.add_edge(u, v, weight=w)

    leaves = set(results["mst_leaves"])
    node_colors = [COLOR_LEAF_HIGHLIGHT if n in leaves else _dim_color(n) for n in G.nodes()]

    fig, ax = plt.subplots(figsize=FIG_SIZES["mst_graph"])
    pos = nx.kamada_kawai_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=COLOR_EDGE_DEFAULT, width=2, ax=ax)
    edge_labels = {(u, v): f"{w:.3f}" for u, v, w in results["mst_edges"]}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, ax=ax)

    patches = [
        mpatches.Patch(color=COLOR_RLHF_SENSITIVE, label="RLHF-sensitive"),
        mpatches.Patch(color=COLOR_RLHF_INSENSITIVE, label="RLHF-insensitive"),
        mpatches.Patch(color=COLOR_LEAF_HIGHLIGHT, label="Leaf node"),
    ]
    ax.legend(handles=patches, loc="upper right", fontsize=8)
    ax.set_title("H-E2 Partial Spearman MST (Minimum Evaluation Set)", fontsize=12)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_bootstrap_heatmap(results: Dict, dim_names: List[str], out_path: str) -> None:
    n = len(dim_names)
    freq_matrix = np.zeros((n, n))
    edge_freqs = results["bootstrap_edge_frequencies"]
    dim_idx = {d: i for i, d in enumerate(dim_names)}

    for key, freq in edge_freqs.items():
        parts = key.split("--")
        if len(parts) == 2 and parts[0] in dim_idx and parts[1] in dim_idx:
            i, j = dim_idx[parts[0]], dim_idx[parts[1]]
            freq_matrix[i, j] = freq
            freq_matrix[j, i] = freq

    fig, ax = plt.subplots(figsize=FIG_SIZES["bootstrap_heatmap"])
    sns.heatmap(freq_matrix, xticklabels=dim_names, yticklabels=dim_names,
                cmap=HEATMAP_CMAP, vmin=0, vmax=1, annot=True, fmt=".2f",
                linewidths=0.5, ax=ax)

    # Bold MST edges
    for u, v, _ in results["mst_edges"]:
        if u in dim_idx and v in dim_idx:
            i, j = dim_idx[u], dim_idx[v]
            for (r, c) in [(i, j), (j, i)]:
                ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=False,
                                           edgecolor=COLOR_MST_EDGE_OVERLAY, lw=2.5))

    ax.set_title("Bootstrap Edge Frequency (MST edges in bold)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_distance_heatmap(results: Dict, rho_partial: np.ndarray, dim_names: List[str], out_path: str) -> None:
    dist_matrix = 1 - np.abs(rho_partial)
    np.fill_diagonal(dist_matrix, 0)

    dim_idx = {d: i for i, d in enumerate(dim_names)}
    fig, ax = plt.subplots(figsize=FIG_SIZES["distance_heatmap"])
    sns.heatmap(dist_matrix, xticklabels=dim_names, yticklabels=dim_names,
                cmap=HEATMAP_CMAP, vmin=0, vmax=1, annot=True, fmt=".3f",
                linewidths=0.5, ax=ax)

    for u, v, _ in results["mst_edges"]:
        if u in dim_idx and v in dim_idx:
            i, j = dim_idx[u], dim_idx[v]
            for (r, c) in [(i, j), (j, i)]:
                ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=False,
                                           edgecolor=COLOR_MST_EDGE_OVERLAY, lw=2.5))

    ax.set_title("Distance Matrix d=1-|ρ_partial| (MST edges in bold)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def plot_mst_comparison(results: Dict, dim_names: List[str], out_path: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=FIG_SIZES["mst_comparison"])

    partial_edges = set(frozenset({u, v}) for u, v, _ in results["mst_edges"])
    raw_edges = set(frozenset({u, v}) for u, v in results["raw_mst_edges"])

    def draw_mst(ax, edges, title, highlight_edges=None):
        G = nx.Graph()
        G.add_nodes_from(dim_names)
        for e in edges:
            u, v = list(e)
            G.add_edge(u, v)
        pos = nx.kamada_kawai_layout(G)
        node_colors = [_dim_color(n) for n in G.nodes()]
        edge_colors = []
        for u, v in G.edges():
            e = frozenset({u, v})
            if highlight_edges and e in highlight_edges:
                edge_colors.append("red")
            else:
                edge_colors.append(COLOR_EDGE_DEFAULT)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=600, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2, ax=ax)
        ax.set_title(title, fontsize=10)
        ax.axis("off")

    diff_edges = raw_edges.symmetric_difference(partial_edges)
    draw_mst(axes[0], raw_edges, "Raw Spearman MST (baseline)", highlight_edges=diff_edges)
    draw_mst(axes[1], partial_edges, "Partial Spearman MST (proposed)", highlight_edges=diff_edges)

    fig.suptitle("MST Comparison: Raw vs Partial Spearman (red = different edges)", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)


def visualize_all(results: Dict, rho_partial: np.ndarray, dim_names: List[str], figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    plot_gate_bar(results, os.path.join(figures_dir, "gate_bar.png"))
    plot_mst_graph(results, dim_names, os.path.join(figures_dir, "mst_graph.png"))
    plot_bootstrap_heatmap(results, dim_names, os.path.join(figures_dir, "bootstrap_heatmap.png"))
    plot_distance_heatmap(results, rho_partial, dim_names, os.path.join(figures_dir, "distance_heatmap.png"))
    plot_mst_comparison(results, dim_names, os.path.join(figures_dir, "mst_comparison.png"))
