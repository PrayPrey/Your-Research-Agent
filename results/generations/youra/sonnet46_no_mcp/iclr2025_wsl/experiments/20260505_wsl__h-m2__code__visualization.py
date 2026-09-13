"""Visualization functions for H-E1 orbit analysis results."""
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import ExperimentConfig, VisualizationConfig


def plot_gate_metrics(
    orbit_proportion: float,
    per_decile: Dict[int, float],
    threshold: float,
    save_path: Path,
    vis_cfg: VisualizationConfig = None,
) -> None:
    """Bar chart: overall orbit proportion vs threshold, with per-decile bars."""
    vis_cfg = vis_cfg or VisualizationConfig()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=vis_cfg.dpi)

    # Left: overall
    ax = axes[0]
    color = "green" if orbit_proportion > threshold else "red"
    ax.bar(["Overall"], [orbit_proportion], color=color, alpha=0.8)
    ax.axhline(y=threshold, color="black", linestyle="--", label=f"Threshold={threshold}")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Orbit Candidate Proportion")
    ax.set_title("H-E1 Gate Metrics: Overall")
    ax.legend()

    # Right: per-decile
    ax2 = axes[1]
    deciles = sorted(per_decile.keys())
    vals = [per_decile[d] for d in deciles]
    colors = ["green" if v > threshold else "red" for v in vals]
    ax2.bar(deciles, vals, color=colors, alpha=0.8)
    ax2.axhline(y=threshold, color="black", linestyle="--", label=f"Threshold={threshold}")
    ax2.set_xlabel("Accuracy Decile")
    ax2.set_ylabel("Orbit Candidate Proportion")
    ax2.set_title("H-E1 Gate Metrics: Per Decile")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=vis_cfg.dpi, bbox_inches="tight")
    plt.close()


def plot_cosine_dist_histogram(
    distances: List[Dict[str, Any]],
    save_path: Path,
    threshold: float = 0.1,
    vis_cfg: VisualizationConfig = None,
) -> None:
    """Histogram of cosine distances colored by decile."""
    vis_cfg = vis_cfg or VisualizationConfig()
    fig, ax = plt.subplots(figsize=vis_cfg.figure_size, dpi=vis_cfg.dpi)

    cmap = plt.get_cmap("tab10")
    for d in range(10):
        dists = [x["cosine_dist"] for x in distances if x["decile"] == d]
        if dists:
            ax.hist(dists, bins=20, alpha=0.5, color=cmap(d), label=f"Decile {d}")

    ax.axvline(x=threshold, color="black", linestyle="--", label=f"Threshold={threshold}")
    ax.set_xlabel("Cosine Distance")
    ax.set_ylabel("Count")
    ax.set_title("H-E1: Cosine Distance Distribution by Decile")
    ax.legend(fontsize=7, ncol=2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=vis_cfg.dpi, bbox_inches="tight")
    plt.close()


def plot_acc_vs_distance(
    pairs: List[Tuple],
    distances: List[Dict[str, Any]],
    save_path: Path,
    threshold: float = 0.1,
    vis_cfg: VisualizationConfig = None,
) -> None:
    """Scatter: |delta_acc| vs cosine_dist for all pairs, colored by decile."""
    vis_cfg = vis_cfg or VisualizationConfig()
    fig, ax = plt.subplots(figsize=vis_cfg.figure_size, dpi=vis_cfg.dpi)

    cmap = plt.get_cmap("tab10")
    for d in range(10):
        paired = [(p, dist) for p, dist in zip(pairs, distances) if dist["decile"] == d]
        if paired:
            delta_accs = [abs(p[0]["test_accuracy"] - p[1]["test_accuracy"]) for p, _ in paired]
            dists = [dist["cosine_dist"] for _, dist in paired]
            ax.scatter(dists, delta_accs, c=[cmap(d)] * len(dists), alpha=0.5, s=15, label=f"D{d}")

    ax.axvline(x=threshold, color="black", linestyle="--", label=f"Threshold={threshold}")
    ax.set_xlabel("Cosine Distance")
    ax.set_ylabel("|Δ Accuracy|")
    ax.set_title("H-E1: Accuracy Difference vs Weight Distance")
    ax.legend(fontsize=7, ncol=2)

    plt.tight_layout()
    plt.savefig(save_path, dpi=vis_cfg.dpi, bbox_inches="tight")
    plt.close()


def plot_per_decile_proportion(
    per_decile: Dict[int, float],
    threshold: float,
    save_path: Path,
    vis_cfg: VisualizationConfig = None,
) -> None:
    """Bar chart: orbit proportion per accuracy decile."""
    vis_cfg = vis_cfg or VisualizationConfig()
    fig, ax = plt.subplots(figsize=vis_cfg.figure_size, dpi=vis_cfg.dpi)

    deciles = sorted(per_decile.keys())
    vals = [per_decile[d] for d in deciles]
    colors = ["green" if v > threshold else "red" for v in vals]
    ax.bar(deciles, vals, color=colors, alpha=0.8)
    ax.axhline(y=threshold, color="black", linestyle="--", label=f"Threshold={threshold}")
    ax.set_xlabel("Accuracy Decile")
    ax.set_ylabel("Orbit Candidate Proportion")
    ax.set_title("H-E1: Per-Decile Orbit Proportion")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=vis_cfg.dpi, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    distances: List[Dict[str, Any]],
    pairs: List[Tuple],
    orbit_proportion: float,
    per_decile: Dict[int, float],
    cfg: ExperimentConfig,
    vis_cfg: VisualizationConfig = None,
) -> None:
    """Generate all 4 figures and save to cfg.figures_dir."""
    vis_cfg = vis_cfg or VisualizationConfig()
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    plot_gate_metrics(
        orbit_proportion, per_decile, cfg.cosine_dist_threshold,
        cfg.figures_dir / "gate_metrics.png", vis_cfg
    )
    plot_cosine_dist_histogram(
        distances, cfg.figures_dir / "cosine_dist_histogram.png",
        cfg.cosine_dist_threshold, vis_cfg
    )
    plot_acc_vs_distance(
        pairs, distances, cfg.figures_dir / "acc_vs_distance.png",
        cfg.cosine_dist_threshold, vis_cfg
    )
    plot_per_decile_proportion(
        per_decile, cfg.orbit_proportion_gate,
        cfg.figures_dir / "per_decile_proportion.png", vis_cfg
    )
