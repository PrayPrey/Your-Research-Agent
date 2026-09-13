"""Visualization functions for H-M2: all 6 required figures (NFN encoder)."""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

logger = logging.getLogger("h-m2")

FIG_SIZE = (10, 6)
DPI = 150


def _ensure_figures_dir(figures_dir) -> Path:
    d = Path(figures_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def plot_gate_metrics_comparison(
    nfn_score: float,
    flat_mlp_score: float,
    threshold_abs: float,
    threshold_rel: float,
    figures_dir,
) -> None:
    """FR-7.1: Bar chart NFN score vs thresholds vs flat MLP."""
    fd = _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    labels = ["NFN Score", "Abs Threshold\n(0.1)", "Rel Threshold\n(0.3245)", "Flat MLP Score\n(0.6490)"]
    values = [nfn_score, threshold_abs, threshold_rel, flat_mlp_score]
    colors = ["#2196F3", "#F44336", "#FF9800", "#9E9E9E"]

    bars = ax.bar(labels, values, color=colors, alpha=0.8, width=0.5)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.4f}", ha="center", va="bottom", fontweight="bold", fontsize=9)

    gate_pass = nfn_score < threshold_abs and nfn_score < threshold_rel
    gate_str = "PASS ✓" if gate_pass else "FAIL ✗"
    ax.set_title(f"H-M2 SHOULD_WORK Gate: NFN vs MLP Sensitivity — {gate_str}", fontsize=12)
    ax.set_ylabel("Sensitivity Score")
    ax.set_ylim(0, max(values) * 1.3)
    ax.grid(True, alpha=0.3, axis="y")

    out = fd / "gate_metrics_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M2] Saved {out}")


def plot_l2_distribution_comparison(
    nfn_equiv_dists: List[float],
    nfn_random_dists: List[float],
    mlp_equiv_dists: List[float],
    mlp_random_dists: List[float],
    figures_dir,
) -> None:
    """FR-7.2: Side-by-side histograms equiv vs random L2 for NFN and MLP."""
    fd = _ensure_figures_dir(figures_dir)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=DPI)
    bins = 30

    ax1.hist(nfn_equiv_dists, bins=bins, alpha=0.6, color="#2196F3",
             label=f"NFN Equiv (μ={np.mean(nfn_equiv_dists):.3f})")
    ax1.hist(nfn_random_dists, bins=bins, alpha=0.6, color="#FF9800",
             label=f"NFN Random (μ={np.mean(nfn_random_dists):.3f})")
    ax1.set_title("NFN Encoder: L2 Distance Distribution")
    ax1.set_xlabel("L2 Distance")
    ax1.set_ylabel("Count")
    ax1.legend()

    if mlp_equiv_dists:
        ax2.hist(mlp_equiv_dists, bins=bins, alpha=0.6, color="#4CAF50",
                 label=f"MLP Equiv (μ={np.mean(mlp_equiv_dists):.3f})")
        ax2.hist(mlp_random_dists, bins=bins, alpha=0.6, color="#F44336",
                 label=f"MLP Random (μ={np.mean(mlp_random_dists):.3f})")
        ax2.set_title("Flat MLP Encoder: L2 Distance Distribution")
        ax2.set_xlabel("L2 Distance")
        ax2.set_ylabel("Count")
        ax2.legend()
    else:
        ax2.text(0.5, 0.5, "MLP data not available", ha="center", va="center",
                 transform=ax2.transAxes)
        ax2.set_title("Flat MLP Encoder: L2 Distance Distribution")

    fig.suptitle("H-M2: NFN vs MLP — Equiv/Random Pair L2 Distributions", fontsize=13)
    fig.tight_layout()
    out = fd / "l2_distribution_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M2] Saved {out}")


def plot_embedding_pca(
    embeddings: np.ndarray,
    accuracies: np.ndarray,
    equiv_pair_indices: List[tuple],
    figures_dir,
) -> None:
    """FR-7.3: PCA 2D scatter colored by accuracy; equiv pairs connected."""
    fd = _ensure_figures_dir(figures_dir)
    if embeddings.shape[0] < 4:
        logger.warning("[H-M2] Too few embeddings for PCA scatter, skipping")
        return

    pca = PCA(n_components=2)
    coords = pca.fit_transform(embeddings)

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    for i, j in equiv_pair_indices[:50]:
        if i < len(coords) and j < len(coords):
            ax.plot([coords[i, 0], coords[j, 0]], [coords[i, 1], coords[j, 1]],
                    "gray", alpha=0.25, linewidth=0.5)

    sc = ax.scatter(coords[:, 0], coords[:, 1], c=accuracies, cmap="viridis",
                    alpha=0.6, s=10)
    plt.colorbar(sc, ax=ax, label="Test Accuracy")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%})")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%})")
    ax.set_title("H-M2 NFN Embeddings (PCA) — Colored by Accuracy, Lines=Equiv Pairs")

    out = fd / "embedding_pca.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M2] Saved {out}")


def plot_training_curves(history, figures_dir) -> None:
    """FR-7.4: Loss + Spearman rho over epochs (train/val)."""
    fd = _ensure_figures_dir(figures_dir)
    epochs = list(range(1, len(history.train_loss) + 1))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=DPI)

    ax1.plot(epochs, history.train_loss, label="Train Loss", color="#2196F3")
    ax1.plot(epochs, history.val_loss, label="Val Loss", color="#F44336")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("MSE Loss")
    ax1.set_title("H-M2 NFN Training: Loss Curves")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, history.train_spearman, label="Train Spearman ρ", color="#2196F3")
    ax2.plot(epochs, history.val_spearman, label="Val Spearman ρ", color="#F44336")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Spearman ρ")
    ax2.set_title("H-M2 NFN Training: Spearman Correlation")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    out = fd / "training_curves.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M2] Saved {out}")


def plot_sensitivity_by_decile(
    nfn_decile_scores: List[float],
    mlp_decile_scores: List[float],
    figures_dir,
) -> None:
    """FR-7.5: NFN per-decile sensitivity bar chart."""
    fd = _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)
    x = list(range(len(nfn_decile_scores)))

    bars = ax.bar(x, nfn_decile_scores, color="#2196F3", alpha=0.8, label="NFN Sensitivity/Decile")
    ax.set_xlabel("Accuracy Decile")
    ax.set_ylabel("Sensitivity Score (equiv/random ratio)")
    ax.set_title("H-M2: NFN Permutation Sensitivity by Accuracy Decile")
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{i}" for i in x])
    for bar, val in zip(bars, nfn_decile_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"{val:.3f}", ha="center", va="bottom", fontsize=7)
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    out = fd / "sensitivity_by_decile.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M2] Saved {out}")


def plot_nfn_vs_mlp_decile_comparison(
    nfn_decile_scores: List[float],
    mlp_decile_scores: List[float],
    figures_dir,
) -> None:
    """FR-7.6: Grouped bar NFN vs flat MLP sensitivity per decile."""
    fd = _ensure_figures_dir(figures_dir)
    fig, ax = plt.subplots(figsize=(12, 6), dpi=DPI)
    n = len(nfn_decile_scores)
    x = np.arange(n)
    width = 0.35

    bars1 = ax.bar(x - width / 2, nfn_decile_scores, width, label="NFN Encoder",
                   color="#2196F3", alpha=0.8)
    if mlp_decile_scores:
        bars2 = ax.bar(x + width / 2, mlp_decile_scores[:n], width,
                       label="Flat MLP Encoder", color="#FF9800", alpha=0.8)

    ax.set_xlabel("Accuracy Decile")
    ax.set_ylabel("Sensitivity Score (equiv/random ratio)")
    ax.set_title("H-M2 vs H-M1: NFN vs Flat MLP Permutation Sensitivity Per Decile")
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{i}" for i in range(n)])
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    out = fd / "nfn_vs_mlp_decile_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M2] Saved {out}")
