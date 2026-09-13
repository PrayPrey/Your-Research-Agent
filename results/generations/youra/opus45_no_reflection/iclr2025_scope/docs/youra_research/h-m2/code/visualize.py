"""Visualization for H-M2 Hidden State Drift Analysis."""
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from config import AnalysisConfig


def plot_drift_vs_length(results: dict, config: AnalysisConfig) -> None:
    """Required: Line plot showing L2 drift for MOHAWK and CAB across lengths."""
    os.makedirs(config.figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    lengths = config.target_lengths

    if "mohawk" in results and results["mohawk"]:
        mohawk_drifts = [results["mohawk"][l]["l2"] for l in lengths]
        mohawk_slope = results["mohawk"]["slope"]["slope"] if "slope" in results["mohawk"] else 0
        ax.plot(lengths, mohawk_drifts, 'o-', color='orange', linewidth=2,
                markersize=8, label=f'MOHAWK (slope={mohawk_slope:.2e})')

    if results.get("cab") and results["cab"]:
        cab_drifts = [results["cab"][l]["l2"] for l in lengths]
        cab_slope = results["cab"]["slope"]["slope"] if "slope" in results["cab"] else 0
        ax.plot(lengths, cab_drifts, 's-', color='blue', linewidth=2,
                markersize=8, label=f'CAB (slope={cab_slope:.2e})')

    ax.set_xlabel("Sequence Length (tokens)", fontsize=12)
    ax.set_ylabel("Mean L2 Drift (Teacher - Student)", fontsize=12)
    ax.set_title("Hidden State Drift vs Sequence Length\n(Token-level CAB vs Matrix-level MOHAWK)", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(lengths)

    gate = results.get("gate", {})
    verdict = "PASS" if gate.get("pass") else "FAIL"
    ax.annotate(f"Gate: {verdict}", xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=12, fontweight='bold', verticalalignment='top',
                color='green' if gate.get("pass") else 'red')

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "drift_vs_length.png"), dpi=150)
    plt.close()
    print("Saved drift_vs_length.png")


def plot_per_layer_heatmap(results: dict, config: AnalysisConfig) -> None:
    """Optional: Heatmap of layers x lengths x {mohawk, cab}."""
    os.makedirs(config.figures_dir, exist_ok=True)

    if not results.get("mohawk") or not results.get("cab"):
        print("Skipping per-layer heatmap (missing variant)")
        return

    lengths = config.target_lengths
    layers = config.middle_layers

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, variant, title in zip(axes, ["mohawk", "cab"], ["MOHAWK (Matrix)", "CAB (Token)"]):
        data = np.array([
            [results[variant][l]["per_layer"].get(layer, {}).get("l2", 0) for l in lengths]
            for layer in layers
        ])

        sns.heatmap(data, annot=True, fmt=".3f",
                    xticklabels=[str(l) for l in lengths],
                    yticklabels=[f"Layer {l}" for l in layers],
                    cmap="YlOrRd", ax=ax)
        ax.set_xlabel("Sequence Length")
        ax.set_ylabel("Layer")
        ax.set_title(f"{title} L2 Drift")

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "per_layer_heatmap.png"), dpi=150)
    plt.close()
    print("Saved per_layer_heatmap.png")


def plot_cosine_bars(results: dict, config: AnalysisConfig) -> None:
    """Optional: Bar chart of cosine similarity per length."""
    os.makedirs(config.figures_dir, exist_ok=True)

    lengths = config.target_lengths
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(lengths))
    width = 0.35

    if "mohawk" in results and results["mohawk"]:
        mohawk_cos = [results["mohawk"][l]["cosine"] for l in lengths]
        ax.bar(x - width/2, mohawk_cos, width, label='MOHAWK', color='orange', alpha=0.8)

    if results.get("cab") and results["cab"]:
        cab_cos = [results["cab"][l]["cosine"] for l in lengths]
        ax.bar(x + width/2, cab_cos, width, label='CAB', color='blue', alpha=0.8)

    ax.set_xlabel("Sequence Length")
    ax.set_ylabel("Cosine Similarity")
    ax.set_title("Teacher-Student Cosine Similarity by Length")
    ax.set_xticks(x)
    ax.set_xticklabels([str(l) for l in lengths])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "cosine_similarity.png"), dpi=150)
    plt.close()
    print("Saved cosine_similarity.png")


def plot_drift_distribution(results: dict, config: AnalysisConfig) -> None:
    """Optional: Simple comparison of drift at different lengths."""
    os.makedirs(config.figures_dir, exist_ok=True)

    if not results.get("mohawk") or not results.get("cab"):
        print("Skipping drift distribution (missing variant)")
        return

    lengths = config.target_lengths

    fig, ax = plt.subplots(figsize=(10, 6))

    mohawk_drifts = [results["mohawk"][l]["l2"] for l in lengths]
    cab_drifts = [results["cab"][l]["l2"] for l in lengths]

    diff = [m - c for m, c in zip(mohawk_drifts, cab_drifts)]

    ax.bar(range(len(lengths)), diff, color=['red' if d > 0 else 'green' for d in diff], alpha=0.7)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xticks(range(len(lengths)))
    ax.set_xticklabels([str(l) for l in lengths])
    ax.set_xlabel("Sequence Length")
    ax.set_ylabel("MOHAWK Drift - CAB Drift")
    ax.set_title("Drift Difference (Positive = MOHAWK drifts more)")
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(config.figures_dir, "drift_difference.png"), dpi=150)
    plt.close()
    print("Saved drift_difference.png")


def generate_all_figures(results: dict, config: AnalysisConfig) -> None:
    """Generate all figures."""
    plot_drift_vs_length(results, config)
    plot_per_layer_heatmap(results, config)
    plot_cosine_bars(results, config)
    plot_drift_distribution(results, config)
