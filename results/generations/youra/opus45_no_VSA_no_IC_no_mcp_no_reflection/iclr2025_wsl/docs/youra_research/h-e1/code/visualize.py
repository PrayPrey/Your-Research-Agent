"""Visualization suite for H-E1 results."""
import os
import matplotlib.pyplot as plt
import numpy as np
from config import CONFIG


def plot_gate_bar(sigma_alpha: float, threshold: float, out_dir: str) -> None:
    """Bar chart comparing sigma_alpha to gate threshold."""
    os.makedirs(out_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["green" if sigma_alpha < threshold else "red", "gray"]
    ax.bar(["σ(α) Measured", "Threshold"], [sigma_alpha, threshold], color=colors)
    ax.axhline(y=threshold, color="red", linestyle="--", label=f"Gate: {threshold}")
    ax.set_ylabel("σ(α)")
    ax.set_title(f"Gate Check: {'PASS' if sigma_alpha < threshold else 'FAIL'}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gate_check.png"), dpi=150)
    plt.close()


def plot_alpha_histogram(results: list[dict], out_dir: str) -> None:
    """Histogram of alpha values across models."""
    os.makedirs(out_dir, exist_ok=True)

    alphas = [r["alpha_mean"] for r in results]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(alphas, bins=20, edgecolor="black", alpha=0.7)
    ax.axvline(np.mean(alphas), color="red", linestyle="--", label=f"Mean: {np.mean(alphas):.2f}")
    ax.set_xlabel("α (Heavy-Tail Exponent)")
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of α across {len(results)} ViT Models")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "alpha_histogram.png"), dpi=150)
    plt.close()


def plot_family_boxplot(results: list[dict], out_dir: str) -> None:
    """Box plot of alpha by model family."""
    os.makedirs(out_dir, exist_ok=True)

    from collections import defaultdict
    by_family = defaultdict(list)
    for r in results:
        by_family[r["family"]].append(r["alpha_mean"])

    families = sorted(by_family.keys(), key=lambda f: -len(by_family[f]))[:10]
    data = [by_family[f] for f in families]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(data, labels=families)
    ax.set_xlabel("Model Family")
    ax.set_ylabel("α")
    ax.set_title("α Distribution by Model Family")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "family_boxplot.png"), dpi=150)
    plt.close()


def plot_alpha_vs_size(results: list[dict], out_dir: str) -> None:
    """Scatter plot of alpha vs model size."""
    os.makedirs(out_dir, exist_ok=True)

    alphas = [r["alpha_mean"] for r in results]
    sizes = [r["n_params"] / 1e6 for r in results]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(sizes, alphas, alpha=0.6)
    ax.set_xlabel("Model Size (M params)")
    ax.set_ylabel("α")
    ax.set_title("α vs Model Size")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "alpha_vs_size.png"), dpi=150)
    plt.close()


def generate_all_figures(results: list[dict], aggregate: dict, out_dir: str) -> None:
    """Generate all required figures."""
    plot_gate_bar(aggregate["sigma_alpha"], CONFIG.sigma_gate_threshold, out_dir)
    plot_alpha_histogram(results, out_dir)
    plot_family_boxplot(results, out_dir)
    plot_alpha_vs_size(results, out_dir)
    print(f"Saved all figures to {out_dir}")
