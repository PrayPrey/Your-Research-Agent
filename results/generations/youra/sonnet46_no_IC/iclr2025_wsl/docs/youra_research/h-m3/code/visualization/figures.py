"""Four required figures for H-M3 results."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_gate_comparison(results, stats, out_path):
    """Fig 1: Bar chart mean acc_latent vs acc_ws with p-value annotation."""
    fig, ax = plt.subplots(figsize=(6, 5))
    methods = ['Latent Interp.', 'Weight-Space Avg.']
    means = [stats['mean_acc_latent'], stats['mean_acc_ws']]
    stds = [
        np.std([r['acc_latent'] for r in results]),
        np.std([r['acc_ws'] for r in results]),
    ]
    colors = ['#2196F3', '#FF9800']
    bars = ax.bar(methods, means, yerr=stds, color=colors, alpha=0.8, capsize=5)
    gate_str = 'PASS' if stats['gate_pass'] else 'DOCUMENT'
    ax.set_title(f"Gate: {gate_str} (p={stats['p_value']:.4f})")
    ax.set_ylabel('Mean Accuracy')
    ax.set_ylim(0, max(means) * 1.2)
    ax.annotate(f"p={stats['p_value']:.4f}", xy=(0.5, 0.92), xycoords='axes fraction',
                ha='center', fontsize=11, color='black')
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def plot_task_stratified(stats, out_path):
    """Fig 2: Per-task mean delta bar chart."""
    fig, ax = plt.subplots(figsize=(7, 5))
    tasks = sorted(stats['per_task'].keys())
    deltas = [stats['per_task'][t]['mean_delta'] for t in tasks]
    stds = [stats['per_task'][t]['std_delta'] for t in tasks]
    colors = ['#4CAF50' if d > 0 else '#F44336' for d in deltas]
    ax.bar(tasks, deltas, yerr=stds, color=colors, alpha=0.8, capsize=5)
    ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_title('Mean Δ Accuracy per Task (Latent − Weight-Space)')
    ax.set_ylabel('Mean Δ Accuracy')
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def plot_delta_histogram(results, stats, out_path):
    """Fig 3: Histogram of per-pair delta with mean line."""
    deltas = [r['acc_latent'] - r['acc_ws'] for r in results]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.hist(deltas, bins=40, color='#9C27B0', alpha=0.7, edgecolor='white')
    ax.axvline(0, color='black', linewidth=1.0, linestyle='--', label='δ=0')
    ax.axvline(stats['mean_delta'], color='red', linewidth=1.5, linestyle='-',
               label=f"mean={stats['mean_delta']:.4f}")
    ax.set_title('Per-Pair Δ Accuracy Distribution')
    ax.set_xlabel('Δ Accuracy (Latent − Weight-Space)')
    ax.set_ylabel('Count')
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def plot_pair_scatter(results, out_path):
    """Fig 4: Scatter of (acc_a, acc_b) colored by delta sign."""
    fig, ax = plt.subplots(figsize=(6, 6))
    for r in results:
        delta = r['acc_latent'] - r['acc_ws']
        color = '#4CAF50' if delta > 0 else '#F44336'
        ax.scatter(r.get('acc_a', 0.5), r.get('acc_b', 0.5),
                   c=color, alpha=0.4, s=10)
    ax.set_xlabel('Model A Accuracy')
    ax.set_ylabel('Model B Accuracy')
    ax.set_title('Pair Accuracy Scatter (green=latent wins, red=ws wins)')
    fig.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=100, bbox_inches='tight')
    plt.close(fig)


def generate_all_figures(results, stats, figures_dir):
    os.makedirs(figures_dir, exist_ok=True)
    plot_gate_comparison(results, stats, os.path.join(figures_dir, 'gate_comparison.png'))
    plot_task_stratified(stats, os.path.join(figures_dir, 'task_stratified.png'))
    plot_delta_histogram(results, stats, os.path.join(figures_dir, 'delta_histogram.png'))
    plot_pair_scatter(results, os.path.join(figures_dir, 'pair_scatter.png'))
    print(f"  Figures saved to: {figures_dir}")
