"""Visualization for H-E1"""

import matplotlib.pyplot as plt
import numpy as np


def plot_gate_metrics_comparison(transformer_scores, mamba_scores, out_path):
    """Bar chart comparing Transformer vs Mamba across benchmarks."""
    benchmarks = list(transformer_scores.keys())
    x = np.arange(len(benchmarks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    t_vals = [transformer_scores[b] for b in benchmarks]
    m_vals = [mamba_scores[b] for b in benchmarks]

    ax.bar(x - width/2, t_vals, width, label="Transformer + LoRA", color="#4C72B0")
    ax.bar(x + width/2, m_vals, width, label="Mamba + LoRA", color="#DD8452")

    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Score")
    ax.set_title("H-E1: Gate Metrics Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(benchmarks)
    ax.legend()
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_delta_vs_density(deltas, densities, correlation, out_path):
    """Scatter plot of accuracy delta vs retrieval density."""
    benchmarks = list(deltas.keys())
    x = [densities[b] for b in benchmarks]
    y = [deltas[b] for b in benchmarks]

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(x, y, s=100, c="#4C72B0", edgecolors="black", linewidth=1)

    for i, b in enumerate(benchmarks):
        ax.annotate(b, (x[i], y[i]), xytext=(5, 5), textcoords="offset points")

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    x_line = np.linspace(min(x), max(x), 100)
    ax.plot(x_line, p(x_line), "--", color="gray", alpha=0.7)

    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    ax.axhline(y=-0.05, color="green", linestyle=":", label="GSM8K threshold (-5%)")
    ax.axhline(y=-0.15, color="red", linestyle=":", label="NQ threshold (-15%)")

    ax.set_xlabel("Retrieval Density")
    ax.set_ylabel("Accuracy Delta (Mamba - Transformer)")
    ax.set_title(f"H-E1: Delta vs Density (Spearman ρ = {correlation:.3f})")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_loss_curves(transformer_losses, mamba_losses, out_path):
    """Plot training loss curves for both models."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    benchmarks = list(transformer_losses.keys())

    for i, benchmark in enumerate(benchmarks):
        if i >= len(axes):
            break

        ax = axes[i]

        t_loss = transformer_losses.get(benchmark, {}).get("loss_curve", [])
        m_loss = mamba_losses.get(benchmark, {}).get("loss_curve", [])

        if t_loss:
            ax.plot(t_loss, label="Transformer", alpha=0.8)
        if m_loss:
            ax.plot(m_loss, label="Mamba", alpha=0.8)

        ax.set_xlabel("Step")
        ax.set_ylabel("Loss")
        ax.set_title(f"{benchmark}")
        ax.legend()

    plt.suptitle("H-E1: Training Loss Curves")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
