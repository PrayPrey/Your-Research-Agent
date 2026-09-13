"""Visualization for H-M1 experiment results."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional


def plot_gate_metrics(
    metrics: Dict[str, float],
    thresholds: Dict[str, float],
    output_path: str
):
    """Plot gate metric bar chart comparing actual vs threshold."""
    fig, ax = plt.subplots(figsize=(10, 6))

    labels = ["Token Accuracy", "Overhead (inverse)"]
    actual = [metrics.get("token_accuracy", 0), 1.0 / max(metrics.get("overhead_p95", 1), 0.1)]
    threshold = [thresholds.get("accuracy_min", 0.95), 1.0 / thresholds.get("overhead_max", 20.0)]

    x = np.arange(len(labels))
    width = 0.35

    bars1 = ax.bar(x - width/2, actual, width, label="Actual", color="#4CAF50")
    bars2 = ax.bar(x + width/2, threshold, width, label="Threshold", color="#2196F3", alpha=0.7)

    ax.set_ylabel("Value")
    ax.set_title("H-M1 Gate Metrics: Actual vs Threshold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    for bar, val in zip(bars1, actual):
        ax.annotate(f"{val:.3f}", xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    ha="center", va="bottom", fontsize=10)

    ax.axhline(y=thresholds.get("accuracy_min", 0.95), color="r", linestyle="--", alpha=0.5, label="Accuracy Min")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_confusion_matrix(
    cm: np.ndarray,
    output_path: str
):
    """Plot confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(8, 6))

    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=["Not Executed", "Executed"],
                yticklabels=["Not Executed", "Executed"])

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("H-M1 Token Classification Confusion Matrix")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_overhead_histogram(
    overheads: List[float],
    threshold: float,
    output_path: str
):
    """Plot histogram of trace collection overhead."""
    fig, ax = plt.subplots(figsize=(10, 6))

    valid_overheads = [o for o in overheads if o < float("inf") and o < 100]

    ax.hist(valid_overheads, bins=50, color="#9C27B0", alpha=0.7, edgecolor="black")
    ax.axvline(x=threshold, color="r", linestyle="--", linewidth=2, label=f"Threshold ({threshold}x)")
    ax.axvline(x=np.median(valid_overheads), color="g", linestyle="-", linewidth=2, label=f"Median ({np.median(valid_overheads):.2f}x)")

    ax.set_xlabel("Overhead (trace time / baseline time)")
    ax.set_ylabel("Frequency")
    ax.set_title("H-M1 Trace Collection Overhead Distribution")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def plot_coverage_heatmap(
    sample_results: List[Dict[str, Any]],
    output_path: str,
    max_samples: int = 50
):
    """Plot coverage heatmap showing executed vs non-executed regions."""
    fig, ax = plt.subplots(figsize=(14, 8))

    sample_results = sample_results[:max_samples]

    max_tokens = max(len(r.get("mask", [])) for r in sample_results if r.get("mask"))
    max_tokens = min(max_tokens, 100)

    matrix = np.zeros((len(sample_results), max_tokens))
    for i, result in enumerate(sample_results):
        mask = result.get("mask", [])[:max_tokens]
        matrix[i, :len(mask)] = mask

    sns.heatmap(matrix, cmap="RdYlGn", ax=ax, cbar_kws={"label": "Executed (1) / Not (0)"})

    ax.set_xlabel("Token Position")
    ax.set_ylabel("Sample Index")
    ax.set_title("H-M1 Token Execution Coverage Heatmap")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_figures(
    results: Dict[str, Any],
    output_dir: str
):
    """Generate all required figures from experiment results."""
    os.makedirs(output_dir, exist_ok=True)

    metrics = results.get("aggregate_metrics", {})
    thresholds = results.get("thresholds", {"accuracy_min": 0.95, "overhead_max": 20.0})

    plot_gate_metrics(
        metrics,
        thresholds,
        os.path.join(output_dir, "gate_metrics.png")
    )

    cm = np.array(results.get("confusion_matrix", [[0, 0], [0, 0]]))
    plot_confusion_matrix(
        cm,
        os.path.join(output_dir, "confusion_matrix.png")
    )

    overhead_stats = results.get("overhead_stats", {})
    if "results" in overhead_stats:
        overheads = [r["overhead"] for r in overhead_stats["results"]]
        plot_overhead_histogram(
            overheads,
            thresholds.get("overhead_max", 20.0),
            os.path.join(output_dir, "overhead_histogram.png")
        )

    sample_results = results.get("sample_results", [])
    if sample_results:
        plot_coverage_heatmap(
            sample_results,
            os.path.join(output_dir, "coverage_heatmap.png")
        )

    print(f"All figures saved to: {output_dir}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results_path = sys.argv[1]
        with open(results_path, "r") as f:
            results = json.load(f)
        output_dir = os.path.dirname(results_path) or "."
        generate_all_figures(results, os.path.join(output_dir, "figures"))
