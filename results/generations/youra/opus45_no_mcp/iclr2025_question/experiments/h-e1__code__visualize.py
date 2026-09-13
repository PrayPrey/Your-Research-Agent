"""Generate figures for H-E1 validation report."""
import json
import os
import numpy as np
import matplotlib.pyplot as plt


def load_results(results_path: str) -> dict:
    with open(results_path, "r") as f:
        return json.load(f)


def plot_success_rate(metrics: dict, figures_dir: str):
    """Bar chart: target vs actual success rate."""
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Target (99%)", "Actual"]
    values = [99.0, metrics["success_rate"]]
    colors = ["#cccccc", "#4CAF50" if metrics["success_rate"] >= 99 else "#f44336"]

    ax.bar(labels, values, color=colors)
    ax.axhline(y=99, color="red", linestyle="--", label="Target")
    ax.set_ylabel("Success Rate (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Gate Metric: Success Rate")

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "success_rate.png"), dpi=150)
    plt.close()


def plot_entropy_histogram(results: list, figures_dir: str):
    """Histogram of entropy values."""
    entropies = [r["entropy"] for r in results if r["success"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(entropies, bins=30, edgecolor="black", alpha=0.7)
    ax.axvline(np.mean(entropies), color="red", linestyle="--", label=f"Mean: {np.mean(entropies):.2f}")
    ax.set_xlabel("Entropy")
    ax.set_ylabel("Frequency")
    ax.set_title("Entropy Distribution")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "entropy_histogram.png"), dpi=150)
    plt.close()


def plot_consistency_histogram(results: list, figures_dir: str):
    """Histogram of consistency values."""
    consistencies = [r["consistency"] for r in results if r["success"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(consistencies, bins=30, edgecolor="black", alpha=0.7, color="orange")
    ax.axvline(np.mean(consistencies), color="red", linestyle="--", label=f"Mean: {np.mean(consistencies):.2f}")
    ax.set_xlabel("Semantic Consistency")
    ax.set_ylabel("Frequency")
    ax.set_title("Consistency Distribution")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "consistency_histogram.png"), dpi=150)
    plt.close()


def plot_entropy_vs_consistency(results: list, figures_dir: str):
    """Scatter plot: entropy vs consistency."""
    successful = [r for r in results if r["success"]]
    entropies = [r["entropy"] for r in successful]
    consistencies = [r["consistency"] for r in successful]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(entropies, consistencies, alpha=0.5, s=10)
    ax.set_xlabel("Entropy")
    ax.set_ylabel("Semantic Consistency")
    ax.set_title("Entropy vs Consistency")

    # Add correlation
    corr = np.corrcoef(entropies, consistencies)[0, 1]
    ax.text(0.05, 0.95, f"r = {corr:.3f}", transform=ax.transAxes, fontsize=12, verticalalignment="top")

    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "entropy_vs_consistency.png"), dpi=150)
    plt.close()


def generate_all_figures(results_path: str, figures_dir: str):
    """Generate all figures from results."""
    os.makedirs(figures_dir, exist_ok=True)

    data = load_results(results_path)
    metrics = data["metrics"]
    results = data["results"]

    plot_success_rate(metrics, figures_dir)
    plot_entropy_histogram(results, figures_dir)
    plot_consistency_histogram(results, figures_dir)
    plot_entropy_vs_consistency(results, figures_dir)

    print(f"Figures saved to {figures_dir}")


if __name__ == "__main__":
    generate_all_figures("outputs/results.json", "../figures")
