"""H-M2 Plots: Visualization suite."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_gate_metrics(comparison: dict, out_path: str) -> None:
    """Bar chart: high-conf rate Type A vs Type B."""
    fig, ax = plt.subplots(figsize=(8, 5))

    x = ["Type A\n(Correctness)", "Type B\n(User-State)"]
    rates = [comparison["rate_A"], comparison["rate_B"]]
    colors = ["#4472C4", "#ED7D31"]

    bars = ax.bar(x, rates, color=colors, edgecolor="black", linewidth=1.2)

    # Add value labels
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{rate:.3f}", ha="center", va="bottom", fontsize=12, fontweight="bold")

    ax.set_ylabel("High-Confidence Rate", fontsize=12)
    ax.set_title(f"H-M2: High-Confidence Rate by Task Type\n(threshold={comparison['threshold']}, diff={comparison['rate_difference']:.4f})",
                 fontsize=13)
    ax.set_ylim(0, max(rates) * 1.2 if max(rates) > 0 else 0.1)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="50% baseline")

    # Gate result annotation
    gate_text = "PASS" if comparison["gate_pass"] else "FAIL"
    gate_color = "green" if comparison["gate_pass"] else "red"
    ax.text(0.95, 0.95, f"Gate: {gate_text}", transform=ax.transAxes,
            fontsize=14, fontweight="bold", color=gate_color,
            ha="right", va="top", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_sensitivity_curve(sweep: dict, out_path: str) -> None:
    """Line plot: rate_difference vs threshold."""
    fig, ax = plt.subplots(figsize=(8, 5))

    thresholds = sorted(sweep.keys())
    diffs = [sweep[t]["diff"] for t in thresholds]

    ax.plot(thresholds, diffs, marker="o", linewidth=2, markersize=8, color="#4472C4")
    ax.axhline(y=0.15, color="green", linestyle="--", label="Gate threshold (0.15)")
    ax.axhline(y=0.30, color="red", linestyle="--", label="Fail threshold (0.30)")

    ax.set_xlabel("High-Confidence Threshold", fontsize=12)
    ax.set_ylabel("Rate Difference |A - B|", fontsize=12)
    ax.set_title("H-M2: Threshold Sensitivity Analysis", fontsize=13)
    ax.legend()
    ax.set_ylim(0, max(diffs) * 1.3 if max(diffs) > 0 else 0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_feature_heatmap(breakdown: dict, out_path: str) -> None:
    """Heatmap: per-feature high-conf rates."""
    if breakdown.get("proxy_analysis"):
        # Skip if no real feature data
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "Feature breakdown unavailable\n(task texts not loaded)",
                ha="center", va="center", fontsize=12)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        plt.savefig(out_path, dpi=150)
        plt.close()
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    features = list(breakdown.keys())
    with_rates = [breakdown[f]["rate_with_feature"] for f in features]
    without_rates = [breakdown[f]["rate_without_feature"] for f in features]

    x = np.arange(len(features))
    width = 0.35

    ax.bar(x - width/2, with_rates, width, label="With Feature", color="#4472C4")
    ax.bar(x + width/2, without_rates, width, label="Without Feature", color="#ED7D31")

    ax.set_ylabel("High-Confidence Rate", fontsize=12)
    ax.set_title("H-M2: High-Conf Rate by Bidirectional Feature", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([f.replace("_", "\n") for f in features], fontsize=10)
    ax.legend()
    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_cross_model_scatter(per_model: dict, out_path: str) -> None:
    """Scatter plot: rate_difference per model."""
    fig, ax = plt.subplots(figsize=(8, 5))

    models = list(per_model.keys())
    diffs = [per_model[m]["diff"] for m in models]

    # Shorten model names
    short_names = [m.replace("confidence_", "").replace("_", " ") for m in models]

    colors = ["#4472C4", "#ED7D31", "#70AD47"]
    ax.scatter(range(len(models)), diffs, s=200, c=colors[:len(models)], edgecolors="black", linewidth=1.5)

    ax.axhline(y=0.15, color="green", linestyle="--", label="Gate threshold (0.15)")

    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(short_names, fontsize=10)
    ax.set_ylabel("Rate Difference |A - B|", fontsize=12)
    ax.set_title("H-M2: Cross-Model Rate Difference", fontsize=13)
    ax.legend()
    ax.set_ylim(0, max(diffs) * 1.3 if max(diffs) > 0 else 0.5)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
