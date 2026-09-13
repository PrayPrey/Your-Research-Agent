import matplotlib.pyplot as plt
import numpy as np
import os


def plot_overhead_bar(overhead_ratio: float, threshold: float = 2.0, save_path: str = None):
    """Bar chart comparing vanilla (1.0) vs TC-SSM overhead."""
    fig, ax = plt.subplots(figsize=(6, 4))

    bars = ax.bar(["Vanilla Mamba", "TC-SSM"], [1.0, overhead_ratio], color=["#2ecc71", "#3498db"])
    ax.axhline(y=threshold, color="red", linestyle="--", label=f"Threshold ({threshold}x)")

    ax.set_ylabel("Relative Time (baseline=1.0)")
    ax.set_title("Overhead Comparison")
    ax.legend()

    for bar, val in zip(bars, [1.0, overhead_ratio]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{val:.2f}x",
                ha="center", fontsize=10)

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
    plt.close()


def plot_rank_ablation(rank_results: dict, save_path: str = None):
    """Line plot of rank vs overhead."""
    ranks = sorted(rank_results.keys())
    overheads = [rank_results[r]["overhead"] for r in ranks]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(ranks, overheads, "o-", color="#3498db", linewidth=2, markersize=8)
    ax.axhline(y=2.0, color="red", linestyle="--", label="Threshold (2.0x)")

    ax.set_xlabel("Rank")
    ax.set_ylabel("Overhead Ratio")
    ax.set_title("Rank Ablation: Overhead vs Rank")
    ax.set_xticks(ranks)
    ax.legend()

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
    plt.close()


def plot_state_variance_heatmap(task_names: list[str], variances: list[float], save_path: str = None):
    """Heatmap of state variance per task."""
    fig, ax = plt.subplots(figsize=(6, 2))

    data = np.array(variances).reshape(1, -1)
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd")

    ax.set_xticks(range(len(task_names)))
    ax.set_xticklabels(task_names)
    ax.set_yticks([])
    ax.set_title("State Variance by Task")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Variance")

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
    plt.close()


def plot_matrix_breakdown(breakdown: dict, save_path: str = None):
    """Pie chart of overhead contribution per matrix."""
    labels = [k for k in ["delta", "B", "C"] if k in breakdown and breakdown[k] > 0]
    sizes = [breakdown[k] for k in labels]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=["#3498db", "#2ecc71", "#e74c3c"])
    ax.set_title("Per-Matrix Overhead Breakdown")

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
    plt.close()
