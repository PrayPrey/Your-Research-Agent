"""Visualization suite for h-m1 experiment."""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from config import MODEL_SIZES, MODEL_PARAMS, RANKS


def plot_gate_metrics(results: dict, correlation: dict, out_path: str) -> None:
    """Required: scatter model_size vs entropy@optimal_rank + regression line."""
    sizes = correlation["model_sizes"]
    entropies = correlation["entropies_at_optimal"]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(sizes, entropies, s=100, c="blue", label="Model")

    z = np.polyfit(sizes, entropies, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(sizes), max(sizes), 100)
    ax.plot(x_line, p(x_line), "r--", label=f"Fit (r={correlation['pearson_r']:.3f})")

    ax.set_xlabel("Model Parameters")
    ax.set_ylabel("Attention Entropy at Optimal Rank")
    ax.set_title(f"h-m1 Gate: Entropy vs Model Size (p={correlation['p_value']:.4f})")
    ax.legend()
    ax.set_xscale("log")

    for i, size in enumerate(MODEL_SIZES):
        ax.annotate(size, (sizes[i], entropies[i]), textcoords="offset points", xytext=(5, 5))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_rank_f1_curves(results: dict, out_path: str) -> None:
    """Line plots showing F1 vs rank for each model size."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for size in MODEL_SIZES:
        f1_scores = [results[size][r]["f1"] for r in RANKS]
        ax.plot(RANKS, f1_scores, marker="o", label=size)

    ax.set_xlabel("LoRA Rank")
    ax.set_ylabel("Validation F1")
    ax.set_title("F1 vs LoRA Rank by Model Size")
    ax.legend()
    ax.set_xscale("log", base=2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_entropy_heatmap(results: dict, out_path: str) -> None:
    """Heatmap of attention entropy across (model_size, rank) combinations."""
    data = np.zeros((len(MODEL_SIZES), len(RANKS)))
    for i, size in enumerate(MODEL_SIZES):
        for j, rank in enumerate(RANKS):
            data[i, j] = results[size][rank]["entropy"]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        data, xticklabels=RANKS, yticklabels=MODEL_SIZES,
        annot=True, fmt=".3f", cmap="viridis", ax=ax
    )
    ax.set_xlabel("LoRA Rank")
    ax.set_ylabel("Model Size")
    ax.set_title("Attention Entropy Heatmap")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_optimal_rank_bar(results: dict, out_path: str) -> None:
    """Bar chart showing optimal rank per model."""
    optimal_ranks = []
    for size in MODEL_SIZES:
        f1_scores = [results[size][r]["f1"] for r in RANKS]
        optimal_ranks.append(RANKS[np.argmax(f1_scores)])

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.bar(MODEL_SIZES, optimal_ranks, color="steelblue")
    ax.set_xlabel("Model Size")
    ax.set_ylabel("Optimal LoRA Rank")
    ax.set_title("Optimal Rank by Model Size")
    ax.set_yscale("log", base=2)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
