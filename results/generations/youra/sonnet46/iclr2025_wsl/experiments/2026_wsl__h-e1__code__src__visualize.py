"""Visualization utilities for h-e1 experiment."""
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__)


def plot_delta_rho_bar(
    flat_mlp_delta_rho: float,
    nft_delta_rho: float,
    save_path: str,
) -> None:
    """Bar chart of delta_rho for both models with threshold lines.

    Parameters
    ----------
    flat_mlp_delta_rho : float
        Delta rho for flat-MLP encoder.
    nft_delta_rho : float
        Delta rho for NFT encoder.
    save_path : str
        Path to save the figure.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    models = ["Flat-MLP", "NFT"]
    values = [flat_mlp_delta_rho, nft_delta_rho]
    colors = ["#e74c3c", "#3498db"]

    bars = ax.bar(models, values, color=colors, alpha=0.8, width=0.4)

    # Threshold lines
    ax.axhline(y=0.10, color="#e74c3c", linestyle="--", linewidth=1.5,
               label="Flat-MLP threshold (0.10)")
    ax.axhline(y=0.02, color="#3498db", linestyle="--", linewidth=1.5,
               label="NFT threshold (0.02)")

    # Value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            bar.get_height() + 0.003,
            f"{val:.4f}",
            ha="center",
            va="bottom",
            fontsize=11,
        )

    ax.set_ylabel("Delta Rho (rho_s0 - rho_s1)", fontsize=12)
    ax.set_title("Permutation Robustness: Delta Rho by Encoder", fontsize=13)
    ax.legend(fontsize=10)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved delta_rho bar chart to {save_path}")


def plot_rho_vs_severity(
    flat_rho_by_severity: dict,
    nft_rho_by_severity: dict,
    save_path: str,
) -> None:
    """Line plot of Spearman rho vs permutation severity.

    Parameters
    ----------
    flat_rho_by_severity : dict[float, float]
        Rho values for flat-MLP at each severity.
    nft_rho_by_severity : dict[float, float]
        Rho values for NFT at each severity.
    save_path : str
        Path to save the figure.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    flat_severities = sorted(flat_rho_by_severity.keys())
    flat_rhos = [flat_rho_by_severity[s] for s in flat_severities]

    nft_severities = sorted(nft_rho_by_severity.keys())
    nft_rhos = [nft_rho_by_severity[s] for s in nft_severities]

    ax.plot(flat_severities, flat_rhos, "o-", color="#e74c3c",
            linewidth=2, markersize=7, label="Flat-MLP")
    ax.plot(nft_severities, nft_rhos, "s-", color="#3498db",
            linewidth=2, markersize=7, label="NFT")

    ax.set_xlabel("Permutation Severity", fontsize=12)
    ax.set_ylabel("Spearman Rho", fontsize=12)
    ax.set_title("Spearman Rho vs Permutation Severity", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved rho_vs_severity plot to {save_path}")


def plot_pred_vs_actual(
    flat_preds_s0: np.ndarray,
    flat_labels: np.ndarray,
    nft_preds_s0: np.ndarray,
    flat_preds_s1: np.ndarray,
    nft_preds_s1: np.ndarray,
    save_path: str,
) -> None:
    """Scatter plot of predictions vs actual generalization gap.

    Parameters
    ----------
    flat_preds_s0 : np.ndarray
        Flat-MLP predictions at severity 0.
    flat_labels : np.ndarray
        True generalization gaps.
    nft_preds_s0 : np.ndarray
        NFT predictions at severity 0.
    flat_preds_s1 : np.ndarray
        Flat-MLP predictions at severity 1.
    nft_preds_s1 : np.ndarray
        NFT predictions at severity 1.
    save_path : str
        Path to save the figure.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    datasets = [
        (axes[0, 0], flat_preds_s0, flat_labels, "Flat-MLP (s=0.0)", "#e74c3c"),
        (axes[0, 1], flat_preds_s1, flat_labels, "Flat-MLP (s=1.0)", "#e74c3c"),
        (axes[1, 0], nft_preds_s0, flat_labels, "NFT (s=0.0)", "#3498db"),
        (axes[1, 1], nft_preds_s1, flat_labels, "NFT (s=1.0)", "#3498db"),
    ]

    for ax, preds, labels, title, color in datasets:
        ax.scatter(labels, preds, alpha=0.3, s=5, color=color)
        # Identity line
        mn, mx = labels.min(), labels.max()
        ax.plot([mn, mx], [mn, mx], "k--", linewidth=1, alpha=0.5)
        ax.set_xlabel("Actual Gen Gap", fontsize=10)
        ax.set_ylabel("Predicted Gen Gap", fontsize=10)
        ax.set_title(title, fontsize=11)
        ax.grid(True, alpha=0.2)

    plt.suptitle("Predicted vs Actual Generalization Gap", fontsize=13, y=1.01)
    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Saved pred_vs_actual plot to {save_path}")


def plot_bootstrap_distribution(
    flat_bootstrap: np.ndarray,
    nft_bootstrap: np.ndarray,
    save_path: str,
) -> None:
    """Histogram of bootstrap delta_rho distributions.

    Parameters
    ----------
    flat_bootstrap : np.ndarray
        Bootstrap delta_rho samples for flat-MLP.
    nft_bootstrap : np.ndarray
        Bootstrap delta_rho samples for NFT.
    save_path : str
        Path to save the figure.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for ax, samples, title, color, threshold in [
        (axes[0], flat_bootstrap, "Flat-MLP Bootstrap Delta-Rho", "#e74c3c", 0.10),
        (axes[1], nft_bootstrap, "NFT Bootstrap Delta-Rho", "#3498db", 0.02),
    ]:
        ax.hist(samples, bins=50, color=color, alpha=0.7, edgecolor="white")
        ax.axvline(x=0, color="black", linestyle="-", linewidth=1.5, label="zero")
        ax.axvline(x=threshold, color="gray", linestyle="--", linewidth=1.5,
                   label=f"threshold ({threshold})")
        ax.axvline(x=np.mean(samples), color="darkred" if color == "#e74c3c" else "darkblue",
                   linestyle="-.", linewidth=2, label=f"mean={np.mean(samples):.4f}")
        ax.set_xlabel("Delta Rho", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)
        ax.set_title(title, fontsize=12)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.2)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close(fig)
    logger.info(f"Saved bootstrap distribution plot to {save_path}")


def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Generate all 4 figures from results dict.

    Parameters
    ----------
    results : dict
        Must contain: flat_mlp_delta_rho, nft_delta_rho,
        flat_rho_by_severity, nft_rho_by_severity,
        flat_preds_s0, flat_labels, nft_preds_s0,
        flat_preds_s1, nft_preds_s1,
        flat_bootstrap, nft_bootstrap.
    figures_dir : str
        Directory to save figures.
    """
    os.makedirs(figures_dir, exist_ok=True)

    plot_delta_rho_bar(
        results["flat_mlp_delta_rho"],
        results["nft_delta_rho"],
        os.path.join(figures_dir, "delta_rho_bar.png"),
    )

    plot_rho_vs_severity(
        results["flat_rho_by_severity"],
        results["nft_rho_by_severity"],
        os.path.join(figures_dir, "rho_vs_severity.png"),
    )

    plot_pred_vs_actual(
        results["flat_preds_s0"],
        results["flat_labels"],
        results["nft_preds_s0"],
        results["flat_preds_s1"],
        results["nft_preds_s1"],
        os.path.join(figures_dir, "pred_vs_actual.png"),
    )

    plot_bootstrap_distribution(
        results["flat_bootstrap"],
        results["nft_bootstrap"],
        os.path.join(figures_dir, "bootstrap_distribution.png"),
    )

    logger.info(f"All figures saved to {figures_dir}")
