"""Visualization for H-M1: overhead benchmark figures."""
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available; figures will be skipped")


def plot_overhead_per_layer_type(
    per_layer_overhead: Dict[str, float],
    threshold: float,
    save_path: str,
) -> None:
    """Bar chart: overhead_ratio per layer type vs threshold line."""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Skipping figure (matplotlib unavailable): %s", save_path)
        return

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
    layer_types = list(per_layer_overhead.keys()) if per_layer_overhead else ["Linear", "Conv2d", "MultiheadAttention"]
    values = [per_layer_overhead.get(lt, 0.0) for lt in layer_types]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(layer_types, values, color=["steelblue", "darkorange", "forestgreen"][:len(layer_types)], alpha=0.8)
    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=1.5, label=f"Threshold ({threshold}x)")
    ax.set_xlabel("Layer Type")
    ax.set_ylabel("Mean Overhead Ratio (orbit-PE / sequential-PE)")
    ax.set_title("H-M1: Orbit-PE Overhead per Layer Type")
    ax.legend()
    ax.set_ylim(0, max(max(values, default=1.0) * 1.3, threshold * 1.3))

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Figure saved: {save_path}")


def plot_overhead_distribution(
    results: List,
    save_path: str,
) -> None:
    """Box plots: overhead_ratio grouped by CNN vs Transformer."""
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Skipping figure (matplotlib unavailable): %s", save_path)
        return

    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

    cnn_ratios = [r.overhead_ratio for r in results if r.arch_family == "cnn" and r.success]
    tf_ratios = [r.overhead_ratio for r in results if r.arch_family == "transformer" and r.success]

    data = []
    labels = []
    if cnn_ratios:
        data.append(cnn_ratios)
        labels.append("CNN")
    if tf_ratios:
        data.append(tf_ratios)
        labels.append("Transformer")

    fig, ax = plt.subplots(figsize=(7, 5))
    if data:
        ax.boxplot(data, labels=labels, patch_artist=True,
                   boxprops=dict(facecolor="lightblue", color="navy"),
                   medianprops=dict(color="red", linewidth=2))
    ax.axhline(y=1.2, color="red", linestyle="--", linewidth=1.5, label="Threshold (1.2x)")
    ax.set_ylabel("Overhead Ratio (orbit-PE / sequential-PE)")
    ax.set_title("H-M1: Overhead Distribution by Architecture Family")
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Figure saved: {save_path}")


def save_all_figures(
    results: List,
    metrics,
    figures_dir: str,
) -> None:
    """Generate and save all required figures."""
    os.makedirs(figures_dir, exist_ok=True)

    plot_overhead_per_layer_type(
        per_layer_overhead=metrics.per_layer_overhead,
        threshold=1.2,
        save_path=os.path.join(figures_dir, "overhead_per_layer_type.png"),
    )

    plot_overhead_distribution(
        results=results,
        save_path=os.path.join(figures_dir, "overhead_distribution.png"),
    )
