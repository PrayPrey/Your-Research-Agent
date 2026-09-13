"""visualize.py — A-4: Five figures for H-M3 correlation analysis."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats


BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def plot_scatter(
    cont_vec: np.ndarray,
    diff_mean_vec: np.ndarray,
    pearson_r: float,
    pearson_p: float,
    benchmark_labels: list[str],
    save_path: str,
) -> None:
    """Scatter: contamination estimate vs mean accuracy differential with regression line."""
    _ensure_dir(save_path)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(cont_vec, diff_mean_vec, s=120, zorder=3, color="steelblue")
    for i, label in enumerate(benchmark_labels):
        ax.annotate(label, (cont_vec[i], diff_mean_vec[i]),
                    textcoords="offset points", xytext=(6, 5), fontsize=9)
    if len(cont_vec) >= 2:
        m, b = np.polyfit(cont_vec, diff_mean_vec, 1)
        x_line = np.linspace(cont_vec.min(), cont_vec.max(), 100)
        ax.plot(x_line, m * x_line + b, "r--", alpha=0.7, label="regression")
    ax.set_xlabel("13-gram Contamination Overlap Rate", fontsize=11)
    ax.set_ylabel("Mean Accuracy Differential (dedup-Pile − Pile)", fontsize=11)
    ax.set_title(f"Contamination vs Accuracy Differential\nPearson r={pearson_r:.3f}, p={pearson_p:.4f}",
                 fontsize=12)
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_correlation_heatmap(
    r_matrix: np.ndarray,
    estimator_labels: list[str],
    model_size_labels: list[str],
    save_path: str,
) -> None:
    """Heatmap of Pearson r by estimator × model size (2×4 grid)."""
    _ensure_dir(save_path)
    fig, ax = plt.subplots(figsize=(8, 3))
    im = ax.imshow(r_matrix, vmin=-1, vmax=1, cmap="RdYlGn", aspect="auto")
    plt.colorbar(im, ax=ax, label="Pearson r")
    ax.set_xticks(range(len(model_size_labels)))
    ax.set_xticklabels(model_size_labels)
    ax.set_yticks(range(len(estimator_labels)))
    ax.set_yticklabels(estimator_labels)
    for i in range(r_matrix.shape[0]):
        for j in range(r_matrix.shape[1]):
            ax.text(j, i, f"{r_matrix[i, j]:.3f}", ha="center", va="center", fontsize=10)
    ax.set_title("Pearson r by Estimator × Model Size", fontsize=12)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_per_benchmark_bars(
    diff_matrix: np.ndarray,
    cont_levels: np.ndarray,
    benchmark_labels: list[str],
    model_size_labels: list[str],
    save_path: str,
) -> None:
    """Grouped bar chart: 4 benchmarks × 4 model sizes."""
    _ensure_dir(save_path)
    x = np.arange(len(benchmark_labels))
    width = 0.2
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (model, color) in enumerate(zip(model_size_labels, colors)):
        ax.bar(x + i * width, diff_matrix[i], width, label=model, alpha=0.85, color=color)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(benchmark_labels)
    ax.set_xlabel("Benchmark", fontsize=11)
    ax.set_ylabel("Accuracy Differential (dedup − pile)", fontsize=11)
    ax.set_title("Per-Benchmark Accuracy Differential by Model Size", fontsize=12)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend(title="Model size")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_bootstrap_ci(
    boot_r_dist: np.ndarray,
    ci_lower: float,
    ci_upper: float,
    observed_r: float,
    save_path: str,
) -> None:
    """Histogram of bootstrap Pearson r distribution with 95% CI marked."""
    _ensure_dir(save_path)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(boot_r_dist, bins=40, color="steelblue", alpha=0.7, edgecolor="white")
    ax.axvline(observed_r, color="red", lw=2, label=f"Observed r={observed_r:.3f}")
    ax.axvline(ci_lower, color="orange", lw=1.5, linestyle="--",
               label=f"95% CI [{ci_lower:.3f}, {ci_upper:.3f}]")
    ax.axvline(ci_upper, color="orange", lw=1.5, linestyle="--")
    ax.set_xlabel("Bootstrap Pearson r", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title("Bootstrap Distribution of Pearson r (n=1000 resamples)", fontsize=12)
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_spearman_ranks(
    cont_vec: np.ndarray,
    diff_mean_vec: np.ndarray,
    benchmark_labels: list[str],
    save_path: str,
) -> None:
    """Rank plot: contamination rank vs differential rank for 4 benchmarks."""
    _ensure_dir(save_path)
    cont_ranks = stats.rankdata(cont_vec)
    diff_ranks = stats.rankdata(diff_mean_vec)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(cont_ranks, diff_ranks, s=120, zorder=3, color="steelblue")
    for i, label in enumerate(benchmark_labels):
        ax.annotate(label, (cont_ranks[i], diff_ranks[i]),
                    textcoords="offset points", xytext=(5, 5), fontsize=9)
    ax.set_xlabel("Contamination Rank", fontsize=11)
    ax.set_ylabel("Differential Rank", fontsize=11)
    ax.set_title("Spearman Rank Visualization (n=4 benchmarks)", fontsize=12)
    ax.set_xticks([1, 2, 3, 4])
    ax.set_yticks([1, 2, 3, 4])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")
