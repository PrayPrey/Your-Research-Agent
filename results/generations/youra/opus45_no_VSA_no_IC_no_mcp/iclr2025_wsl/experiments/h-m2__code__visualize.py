from typing import Dict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


def plot_learning_curves(stats: Dict, out_path: str) -> None:
    """AUC vs fraction with error bars."""
    fractions = sorted(stats.keys())

    plt.figure(figsize=(8, 6))
    colors = {'mlp': 'gray', 'dws': 'blue', 'nft': 'orange'}
    markers = {'mlp': 'o', 'dws': 's', 'nft': '^'}

    for model_type in ['mlp', 'dws', 'nft']:
        means = [stats[f][model_type]['auc_mean'] for f in fractions]
        stds = [stats[f][model_type]['auc_std'] for f in fractions]
        plt.errorbar(
            fractions, means, yerr=stds,
            label=model_type.upper(),
            color=colors[model_type],
            marker=markers[model_type],
            capsize=3,
            linewidth=2,
            markersize=8,
        )

    plt.xlabel('Training Data Fraction')
    plt.ylabel('Macro AUC (OVR)')
    plt.title('Sample Efficiency: AUC vs Training Data Fraction')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_25pct_bar(stats: Dict, out_path: str) -> None:
    """Bar chart at 25% data."""
    models = ['mlp', 'dws', 'nft']
    means = [stats[0.25][m]['auc_mean'] for m in models]
    stds = [stats[0.25][m]['auc_std'] for m in models]
    colors = ['gray', 'blue', 'orange']

    plt.figure(figsize=(6, 5))
    bars = plt.bar([m.upper() for m in models], means, yerr=stds, capsize=5, color=colors)
    plt.ylabel('Macro AUC')
    plt.title('Performance at 25% Training Data')
    plt.ylim(0, 1.1)

    for bar, mean in zip(bars, means):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f'{mean:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_gap_closure(gap: Dict, out_path: str) -> None:
    """DWS-NFT gap vs fraction."""
    fractions = sorted(gap.keys())
    gaps = [gap[f] for f in fractions]

    plt.figure(figsize=(7, 5))
    plt.bar([f'{f*100:.0f}%' for f in fractions], gaps, color='green', alpha=0.7)
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.ylabel('DWS - NFT (AUC difference)')
    plt.xlabel('Training Data Fraction')
    plt.title('Gap Closure: DWS Advantage vs NFT')

    for i, g in enumerate(gaps):
        plt.text(i, g + 0.002 if g >= 0 else g - 0.01, f'{g:.3f}', ha='center')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_auc_boxplots(results: Dict, out_path: str) -> None:
    """Box plots of AUC by model and fraction."""
    fractions = sorted(results.keys())
    models = ['mlp', 'dws', 'nft']

    fig, axes = plt.subplots(1, len(fractions), figsize=(12, 5), sharey=True)

    for ax, fraction in zip(axes, fractions):
        data = [[r['auc'] for r in results[fraction][m]] for m in models]
        bp = ax.boxplot(data, labels=[m.upper() for m in models], patch_artist=True)
        colors = ['gray', 'blue', 'orange']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.6)
        ax.set_title(f'{fraction*100:.0f}% Data')
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel('Macro AUC')
    fig.suptitle('AUC Distribution Across Seeds', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_gate_metrics(stats: Dict, criteria: Dict, out_path: str) -> None:
    """Summary figure for gate decision."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    # 1. AUC at 25%
    ax = axes[0]
    models = ['mlp', 'dws', 'nft']
    means = [stats[0.25][m]['auc_mean'] for m in models]
    colors = ['gray', 'blue', 'orange']
    bars = ax.bar([m.upper() for m in models], means, color=colors)
    ax.set_ylabel('Macro AUC')
    ax.set_title(f"25% Data: DWS > NFT? {criteria['dws_gt_nft_at_25pct']}")
    ax.set_ylim(0, 1.1)

    # 2. Gap closure
    ax = axes[1]
    fractions = sorted(stats.keys())
    gaps = [stats[f]['dws']['auc_mean'] - stats[f]['nft']['auc_mean'] for f in fractions]
    ax.plot([f*100 for f in fractions], gaps, 'go-', linewidth=2, markersize=10)
    ax.axhline(0, color='black', linestyle='--')
    ax.set_xlabel('Data %')
    ax.set_ylabel('DWS - NFT')
    ax.set_title(f"Gap Narrows? {criteria['gap_narrows_at_100pct']}")

    # 3. Both > MLP
    ax = axes[2]
    for f in fractions:
        x_pos = f * 100
        for i, (m, c) in enumerate(zip(['dws', 'nft'], ['blue', 'orange'])):
            y = stats[f][m]['auc_mean'] - stats[f]['mlp']['auc_mean']
            ax.bar(x_pos + (i-0.5)*5, y, width=4, color=c, label=m.upper() if f == fractions[0] else '')
    ax.axhline(0, color='red', linestyle='--', label='MLP baseline')
    ax.set_xlabel('Data %')
    ax.set_ylabel('AUC - MLP')
    ax.set_title(f"Both > MLP? {criteria['both_gt_mlp']}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
