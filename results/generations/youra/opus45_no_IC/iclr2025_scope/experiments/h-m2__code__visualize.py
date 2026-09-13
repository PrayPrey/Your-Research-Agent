"""H-M2: Visualization - bar chart, boxplot, scatter, heatmap."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_gate_bar(high_retention: np.ndarray, low_retention: np.ndarray,
                  gate_result: dict, output_dir: str) -> str:
    """Mandatory: Bar chart comparing high vs low entropy retention."""
    fig, ax = plt.subplots(figsize=(8, 6))

    means = [high_retention.mean(), low_retention.mean()]
    sems = [high_retention.std() / np.sqrt(len(high_retention)),
            low_retention.std() / np.sqrt(len(low_retention))]

    bars = ax.bar(['High Entropy', 'Low Entropy'], means, yerr=sems,
                  capsize=5, color=['#2ecc71', '#e74c3c'], alpha=0.8)

    ax.set_ylabel('Accuracy Retention (Evicted / Full)')
    ax.set_title(f"H-M2: Entropy-Eviction Tolerance\np={gate_result.get('p_value', 0):.4f}, d={gate_result.get('cohens_d', 0):.3f}")
    ax.set_ylim(0, 1.2)

    gate_pass = gate_result.get('gate_pass', False)
    ax.text(0.5, 0.95, f"GATE: {'PASS' if gate_pass else 'FAIL'}",
            transform=ax.transAxes, ha='center', fontsize=14,
            color='green' if gate_pass else 'red', fontweight='bold')

    plt.tight_layout()
    path = os.path.join(output_dir, 'gate_bar.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_boxplot(high_retention: np.ndarray, low_retention: np.ndarray,
                 output_dir: str) -> str:
    """Boxplot of retention distribution by group."""
    fig, ax = plt.subplots(figsize=(8, 6))

    data = [high_retention, low_retention]
    bp = ax.boxplot(data, labels=['High Entropy', 'Low Entropy'], patch_artist=True)

    colors = ['#2ecc71', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel('Accuracy Retention')
    ax.set_title('H-M2: Retention Distribution by Entropy Group')

    plt.tight_layout()
    path = os.path.join(output_dir, 'boxplot.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_scatter_entropy_retention(entropy: np.ndarray, retention: np.ndarray,
                                   group_mask: np.ndarray, output_dir: str) -> str:
    """Scatter plot: per-sample entropy vs retention."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(entropy[group_mask], retention[group_mask],
               c='#2ecc71', alpha=0.6, label='High Entropy', s=30)
    ax.scatter(entropy[~group_mask], retention[~group_mask],
               c='#e74c3c', alpha=0.6, label='Low Entropy', s=30)

    z = np.polyfit(entropy, retention, 1)
    p = np.poly1d(z)
    x_line = np.linspace(entropy.min(), entropy.max(), 100)
    ax.plot(x_line, p(x_line), 'k--', alpha=0.5, label=f'Trend')

    ax.set_xlabel('Sample Entropy (mean over layers/heads)')
    ax.set_ylabel('Accuracy Retention')
    ax.set_title('H-M2: Entropy vs Eviction Tolerance')
    ax.legend()

    plt.tight_layout()
    path = os.path.join(output_dir, 'scatter_entropy_retention.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_heatmap_domain_ratio(retention_by_domain_ratio: dict, output_dir: str) -> str:
    """Heatmap: domain x ratio mean retention."""
    domains = list(retention_by_domain_ratio.keys())
    ratios = list(retention_by_domain_ratio[domains[0]].keys())

    data = np.array([[retention_by_domain_ratio[d][r] for r in ratios] for d in domains])

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(data, annot=True, fmt='.3f', cmap='RdYlGn',
                xticklabels=[f'{r*100:.0f}%' for r in ratios],
                yticklabels=[d[:20] + '...' if len(d) > 20 else d for d in domains],
                ax=ax)

    ax.set_xlabel('Retention Ratio')
    ax.set_ylabel('Domain')
    ax.set_title('H-M2: Mean Retention by Domain and Ratio')

    plt.tight_layout()
    path = os.path.join(output_dir, 'heatmap_domain_ratio.png')
    plt.savefig(path, dpi=150)
    plt.close()
    return path
