"""Visualization: permutation distribution, scree plot, loadings bar chart."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def plot_permutation_dist(null_dist: list, lambda_obs: float, threshold_95: float, out_path: str) -> None:
    """Plot null distribution with observed λ₁ and threshold."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.hist(null_dist, bins=50, color="steelblue", alpha=0.7, edgecolor="white", label="Null distribution")
    ax.axvline(threshold_95, color="orange", linestyle="--", linewidth=2, label=f"95th percentile ({threshold_95:.3f})")
    ax.axvline(lambda_obs, color="red", linestyle="-", linewidth=2, label=f"Observed λ₁ ({lambda_obs:.3f})")

    ax.set_xlabel("First eigenvalue (λ₁)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Permutation Test: λ₁ Significance", fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_scree(eigenvalues: list, out_path: str) -> None:
    """Scree plot of eigenvalues."""
    fig, ax = plt.subplots(figsize=(7, 5))

    x = range(1, len(eigenvalues) + 1)
    ax.plot(x, eigenvalues, "o-", color="steelblue", markersize=8, linewidth=2)
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Kaiser criterion (λ=1)")

    ax.set_xlabel("Principal Component", fontsize=12)
    ax.set_ylabel("Eigenvalue", fontsize=12)
    ax.set_title("Scree Plot", fontsize=14)
    ax.set_xticks(x)
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_pc1_loadings(loadings: list, labels: list, out_path: str) -> None:
    """Bar chart of PC1 loadings."""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = np.arange(len(labels))
    colors = ["steelblue" if v >= 0 else "coral" for v in loadings]

    ax.bar(x, loadings, color=colors, edgecolor="white")
    ax.axhline(0, color="black", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_xlabel("Benchmark", fontsize=12)
    ax.set_ylabel("PC1 Loading", fontsize=12)
    ax.set_title("First Principal Component Loadings", fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
