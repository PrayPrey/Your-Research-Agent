"""Visualization for H-M1."""
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from config import AnalysisConfig

def plot_gate_bar_chart(results: dict, config: AnalysisConfig) -> None:
    """Bar chart: entropy at key lengths."""
    os.makedirs(config.figures_dir, exist_ok=True)

    lengths = [256, 1024, 2048]
    layers = config.middle_layers

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(lengths))
    width = 0.25

    for i, layer in enumerate(layers):
        entropies = [results[l][layer]["entropy"]["mean"] for l in lengths]
        ax.bar(x + i * width, entropies, width, label=f"Layer {layer}")

    ax.set_xlabel("Sequence Length")
    ax.set_ylabel("Attention Entropy")
    ax.set_title("Attention Entropy at Key Sequence Lengths")
    ax.set_xticks(x + width)
    ax.set_xticklabels(["256", "1K", "2K"])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "gate_entropy_comparison.png"), dpi=150)
    plt.close()
    print("Saved gate_entropy_comparison.png")

def plot_entropy_vs_length(results: dict, config: AnalysisConfig) -> None:
    """Line plot: entropy vs length (log-scale x-axis)."""
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    for layer in config.middle_layers:
        lengths = config.target_lengths
        entropies = [results[l][layer]["entropy"]["mean"] for l in lengths]
        errors = [results[l][layer]["entropy"]["std"] for l in lengths]
        ax.errorbar(lengths, entropies, yerr=errors, marker='o', label=f"Layer {layer}", capsize=3)

    ax.set_xscale("log", base=2)
    ax.set_xlabel("Sequence Length (tokens)")
    ax.set_ylabel("Mean Attention Entropy")
    ax.set_title("Attention Entropy vs Sequence Length")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xticks(config.target_lengths)
    ax.set_xticklabels(["256", "512", "1K", "1.5K", "2K"])

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "entropy_vs_length.png"), dpi=150)
    plt.close()
    print("Saved entropy_vs_length.png")

def plot_layer_length_heatmap(results: dict, config: AnalysisConfig) -> None:
    """Heatmap: layers x lengths entropy."""
    os.makedirs(config.figures_dir, exist_ok=True)

    data = np.array([
        [results[l][layer]["entropy"]["mean"] for l in config.target_lengths]
        for layer in config.middle_layers
    ])

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.heatmap(data, annot=True, fmt=".3f",
                xticklabels=["2K", "4K", "8K", "16K", "32K"],
                yticklabels=[f"Layer {l}" for l in config.middle_layers],
                cmap="YlOrRd", ax=ax)
    ax.set_xlabel("Sequence Length")
    ax.set_ylabel("Layer")
    ax.set_title("Attention Entropy Heatmap (Layers × Lengths)")

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "entropy_heatmap.png"), dpi=150)
    plt.close()
    print("Saved entropy_heatmap.png")

def plot_sparsity_boxplots(results: dict, config: AnalysisConfig) -> None:
    """Box plots: sparsity distribution per length."""
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    lengths = config.target_lengths
    sparsities = []
    labels = []

    for l in lengths:
        for layer in config.middle_layers:
            sparsities.append(results[l][layer]["sparsity"]["mean"])
            labels.append(f"{l//1024}K")

    length_means = []
    for l in lengths:
        layer_means = [results[l][layer]["sparsity"]["mean"] for layer in config.middle_layers]
        length_means.append(np.mean(layer_means))

    ax.bar(range(len(lengths)), length_means, alpha=0.7)
    ax.set_xticks(range(len(lengths)))
    ax.set_xticklabels(["256", "512", "1K", "1.5K", "2K"])
    ax.set_xlabel("Sequence Length")
    ax.set_ylabel("Top-k Sparsity (k=32)")
    ax.set_title("Attention Sparsity vs Sequence Length")
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "sparsity_vs_length.png"), dpi=150)
    plt.close()
    print("Saved sparsity_vs_length.png")

def generate_all_figures(results: dict, config: AnalysisConfig) -> None:
    """Generate all required figures."""
    plot_gate_bar_chart(results, config)
    plot_entropy_vs_length(results, config)
    plot_layer_length_heatmap(results, config)
    plot_sparsity_boxplots(results, config)
