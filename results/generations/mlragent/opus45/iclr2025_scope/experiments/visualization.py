"""
Visualization utilities for experiment results.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import os


def set_plot_style():
    """Set consistent plot style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.figsize': (10, 6),
        'figure.dpi': 150,
    })


def plot_training_curves(
    train_losses: List[float],
    val_losses: List[float],
    save_path: str = 'training_curves.png',
    title: str = 'RPN Training Curves',
):
    """Plot training and validation loss curves."""
    set_plot_style()

    fig, ax = plt.subplots(figsize=(10, 6))

    epochs = range(1, len(train_losses) + 1)

    ax.plot(epochs, train_losses, 'b-o', label='Training Loss', linewidth=2, markersize=8)
    ax.plot(epochs, val_losses, 'r-s', label='Validation Loss', linewidth=2, markersize=8)

    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss (KL Divergence)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved training curves to {save_path}")


def plot_compression_comparison(
    results: Dict[str, Dict[str, float]],
    save_path: str = 'compression_comparison.png',
):
    """Plot comparison of compression methods."""
    set_plot_style()

    methods = list(results.keys())
    metrics = ['compression_ratio_mean', 'perplexity_mean', 'memory_reduction_pct']
    metric_labels = ['Compression Ratio', 'Perplexity', 'Memory Reduction (%)']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))

    for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
        ax = axes[idx]
        values = [results[m].get(metric, 0) for m in methods]

        bars = ax.bar(methods, values, color=colors)
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.tick_params(axis='x', rotation=45)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            if not np.isnan(val):
                ax.annotate(f'{val:.2f}',
                           xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                           ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved compression comparison to {save_path}")


def plot_perplexity_vs_compression(
    results: Dict[str, Dict[str, float]],
    save_path: str = 'perplexity_vs_compression.png',
):
    """Plot perplexity vs compression ratio trade-off."""
    set_plot_style()

    fig, ax = plt.subplots(figsize=(10, 7))

    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))
    markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', 'h', '*']

    for idx, (method, metrics) in enumerate(results.items()):
        compression = metrics.get('compression_ratio_mean', 1.0)
        perplexity = metrics.get('perplexity_mean', 0)

        if np.isnan(perplexity) or compression == 0:
            continue

        ax.scatter(compression, perplexity,
                  c=[colors[idx]], marker=markers[idx % len(markers)],
                  s=200, label=method, edgecolors='black', linewidths=1.5)

    ax.set_xlabel('Compression Ratio')
    ax.set_ylabel('Perplexity')
    ax.set_title('Perplexity vs Compression Ratio Trade-off')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)

    # Set reasonable axis limits
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved perplexity vs compression plot to {save_path}")


def plot_memory_efficiency(
    results: Dict[str, Dict[str, float]],
    save_path: str = 'memory_efficiency.png',
):
    """Plot memory efficiency comparison."""
    set_plot_style()

    methods = list(results.keys())
    memory_reduction = [results[m].get('memory_reduction_pct', 0) for m in methods]
    exact_match = [results[m].get('exact_match', 0) * 100 for m in methods]  # Convert to percentage

    fig, ax1 = plt.subplots(figsize=(12, 6))

    x = np.arange(len(methods))
    width = 0.35

    bars1 = ax1.bar(x - width/2, memory_reduction, width, label='Memory Reduction (%)',
                    color='steelblue', edgecolor='black')
    ax1.set_ylabel('Memory Reduction (%)', color='steelblue')
    ax1.tick_params(axis='y', labelcolor='steelblue')

    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, exact_match, width, label='Exact Match (%)',
                    color='coral', edgecolor='black')
    ax2.set_ylabel('Exact Match (%)', color='coral')
    ax2.tick_params(axis='y', labelcolor='coral')

    ax1.set_xticks(x)
    ax1.set_xticklabels(methods, rotation=45, ha='right')
    ax1.set_title('Memory Efficiency vs Task Performance')

    # Add legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        if not np.isnan(height):
            ax1.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        ha='center', va='bottom', fontsize=8)

    for bar in bars2:
        height = bar.get_height()
        if not np.isnan(height):
            ax2.annotate(f'{height:.1f}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved memory efficiency plot to {save_path}")


def plot_latency_comparison(
    results: Dict[str, Dict[str, float]],
    save_path: str = 'latency_comparison.png',
):
    """Plot latency comparison across methods."""
    set_plot_style()

    methods = list(results.keys())
    latencies = [results[m].get('latency_mean_ms', 0) for m in methods]
    latency_stds = [results[m].get('latency_std_ms', 0) for m in methods]

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.Set2(np.linspace(0, 1, len(methods)))

    bars = ax.bar(methods, latencies, yerr=latency_stds, capsize=5,
                  color=colors, edgecolor='black', linewidth=1.5)

    ax.set_ylabel('Latency (ms)')
    ax.set_title('Inference Latency Comparison')
    ax.tick_params(axis='x', rotation=45)

    # Add value labels
    for bar, lat in zip(bars, latencies):
        if not np.isnan(lat):
            ax.annotate(f'{lat:.1f}',
                       xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved latency comparison to {save_path}")


def plot_radar_chart(
    results: Dict[str, Dict[str, float]],
    save_path: str = 'radar_comparison.png',
):
    """Create radar chart comparing methods across multiple metrics."""
    set_plot_style()

    # Metrics to include (normalized to 0-1 scale)
    metric_keys = ['compression_ratio_mean', 'perplexity_mean', 'exact_match', 'latency_mean_ms']
    metric_labels = ['Compression', 'Perplexity\n(lower better)', 'Accuracy', 'Speed\n(lower better)']

    # Get values and normalize
    methods = [m for m in results.keys() if results[m].get('compression_ratio_mean', 0) > 0]

    if len(methods) < 2:
        print("Not enough methods for radar chart")
        return

    # Collect values
    values_dict = {}
    for method in methods:
        vals = []
        for key in metric_keys:
            v = results[method].get(key, 0)
            if np.isnan(v):
                v = 0
            vals.append(v)
        values_dict[method] = vals

    # Normalize (0-1 scale, handle inversions)
    normalized = {}
    for method in methods:
        norm_vals = []
        for i, key in enumerate(metric_keys):
            all_vals = [values_dict[m][i] for m in methods if values_dict[m][i] > 0]
            if not all_vals:
                norm_vals.append(0)
                continue

            v = values_dict[method][i]
            min_v, max_v = min(all_vals), max(all_vals)

            if max_v == min_v:
                norm = 0.5
            else:
                norm = (v - min_v) / (max_v - min_v)

            # Invert for "lower is better" metrics
            if key in ['perplexity_mean', 'latency_mean_ms']:
                norm = 1 - norm

            norm_vals.append(norm)
        normalized[method] = norm_vals

    # Create radar chart
    num_metrics = len(metric_labels)
    angles = np.linspace(0, 2 * np.pi, num_metrics, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))

    colors = plt.cm.Set1(np.linspace(0, 1, len(methods)))

    for idx, method in enumerate(methods):
        values = normalized[method] + normalized[method][:1]  # Close the polygon
        ax.plot(angles, values, 'o-', linewidth=2, label=method, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels)
    ax.set_ylim(0, 1)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    ax.set_title('Multi-Metric Comparison', y=1.1)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved radar chart to {save_path}")


def plot_ablation_study(
    ablation_results: Dict[str, Dict[str, float]],
    save_path: str = 'ablation_study.png',
):
    """Plot ablation study results."""
    set_plot_style()

    configs = list(ablation_results.keys())
    perplexity = [ablation_results[c].get('perplexity_mean', 0) for c in configs]
    compression = [ablation_results[c].get('compression_ratio_mean', 1) for c in configs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Perplexity comparison
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(configs)))
    bars1 = ax1.bar(configs, perplexity, color=colors, edgecolor='black')
    ax1.set_ylabel('Perplexity')
    ax1.set_title('Ablation: Perplexity by Configuration')
    ax1.tick_params(axis='x', rotation=45)

    for bar, val in zip(bars1, perplexity):
        if val > 0:
            ax1.annotate(f'{val:.2f}',
                        xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        ha='center', va='bottom', fontsize=9)

    # Compression ratio comparison
    bars2 = ax2.bar(configs, compression, color=colors, edgecolor='black')
    ax2.set_ylabel('Compression Ratio')
    ax2.set_title('Ablation: Compression Ratio by Configuration')
    ax2.tick_params(axis='x', rotation=45)

    for bar, val in zip(bars2, compression):
        if val > 0:
            ax2.annotate(f'{val:.2f}',
                        xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved ablation study plot to {save_path}")


def create_results_table(
    results: Dict[str, Dict[str, float]],
    save_path: str = 'results_table.csv',
) -> pd.DataFrame:
    """Create and save results table."""
    df = pd.DataFrame(results).T
    df = df.round(4)
    df.to_csv(save_path)
    print(f"Saved results table to {save_path}")
    return df


def generate_all_visualizations(
    results: Dict[str, Dict[str, float]],
    train_losses: Optional[List[float]] = None,
    val_losses: Optional[List[float]] = None,
    ablation_results: Optional[Dict[str, Dict[str, float]]] = None,
    output_dir: str = 'outputs',
):
    """Generate all visualization plots."""
    os.makedirs(output_dir, exist_ok=True)

    # Training curves (if available)
    if train_losses and val_losses:
        plot_training_curves(
            train_losses, val_losses,
            save_path=os.path.join(output_dir, 'training_curves.png')
        )

    # Main comparison plots
    plot_compression_comparison(
        results,
        save_path=os.path.join(output_dir, 'compression_comparison.png')
    )

    plot_perplexity_vs_compression(
        results,
        save_path=os.path.join(output_dir, 'perplexity_vs_compression.png')
    )

    plot_memory_efficiency(
        results,
        save_path=os.path.join(output_dir, 'memory_efficiency.png')
    )

    plot_latency_comparison(
        results,
        save_path=os.path.join(output_dir, 'latency_comparison.png')
    )

    plot_radar_chart(
        results,
        save_path=os.path.join(output_dir, 'radar_comparison.png')
    )

    # Ablation study (if available)
    if ablation_results:
        plot_ablation_study(
            ablation_results,
            save_path=os.path.join(output_dir, 'ablation_study.png')
        )

    # Results table
    create_results_table(
        results,
        save_path=os.path.join(output_dir, 'results_table.csv')
    )

    print(f"\nAll visualizations saved to {output_dir}/")
