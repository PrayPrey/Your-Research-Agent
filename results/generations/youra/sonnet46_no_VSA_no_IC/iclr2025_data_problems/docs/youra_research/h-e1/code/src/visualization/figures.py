"""Figure generators for h-e1 domain exposure analysis."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def plot_gate_metrics(
    per_domain_std: np.ndarray,
    domain_names: list,
    out_path: Path,
    threshold: float = 0.001,
) -> None:
    """Bar chart: per-domain std; green/red bars; threshold line."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    colors = ["green" if s > threshold else "red" for s in per_domain_std]
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(range(len(domain_names)), per_domain_std, color=colors)
    ax.axhline(y=threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_xticks(range(len(domain_names)))
    ax.set_xticklabels(domain_names, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("std(cumulative_exposure_fraction)")
    ax.set_title("Per-Domain Std of Cumulative Exposure Fraction (Gate Metrics)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_trajectories(
    trajectories: np.ndarray,
    domain_names: list,
    checkpoint_steps: list,
    out_path: Path,
    n_top: int = 5,
) -> None:
    """Line plot: top-N and bottom-N variance domains."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stds = np.std(trajectories, axis=1)
    ranked = np.argsort(stds)
    top_idx = ranked[-n_top:][::-1]
    bot_idx = ranked[:n_top]

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    for idx in top_idx:
        axes[0].plot(checkpoint_steps, trajectories[idx], label=domain_names[idx])
    axes[0].set_title(f"Top-{n_top} Variance Domains")
    axes[0].set_xlabel("Checkpoint Step")
    axes[0].set_ylabel("Cumulative Exposure Fraction")
    axes[0].legend(fontsize=7)

    for idx in bot_idx:
        axes[1].plot(checkpoint_steps, trajectories[idx], label=domain_names[idx])
    axes[1].set_title(f"Bottom-{n_top} Variance Domains")
    axes[1].set_xlabel("Checkpoint Step")
    axes[1].legend(fontsize=7)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_variance_heatmap(
    all_stds: dict,
    domain_names: list,
    out_path: Path,
) -> None:
    """22 domains x N model sizes heatmap."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sizes = list(all_stds.keys())
    matrix = np.array([all_stds[s] for s in sizes]).T  # (22, N)

    fig, ax = plt.subplots(figsize=(max(8, len(sizes) * 0.8), 10))
    sns.heatmap(matrix, xticklabels=sizes, yticklabels=domain_names, ax=ax, cmap="YlOrRd")
    ax.set_title("Domain Std Variance Heatmap (domains x model sizes)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_spearman_matrix(
    rho_matrix: np.ndarray,
    model_sizes: list,
    out_path: Path,
) -> None:
    """NxN Spearman correlation matrix heatmap."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(rho_matrix, xticklabels=model_sizes, yticklabels=model_sizes,
                ax=ax, cmap="coolwarm", vmin=-1, vmax=1, annot=True, fmt=".2f")
    ax.set_title("Spearman Correlation of Domain-Std Vectors Across Model Sizes")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
