"""Visualization functions for H-M1: all 5 required figures."""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

logger = logging.getLogger("h-m1")

FIG_SIZE = (10, 6)
DPI = 150


def _ensure_figures_dir(cfg) -> Path:
    d = Path(cfg.figures_dir)
    d.mkdir(parents=True, exist_ok=True)
    return d


def plot_gate_metrics(
    sensitivity_score: float,
    spearman_rho: float,
    cfg,
) -> None:
    """Bar chart: sensitivity_score vs 0.3 threshold, Spearman rho vs 0.5 target."""
    figures_dir = _ensure_figures_dir(cfg)
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    labels = ["Sensitivity Score", "Spearman ρ"]
    values = [sensitivity_score, spearman_rho]
    thresholds = [cfg.sensitivity_gate, cfg.spearman_target]
    colors = ["#2196F3" if v >= t else "#F44336" for v, t in zip(values, thresholds)]

    bars = ax.bar(labels, values, color=colors, alpha=0.8, width=0.4)
    for t, x in zip(thresholds, [0, 1]):
        ax.axhline(y=t, xmin=x / 2, xmax=(x + 1) / 2, color="black", linewidth=2,
                   linestyle="--", label=f"Threshold={t}")

    ax.set_ylim(0, max(max(values) * 1.3, 1.0))
    ax.set_ylabel("Value")
    ax.set_title("H-M1 Gate Metrics: Sensitivity Score & Spearman ρ")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontweight="bold")

    gate_str = "PASS ✓" if sensitivity_score > cfg.sensitivity_gate else "FAIL ✗"
    ax.set_title(f"H-M1 Gate Metrics — Gate: {gate_str}")
    ax.legend()
    out = figures_dir / "gate_metrics.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M1] Saved {out}")


def plot_l2_distribution(
    equiv_dists: List[float],
    random_dists: List[float],
    cfg,
) -> None:
    """Histogram: equiv-pair L2 vs random-pair L2 overlaid."""
    figures_dir = _ensure_figures_dir(cfg)
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    bins = 30
    ax.hist(equiv_dists, bins=bins, alpha=0.6, color="#2196F3", label=f"Equiv pairs (n={len(equiv_dists)})")
    ax.hist(random_dists, bins=bins, alpha=0.6, color="#FF9800", label=f"Random pairs (n={len(random_dists)})")

    ax.axvline(np.mean(equiv_dists), color="#1565C0", linewidth=2, linestyle="--",
               label=f"Mean equiv={np.mean(equiv_dists):.3f}")
    ax.axvline(np.mean(random_dists), color="#E65100", linewidth=2, linestyle="--",
               label=f"Mean random={np.mean(random_dists):.3f}")

    ax.set_xlabel("L2 Distance")
    ax.set_ylabel("Count")
    ax.set_title("H-M1: L2 Distance Distribution — Equiv vs Random Pairs")
    ax.legend()
    out = figures_dir / "l2_distance_distribution.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M1] Saved {out}")


def plot_training_curve(history, cfg) -> None:
    """Line chart: train/val loss + Spearman rho over epochs."""
    figures_dir = _ensure_figures_dir(cfg)
    epochs = list(range(1, len(history.train_loss) + 1))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=DPI)

    ax1.plot(epochs, history.train_loss, label="Train Loss", color="#2196F3")
    ax1.plot(epochs, history.val_loss, label="Val Loss", color="#F44336")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("MSE Loss")
    ax1.set_title("H-M1 Training: Loss Curves")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, history.train_spearman, label="Train Spearman ρ", color="#2196F3")
    ax2.plot(epochs, history.val_spearman, label="Val Spearman ρ", color="#F44336")
    ax2.axhline(y=cfg.spearman_target, color="green", linestyle="--",
                label=f"Target ρ={cfg.spearman_target}")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Spearman ρ")
    ax2.set_title("H-M1 Training: Spearman Correlation")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    out = figures_dir / "training_curve.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M1] Saved {out}")


def plot_sensitivity_by_decile(
    decile_scores: List[float],
    cfg,
) -> None:
    """Bar chart: mean equiv L2 per accuracy decile (10 bars)."""
    figures_dir = _ensure_figures_dir(cfg)
    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    x = list(range(len(decile_scores)))
    colors = ["#2196F3" if s > cfg.sensitivity_gate else "#FF9800" for s in decile_scores]
    bars = ax.bar(x, decile_scores, color=colors, alpha=0.8)

    ax.axhline(y=cfg.sensitivity_gate, color="red", linestyle="--",
               label=f"Gate threshold={cfg.sensitivity_gate}")
    ax.set_xlabel("Accuracy Decile")
    ax.set_ylabel("Mean Equiv L2 Distance")
    ax.set_title("H-M1: Permutation Sensitivity by Accuracy Decile")
    ax.set_xticks(x)
    ax.set_xticklabels([f"D{i}" for i in x])
    ax.legend()
    for bar, val in zip(bars, decile_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    out = figures_dir / "sensitivity_by_decile.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M1] Saved {out}")


def plot_embedding_scatter(
    embeddings: np.ndarray,
    accuracies: np.ndarray,
    equiv_pair_indices: List[Tuple[int, int]],
    cfg,
    method: str = "pca",
) -> None:
    """2D PCA scatter colored by accuracy; lines connecting equiv pairs."""
    figures_dir = _ensure_figures_dir(cfg)

    # Reduce to 2D
    n_components = min(2, embeddings.shape[1], embeddings.shape[0])
    if embeddings.shape[0] < 2:
        logger.warning("[H-M1] Too few embeddings for scatter plot, skipping")
        return

    pca = PCA(n_components=2)
    coords = pca.fit_transform(embeddings)  # [N, 2]

    fig, ax = plt.subplots(figsize=FIG_SIZE, dpi=DPI)

    # Draw equiv pair connections (sample up to 50)
    for i, j in equiv_pair_indices[:50]:
        if i < len(coords) and j < len(coords):
            ax.plot([coords[i, 0], coords[j, 0]], [coords[i, 1], coords[j, 1]],
                    "gray", alpha=0.3, linewidth=0.5)

    sc = ax.scatter(coords[:, 0], coords[:, 1], c=accuracies, cmap="viridis",
                    alpha=0.6, s=10)
    plt.colorbar(sc, ax=ax, label="Test Accuracy")
    ax.set_xlabel(f"PCA Component 1 (var={pca.explained_variance_ratio_[0]:.2%})")
    ax.set_ylabel(f"PCA Component 2 (var={pca.explained_variance_ratio_[1]:.2%})")
    ax.set_title("H-M1: Embedding Space (PCA) — Colored by Accuracy, Lines=Equiv Pairs")

    out = figures_dir / "embedding_scatter.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"[H-M1] Saved {out}")
