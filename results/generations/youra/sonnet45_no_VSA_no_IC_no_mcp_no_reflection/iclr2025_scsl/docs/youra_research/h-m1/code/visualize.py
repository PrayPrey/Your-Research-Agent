"""Visualization functions for layer-neuron analysis."""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict
from pathlib import Path


def plot_layer_means(
    layer_means: Dict[str, float],
    layer_rho_j: Dict[str, np.ndarray],
    save_path: Path
):
    """Bar chart with 95% confidence intervals."""
    layers = ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']
    means = [layer_means[l] for l in layers]
    cis = [1.96 * stats.sem(layer_rho_j[l]) for l in layers]

    plt.figure(figsize=(10, 6))
    plt.bar(layers, means, yerr=cis, capsize=5, alpha=0.7)
    plt.ylabel('Mean Pearson Correlation (ρ_j)', fontsize=12)
    plt.xlabel('Layer', fontsize=12)
    plt.title('Layer-wise Spurious Correlation (Early > Late)', fontsize=14)
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_heatmap(
    layer_rho_j: Dict[str, np.ndarray],
    save_path: Path,
    max_neurons_per_layer: int = 100
):
    """Heatmap (layers × neurons) showing individual ρ_j values."""
    data = []
    for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
        rho = layer_rho_j[layer_name]
        if len(rho) > max_neurons_per_layer:
            # Subsample evenly
            indices = np.linspace(0, len(rho)-1, max_neurons_per_layer, dtype=int)
            rho = rho[indices]
        data.append(rho)

    # Pad to same length
    max_len = max(len(row) for row in data)
    data_padded = np.array([
        np.pad(row, (0, max_len - len(row)), constant_values=np.nan)
        for row in data
    ])

    plt.figure(figsize=(12, 6))
    sns.heatmap(
        data_padded,
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        yticklabels=['conv1', 'layer1', 'layer2', 'layer3', 'layer4'],
        cbar_kws={'label': 'Pearson ρ_j'},
        xticklabels=False
    )
    plt.xlabel('Neuron Index', fontsize=12)
    plt.ylabel('Layer', fontsize=12)
    plt.title('Neuron-Spurious Correlation (Per Layer)', fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_cdf(layer_rho_j: Dict[str, np.ndarray], save_path: Path):
    """Cumulative distribution of ρ_j for early vs late groups."""
    early = np.concatenate([layer_rho_j['conv1'], layer_rho_j['layer1']])
    late = np.concatenate([layer_rho_j['layer3'], layer_rho_j['layer4']])

    plt.figure(figsize=(10, 6))
    plt.hist(early, bins=50, cumulative=True, density=True,
             alpha=0.6, label='Early (conv1, layer1)', histtype='step', linewidth=2)
    plt.hist(late, bins=50, cumulative=True, density=True,
             alpha=0.6, label='Late (layer3, layer4)', histtype='step', linewidth=2)
    plt.xlabel('Pearson Correlation (ρ_j)', fontsize=12)
    plt.ylabel('Cumulative Probability', fontsize=12)
    plt.title('CDF: Early vs Late Layer Correlations', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
