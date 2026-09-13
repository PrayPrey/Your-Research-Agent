"""Visualization for h-m1."""
import os

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


def plot_heatmap(interaction_matrix: np.ndarray, methods: list, modes: list, out_path: str) -> None:
    """Required: Method x Mode heatmap."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        interaction_matrix,
        annot=True,
        fmt=".2f",
        xticklabels=modes,
        yticklabels=methods,
        cmap="RdYlBu_r",
        vmin=0,
        vmax=1
    )
    plt.xlabel("Mode")
    plt.ylabel("Method")
    plt.title("h-m1: Method × Mode Sensitivity (Normalized)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_radar(results: dict, out_path: str) -> None:
    """Mode sensitivity radar chart per method."""
    methods = ["trak", "tracin", "kronfluence"]
    modes = ["mem", "transfer", "spurious"]

    # Compute sensitivities
    sensitivities = {}
    for method in methods:
        sensitivities[method] = [float(np.mean(results[method][m])) for m in modes]

    # Normalize for visualization
    all_vals = [v for vals in sensitivities.values() for v in vals]
    vmin, vmax = min(all_vals), max(all_vals)
    if vmax > vmin:
        for method in methods:
            sensitivities[method] = [(v - vmin) / (vmax - vmin) for v in sensitivities[method]]

    # Radar chart
    angles = np.linspace(0, 2 * np.pi, len(modes), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    colors = ["#e74c3c", "#3498db", "#2ecc71"]
    for method, color in zip(methods, colors):
        values = sensitivities[method] + sensitivities[method][:1]
        ax.plot(angles, values, "o-", linewidth=2, label=method, color=color)
        ax.fill(angles, values, alpha=0.25, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(modes)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    plt.title("h-m1: Mode Sensitivity per Method")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_distributions(results: dict, out_path: str) -> None:
    """Influence score distributions per mode."""
    methods = ["trak", "tracin", "kronfluence"]
    modes = ["mem", "transfer", "spurious"]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    for ax, mode in zip(axes, modes):
        for method in methods:
            scores = results[method][mode]
            ax.hist(scores, bins=30, alpha=0.5, label=method, density=True)
        ax.set_title(f"Mode: {mode}")
        ax.set_xlabel("Influence Score")
        ax.set_ylabel("Density")
        ax.legend()

    plt.suptitle("h-m1: Score Distributions per Mode")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_method_correlation(results: dict, out_path: str) -> None:
    """Pairwise correlation of flattened score vectors."""
    methods = ["trak", "tracin", "kronfluence"]

    # Flatten scores per method
    flat_scores = {}
    for method in methods:
        flat_scores[method] = np.concatenate(list(results[method].values()))

    # Correlation matrix
    corr = np.zeros((3, 3))
    for i, m1 in enumerate(methods):
        for j, m2 in enumerate(methods):
            corr[i, j] = np.corrcoef(flat_scores[m1], flat_scores[m2])[0, 1]

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".3f",
        xticklabels=methods,
        yticklabels=methods,
        cmap="coolwarm",
        vmin=-1,
        vmax=1
    )
    plt.title("h-m1: Method Correlation Matrix")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
