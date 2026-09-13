"""Visualization functions for h-m1 mechanism validation."""

import matplotlib.pyplot as plt


def plot_beam_count_over_steps(beam_counts, k, save_path):
    """Line plot of beam count per generation step."""
    plt.figure(figsize=(10, 5))
    plt.plot(beam_counts, marker='o', label=f'k={k}')
    plt.axhline(y=k, color='red', linestyle='--', label='Expected')
    plt.xlabel('Generation Step')
    plt.ylabel('Active Beam Count')
    plt.title(f'Beam Count Maintenance (k={k})')
    plt.legend()
    plt.grid(True)
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_diversity_by_k(results, save_path):
    """Bar chart of diversity ratio for each k."""
    k_vals = sorted(results.keys())
    avg_divs = [results[k]['avg_diversity'] for k in k_vals]

    plt.figure(figsize=(8, 5))
    plt.bar([str(k) for k in k_vals], avg_divs, color='skyblue')
    plt.axhline(y=0.6, color='red', linestyle='--', label='Target (60%)')
    plt.xlabel('Beam Width (k)')
    plt.ylabel('Diversity Ratio')
    plt.title('Output Diversity vs Beam Width')
    plt.legend()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_compute_time_vs_k(results, save_path):
    """Bar chart of generation time for each k."""
    k_vals = sorted(results.keys())
    times = [results[k]['time_sec'] for k in k_vals]

    plt.figure(figsize=(8, 5))
    plt.bar([str(k) for k in k_vals], times, color='orange')
    plt.xlabel('Beam Width (k)')
    plt.ylabel('Generation Time (seconds)')
    plt.title('Computational Cost vs Beam Width')
    plt.savefig(save_path, dpi=150)
    plt.close()
