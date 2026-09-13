"""
Visualization script for experimental results
"""

import json
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12


def load_results(results_path='experiment_results.json'):
    """Load experimental results"""
    with open(results_path, 'r') as f:
        results = json.load(f)
    return results


def plot_comparison_metrics(results, output_dir='.'):
    """Plot comparison of all methods across metrics"""

    methods = list(results.keys())
    metrics_to_plot = [
        ('avg_retention_rate', 'Average Retention Rate', 'Retention Rate'),
        ('cache_reduction', 'KV Cache Reduction', 'Cache Reduction (%)'),
        ('avg_latency', 'Average Latency', 'Latency (seconds)'),
        ('avg_memory_mb', 'Memory Usage', 'Memory (MB)')
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

    for idx, (metric_key, title, ylabel) in enumerate(metrics_to_plot):
        ax = axes[idx]

        values = [results[m][metric_key] for m in methods]

        bars = ax.bar(methods, values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.3f}' if val < 10 else f'{val:.1f}',
                   ha='center', va='bottom', fontsize=10)

        ax.set_xlabel('Method', fontweight='bold')
        ax.set_ylabel(ylabel, fontweight='bold')
        ax.set_title(title, fontweight='bold', fontsize=14)
        ax.grid(axis='y', alpha=0.3)

        # Rotate x labels if needed
        ax.set_xticklabels(methods, rotation=0)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_metrics.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {os.path.join(output_dir, 'comparison_metrics.png')}")
    plt.close()


def plot_efficiency_performance_tradeoff(results, output_dir='.'):
    """Plot efficiency vs performance trade-off"""

    fig, ax = plt.subplots(figsize=(10, 8))

    methods = list(results.keys())
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
    markers = ['o', 's', '^', 'D']

    for method, color, marker in zip(methods, colors, markers):
        cache_reduction = results[method]['cache_reduction'] * 100
        # Inverse latency as proxy for performance (higher is better)
        performance_score = 1.0 / (results[method]['avg_latency'] + 1e-6)

        ax.scatter(cache_reduction, performance_score,
                  s=300, alpha=0.7, c=color, marker=marker,
                  edgecolors='black', linewidths=2, label=method)

        # Add annotation
        ax.annotate(method,
                   xy=(cache_reduction, performance_score),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=11, fontweight='bold')

    ax.set_xlabel('KV Cache Reduction (%)', fontweight='bold', fontsize=13)
    ax.set_ylabel('Performance Score (1/Latency)', fontweight='bold', fontsize=13)
    ax.set_title('Efficiency-Performance Trade-off', fontweight='bold', fontsize=15)
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'efficiency_performance_tradeoff.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {os.path.join(output_dir, 'efficiency_performance_tradeoff.png')}")
    plt.close()


def plot_retention_distribution(results, output_dir='.'):
    """Plot distribution of retention rates across methods"""

    fig, ax = plt.subplots(figsize=(12, 7))

    methods = list(results.keys())
    retention_data = []
    labels = []

    for method in methods:
        if 'retention_rates' in results[method] and results[method]['retention_rates']:
            retention_data.append(np.array(results[method]['retention_rates']))
            labels.append(method)

    if retention_data:
        positions = np.arange(len(labels))
        bp = ax.boxplot(retention_data, positions=positions, widths=0.6,
                       patch_artist=True, notch=True,
                       boxprops=dict(facecolor='lightblue', alpha=0.7),
                       medianprops=dict(color='red', linewidth=2),
                       whiskerprops=dict(linewidth=1.5),
                       capprops=dict(linewidth=1.5))

        # Color boxes differently
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        for patch, color in zip(bp['boxes'], colors[:len(labels)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_xticklabels(labels, rotation=0, fontsize=12)
        ax.set_xlabel('Method', fontweight='bold', fontsize=13)
        ax.set_ylabel('Retention Rate', fontweight='bold', fontsize=13)
        ax.set_title('Distribution of Retention Rates Across Methods', fontweight='bold', fontsize=15)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'retention_distribution.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {os.path.join(output_dir, 'retention_distribution.png')}")
    plt.close()


def plot_radar_chart(results, output_dir='.'):
    """Plot radar chart comparing methods across metrics"""

    methods = list(results.keys())

    # Normalize metrics to 0-1 scale
    categories = ['Cache\nReduction', 'Speed\n(1/Latency)', 'Memory\nEfficiency', 'Overall']

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle

    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

    # Get max values for normalization
    max_cache_red = max([results[m]['cache_reduction'] for m in methods])
    max_latency = max([results[m]['avg_latency'] for m in methods])
    max_memory = max([results[m]['avg_memory_mb'] for m in methods])

    for method, color in zip(methods, colors):
        # Normalize metrics (higher is better)
        cache_red_norm = results[method]['cache_reduction'] / (max_cache_red + 1e-6)
        speed_norm = (1.0 - results[method]['avg_latency'] / (max_latency + 1e-6))
        memory_eff_norm = (1.0 - results[method]['avg_memory_mb'] / (max_memory + 1e-6))

        # Overall score
        overall = (cache_red_norm + speed_norm + memory_eff_norm) / 3.0

        values = [cache_red_norm, speed_norm, memory_eff_norm, overall]
        values += values[:1]  # Complete the circle

        ax.plot(angles, values, 'o-', linewidth=2, label=method, color=color)
        ax.fill(angles, values, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_title('Multi-dimensional Method Comparison',
                fontweight='bold', fontsize=15, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'radar_comparison.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {os.path.join(output_dir, 'radar_comparison.png')}")
    plt.close()


def plot_method_comparison_table(results, output_dir='.'):
    """Create a visual table comparing methods"""

    methods = list(results.keys())
    metrics = ['Retention Rate', 'Cache Reduction', 'Latency (s)', 'Memory (MB)']

    data = []
    for method in methods:
        row = [
            f"{results[method]['avg_retention_rate']:.3f}",
            f"{results[method]['cache_reduction']:.3f}",
            f"{results[method]['avg_latency']:.4f}",
            f"{results[method]['avg_memory_mb']:.2f}"
        ]
        data.append(row)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('tight')
    ax.axis('off')

    table = ax.table(cellText=data,
                    rowLabels=methods,
                    colLabels=metrics,
                    cellLoc='center',
                    rowLoc='center',
                    loc='center',
                    colWidths=[0.2, 0.2, 0.2, 0.2])

    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 2)

    # Style header
    for i in range(len(metrics)):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # Style rows
    colors = ['#ecf0f1', '#d5dbdb']
    for i in range(len(methods)):
        table[(i+1, -1)].set_facecolor(colors[i % 2])
        for j in range(len(metrics)):
            table[(i+1, j)].set_facecolor(colors[i % 2])

    plt.title('Method Comparison Summary', fontweight='bold', fontsize=15, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'comparison_table.png'), dpi=300, bbox_inches='tight')
    print(f"Saved: {os.path.join(output_dir, 'comparison_table.png')}")
    plt.close()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results_path', type=str, default='experiment_results.json')
    parser.add_argument('--output_dir', type=str, default='.')
    args = parser.parse_args()

    print("Loading results...")
    results = load_results(args.results_path)

    print("Generating visualizations...")

    # Generate all plots
    plot_comparison_metrics(results, args.output_dir)
    plot_efficiency_performance_tradeoff(results, args.output_dir)
    plot_retention_distribution(results, args.output_dir)
    plot_radar_chart(results, args.output_dir)
    plot_method_comparison_table(results, args.output_dir)

    print("\nAll visualizations generated successfully!")


if __name__ == '__main__':
    main()
