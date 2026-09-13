"""H-M4 Visualization: Cross-benchmark timing figures"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def plot_gate_metrics(gate_result: dict, save_path: str) -> None:
    """Bar chart comparing target vs actual gate metrics."""
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics = gate_result['metrics']
    labels = ['Range Compliance (%)', 'Cross-Benchmark Variance']
    targets = [100.0, gate_result['metrics']['variance_target']]
    actuals = [metrics['range_compliance_percent'], metrics['cross_benchmark_variance']]

    x = np.arange(len(labels))
    width = 0.35
    passed = gate_result['status'] == 'PASS'
    color = '#4CAF50' if passed else ('#FF9800' if gate_result['status'] == 'CONDITIONAL' else '#F44336')

    ax.bar(x - width/2, targets, width, label='Target', color='#2196F3', alpha=0.8)
    ax.bar(x + width/2, actuals, width, label='Actual', color=color, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel('Value')
    ax.set_title(f"H-M4 Gate Metrics - {gate_result['status']}")
    ax.legend()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_normalized_timing_bars(aggregated: dict, expected_range: tuple, save_path: str) -> None:
    """Per-benchmark normalized timing with 20-40% shaded band."""
    fig, ax = plt.subplots(figsize=(12, 6))
    benchmarks = list(aggregated.keys())
    timings = [aggregated[b]['mean_normalized_timing'] or 0 for b in benchmarks]
    errors = [aggregated[b]['timing_std'] or 0 for b in benchmarks]

    colors = ['#2196F3', '#4CAF50', '#FF9800']
    x = np.arange(len(benchmarks))
    bars = ax.bar(x, timings, yerr=errors, capsize=5, color=colors[:len(benchmarks)], alpha=0.8)

    ax.axhspan(expected_range[0], expected_range[1], alpha=0.2, color='green', label='Expected Range (20-40%)')
    ax.axhline(y=expected_range[0], color='green', linestyle='--', linewidth=1)
    ax.axhline(y=expected_range[1], color='green', linestyle='--', linewidth=1)

    ax.set_xticks(x)
    ax.set_xticklabels([aggregated[b]['expected_range'][0] and b.title() for b in benchmarks])
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('Normalized Peak Timing (%)')
    ax.set_title('Crystallization Timing Across Benchmarks')
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    for bar, t in zip(bars, timings):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{t:.1f}%', ha='center', va='bottom', fontsize=10)

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_wga_curves_overlay(wga_curves: dict, configs: dict, save_path: str) -> None:
    """3-panel plot showing WGA curves for all benchmarks (normalized x-axis)."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    benchmarks = list(wga_curves.keys())
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#E91E63']

    for idx, benchmark in enumerate(benchmarks):
        ax = axes[idx] if idx < 3 else axes[-1]
        seeds_data = wga_curves[benchmark]
        total_epochs = configs[benchmark].total_epochs

        for seed, wga in seeds_data.items():
            x_norm = np.linspace(0, 100, len(wga))
            ax.plot(x_norm, wga, color=colors[seed % len(colors)], alpha=0.7, label=f'Seed {seed}')

        ax.axvspan(20, 40, alpha=0.15, color='green')
        ax.set_xlabel('Training Progress (%)')
        ax.set_ylabel('WGA')
        ax.set_title(f'{benchmark.title()} ({total_epochs} epochs)')
        ax.grid(True, alpha=0.3)
        if idx == 0:
            ax.legend(fontsize=8)

    fig.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_timing_distribution(results: dict, save_path: str) -> None:
    """Box plot of normalized timing across seeds for each benchmark."""
    fig, ax = plt.subplots(figsize=(10, 6))
    benchmarks = list(results.keys())
    timing_data = []

    for bm in benchmarks:
        timings = [r['normalized_timing_percent'] for r in results[bm]['runs']
                   if r['detected'] and r['normalized_timing_percent'] is not None]
        timing_data.append(timings if timings else [0])

    bp = ax.boxplot(timing_data, patch_artist=True)
    colors = ['#2196F3', '#4CAF50', '#FF9800']
    for patch, color in zip(bp['boxes'], colors[:len(benchmarks)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.axhspan(20, 40, alpha=0.2, color='green', label='Expected Range')
    ax.set_xticks(range(1, len(benchmarks) + 1))
    ax.set_xticklabels([b.title() for b in benchmarks])
    ax.set_xlabel('Benchmark')
    ax.set_ylabel('Normalized Timing (%)')
    ax.set_title('Timing Distribution Across Seeds')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_cross_benchmark_regression(aggregated: dict, configs: dict, save_path: str) -> None:
    """Scatter: absolute epoch vs total epochs with regression line."""
    fig, ax = plt.subplots(figsize=(10, 6))

    x_vals, y_vals = [], []
    labels = []
    for bm, agg in aggregated.items():
        if agg['mean_normalized_timing'] is not None:
            total_epochs = configs[bm].total_epochs
            abs_epoch = agg['mean_normalized_timing'] * total_epochs / 100.0
            x_vals.append(total_epochs)
            y_vals.append(abs_epoch)
            labels.append(bm.title())

    colors = ['#2196F3', '#4CAF50', '#FF9800']
    ax.scatter(x_vals, y_vals, c=colors[:len(x_vals)], s=150, alpha=0.8, edgecolors='black')

    for i, label in enumerate(labels):
        ax.annotate(label, (x_vals[i], y_vals[i]), xytext=(5, 5), textcoords='offset points')

    if len(x_vals) >= 2:
        z = np.polyfit(x_vals, y_vals, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(x_vals), max(x_vals), 100)
        ax.plot(x_line, p(x_line), 'r--', alpha=0.5, label=f'Fit: y={z[0]:.3f}x + {z[1]:.1f}')
        ax.legend()

    ax.set_xlabel('Total Training Epochs')
    ax.set_ylabel('Absolute Peak Epoch')
    ax.set_title('Crystallization Timing vs Training Duration')
    ax.grid(True, alpha=0.3)

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_gate_dashboard(gate_result: dict, aggregated: dict, save_path: str) -> None:
    """Summary dashboard showing pass/fail status for each criterion."""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')

    status = gate_result['status']
    metrics = gate_result['metrics']
    color = '#4CAF50' if status == 'PASS' else ('#FF9800' if status == 'CONDITIONAL' else '#F44336')

    ax.text(0.5, 0.9, f'H-M4 Gate: {status}', fontsize=24, ha='center', va='top',
            fontweight='bold', color=color, transform=ax.transAxes)

    y = 0.75
    for key, value in metrics.items():
        ax.text(0.1, y, f'{key}:', fontsize=14, ha='left', va='top', transform=ax.transAxes)
        ax.text(0.6, y, f'{value}', fontsize=14, ha='left', va='top', transform=ax.transAxes)
        y -= 0.08

    ax.text(0.5, 0.25, 'Per-Benchmark Summary:', fontsize=16, ha='center', va='top',
            fontweight='bold', transform=ax.transAxes)

    y = 0.18
    for bm, agg in aggregated.items():
        timing = agg['mean_normalized_timing']
        status_str = 'IN' if agg['in_expected_range'] else 'OUT'
        ax.text(0.1, y, f'{bm.title()}: {timing:.1f}% ({status_str})',
                fontsize=12, ha='left', va='top', transform=ax.transAxes)
        y -= 0.06

    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
