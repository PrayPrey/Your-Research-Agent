"""
Visualization utilities for EmbedPrint experiments.
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")


def plot_training_curves(
    history: Dict[str, List[float]],
    save_path: str,
    title: str = "Training Curves",
):
    """Plot training and validation loss curves."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # Total loss
    ax = axes[0]
    epochs = range(1, len(history["train_loss"]) + 1)
    ax.plot(epochs, history["train_loss"], 'b-o', label="Train Loss", markersize=6)
    if "eval_loss" in history:
        ax.plot(epochs, history["eval_loss"], 'r-s', label="Eval Loss", markersize=6)
    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Loss", fontsize=12)
    ax.set_title("Total Loss", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # LM and FP losses (for EmbedPrint)
    ax = axes[1]
    if "train_lm_loss" in history and "train_fp_loss" in history:
        ax.plot(epochs, history["train_lm_loss"], 'g-^', label="LM Loss", markersize=6)
        ax.plot(epochs, history["train_fp_loss"], 'm-d', label="FP Loss", markersize=6)
        ax.set_xlabel("Epoch", fontsize=12)
        ax.set_ylabel("Loss", fontsize=12)
        ax.set_title("LM vs Fingerprint Loss", fontsize=14)
        ax.legend(fontsize=10)
    else:
        ax.text(0.5, 0.5, "N/A for baseline", ha='center', va='center', fontsize=12)
        ax.set_title("LM vs Fingerprint Loss", fontsize=14)
    ax.grid(True, alpha=0.3)

    # Perplexity
    ax = axes[2]
    if "eval_perplexity" in history:
        ax.plot(epochs, history["eval_perplexity"], 'c-o', label="Eval Perplexity", markersize=6)
        ax.set_xlabel("Epoch", fontsize=12)
        ax.set_ylabel("Perplexity", fontsize=12)
        ax.set_title("Evaluation Perplexity", fontsize=14)
        ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved training curves to {save_path}")


def plot_attribution_accuracy(
    history: Dict[str, List[float]],
    save_path: str,
    title: str = "Attribution Accuracy Over Training",
):
    """Plot attribution accuracy over training epochs."""
    if "attribution_accuracy" not in history or len(history["attribution_accuracy"]) == 0:
        # Create placeholder plot
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, "No attribution accuracy data available", ha='center', va='center', fontsize=12)
        ax.set_title(title, fontsize=14)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    epochs = range(1, len(history["attribution_accuracy"]) + 1)
    ax.plot(epochs, history["attribution_accuracy"], 'b-o', linewidth=2, markersize=8)

    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Precision@10", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3)

    # Add value labels
    for i, v in enumerate(history["attribution_accuracy"]):
        ax.annotate(f'{v:.3f}', (i + 1, v), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved attribution accuracy plot to {save_path}")


def plot_method_comparison(
    results: Dict[str, Dict[str, float]],
    metric: str,
    save_path: str,
    title: str = "Method Comparison",
):
    """Plot comparison of different methods on a specific metric."""
    fig, ax = plt.subplots(figsize=(10, 6))

    methods = list(results.keys())
    values = [results[m].get(metric, 0) for m in methods]
    colors = plt.cm.Set2(np.linspace(0, 1, len(methods)))

    bars = ax.bar(methods, values, color=colors, edgecolor='black', linewidth=1)

    ax.set_xlabel("Method", fontsize=12)
    ax.set_ylabel(metric, fontsize=12)
    ax.set_title(title, fontsize=14)

    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(f'{val:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved method comparison plot to {save_path}")


def plot_precision_recall_curves(
    results: Dict[str, Dict[str, float]],
    save_path: str,
    title: str = "Precision@K Comparison",
):
    """Plot precision@k for different k values across methods."""
    fig, ax = plt.subplots(figsize=(10, 6))

    k_values = [1, 5, 10, 20]
    markers = ['o', 's', '^', 'd', 'v', 'p']
    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))

    for idx, (method, metrics) in enumerate(results.items()):
        precisions = [metrics.get(f"precision@{k}", 0) for k in k_values]
        ax.plot(k_values, precisions, marker=markers[idx % len(markers)],
                label=method, linewidth=2, markersize=8, color=colors[idx])

    ax.set_xlabel("K", fontsize=12)
    ax.set_ylabel("Precision@K", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_ylim([0, 1])
    ax.set_xticks(k_values)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved precision-recall curves to {save_path}")


def plot_latency_comparison(
    results: Dict[str, Dict[str, float]],
    save_path: str,
    title: str = "Attribution Latency Comparison",
):
    """Plot latency comparison across methods."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    methods = list(results.keys())
    latencies = [results[m].get("avg_latency_ms", 0) for m in methods]
    throughputs = [results[m].get("throughput_qps", 0) for m in methods]
    colors = plt.cm.Set3(np.linspace(0, 1, len(methods)))

    # Latency plot (log scale)
    ax = axes[0]
    bars = ax.bar(methods, latencies, color=colors, edgecolor='black', linewidth=1)
    ax.set_xlabel("Method", fontsize=12)
    ax.set_ylabel("Latency (ms)", fontsize=12)
    ax.set_title("Average Attribution Latency", fontsize=14)
    ax.set_yscale('log')

    for bar, val in zip(bars, latencies):
        height = bar.get_height()
        ax.annotate(f'{val:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.sca(ax)
    plt.xticks(rotation=15, ha='right')

    # Throughput plot
    ax = axes[1]
    bars = ax.bar(methods, throughputs, color=colors, edgecolor='black', linewidth=1)
    ax.set_xlabel("Method", fontsize=12)
    ax.set_ylabel("Throughput (queries/sec)", fontsize=12)
    ax.set_title("Attribution Throughput", fontsize=14)

    for bar, val in zip(bars, throughputs):
        height = bar.get_height()
        ax.annotate(f'{val:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    plt.sca(ax)
    plt.xticks(rotation=15, ha='right')

    plt.suptitle(title, fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved latency comparison plot to {save_path}")


def plot_radar_chart(
    results: Dict[str, Dict[str, float]],
    metrics: List[str],
    save_path: str,
    title: str = "Multi-Metric Comparison",
):
    """Create radar chart for multi-metric comparison."""
    num_metrics = len(metrics)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))

    colors = plt.cm.Set1(np.linspace(0, 1, len(results)))

    for idx, (method, method_results) in enumerate(results.items()):
        values = []
        for m in metrics:
            val = method_results.get(m, 0)
            # Normalize latency (inverse, lower is better)
            if "latency" in m.lower():
                val = 1 / (1 + val / 1000)  # Normalize to [0, 1]
            values.append(val)
        values += values[:1]

        ax.plot(angles, values, 'o-', linewidth=2, label=method, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylim([0, 1])
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=10)
    ax.set_title(title, fontsize=14, y=1.08)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved radar chart to {save_path}")


def plot_perplexity_comparison(
    embedprint_ppl: float,
    baseline_ppl: float,
    save_path: str,
    title: str = "Model Quality Comparison",
):
    """Plot perplexity comparison between EmbedPrint and baseline."""
    fig, ax = plt.subplots(figsize=(8, 5))

    methods = ["Baseline LM", "EmbedPrint"]
    ppls = [baseline_ppl, embedprint_ppl]
    colors = ['#2ecc71', '#3498db']

    bars = ax.bar(methods, ppls, color=colors, edgecolor='black', linewidth=1.5, width=0.5)

    ax.set_ylabel("Perplexity", fontsize=12)
    ax.set_title(title, fontsize=14)

    # Add value labels
    for bar, val in zip(bars, ppls):
        height = bar.get_height()
        ax.annotate(f'{val:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Add degradation annotation
    degradation = ((embedprint_ppl - baseline_ppl) / baseline_ppl) * 100
    ax.text(0.5, 0.95, f"Degradation: {degradation:+.2f}%",
            transform=ax.transAxes, ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved perplexity comparison plot to {save_path}")


def create_results_table(
    results: Dict[str, Dict[str, float]],
    save_path: str,
):
    """Create and save results table as CSV."""
    # Flatten results into DataFrame
    rows = []
    for method, metrics in results.items():
        row = {"Method": method}
        row.update(metrics)
        rows.append(row)

    df = pd.DataFrame(rows)

    # Reorder columns
    priority_cols = ["Method", "precision@1", "precision@5", "precision@10", "precision@20",
                     "mrr", "avg_latency_ms", "throughput_qps"]
    cols = [c for c in priority_cols if c in df.columns]
    other_cols = [c for c in df.columns if c not in cols]
    df = df[cols + other_cols]

    df.to_csv(save_path, index=False, float_format='%.4f')
    print(f"Saved results table to {save_path}")

    return df


def generate_all_figures(
    embedprint_history: Dict[str, List[float]],
    baseline_history: Dict[str, List[float]],
    all_results: Dict[str, Dict[str, float]],
    output_dir: str,
):
    """Generate all figures for the experiment."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Training curves
    plot_training_curves(
        embedprint_history,
        str(output_dir / "embedprint_training_curves.png"),
        "EmbedPrint Training Curves"
    )

    if baseline_history:
        plot_training_curves(
            baseline_history,
            str(output_dir / "baseline_training_curves.png"),
            "Baseline LM Training Curves"
        )

    # Attribution accuracy over training
    plot_attribution_accuracy(
        embedprint_history,
        str(output_dir / "attribution_accuracy_training.png"),
        "EmbedPrint Attribution Accuracy Over Training"
    )

    # Method comparison - Precision@10
    plot_method_comparison(
        all_results,
        "precision@10",
        str(output_dir / "method_comparison_precision10.png"),
        "Attribution Precision@10 Comparison"
    )

    # Method comparison - MRR
    plot_method_comparison(
        all_results,
        "mrr",
        str(output_dir / "method_comparison_mrr.png"),
        "Attribution MRR Comparison"
    )

    # Precision@K curves
    plot_precision_recall_curves(
        all_results,
        str(output_dir / "precision_at_k_curves.png"),
        "Precision@K Across Methods"
    )

    # Latency comparison
    plot_latency_comparison(
        all_results,
        str(output_dir / "latency_comparison.png"),
        "Attribution Efficiency Comparison"
    )

    # Radar chart
    metrics = ["precision@10", "mrr", "avg_latency_ms"]
    plot_radar_chart(
        all_results,
        metrics,
        str(output_dir / "radar_comparison.png"),
        "Multi-Metric Method Comparison"
    )

    # Perplexity comparison
    embedprint_ppl = embedprint_history.get("eval_perplexity", [0])[-1] if embedprint_history.get("eval_perplexity") else 0
    baseline_ppl = baseline_history.get("eval_perplexity", [0])[-1] if baseline_history.get("eval_perplexity") else 0
    if embedprint_ppl > 0 and baseline_ppl > 0:
        plot_perplexity_comparison(
            embedprint_ppl,
            baseline_ppl,
            str(output_dir / "perplexity_comparison.png"),
            "Language Model Quality: Baseline vs EmbedPrint"
        )

    # Results table
    create_results_table(all_results, str(output_dir / "results_table.csv"))

    print(f"\nAll figures saved to {output_dir}")
