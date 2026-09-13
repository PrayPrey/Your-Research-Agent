"""Figure generation for H-C1: 3-way convergence visualization."""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
from pathlib import Path

import config

METHODS = ["stats", "mlp", "nfn"]
METHOD_LABELS = {"stats": "Statistics", "mlp": "MLP", "nfn": "NFN"}
COLORS = {"stats": "#3498db", "mlp": "#e74c3c", "nfn": "#2ecc71"}


def plot_r2_comparison(results: List[Dict], out_path: str) -> None:
    """Bar chart: all 3 methods mean R2 with error bars at N=5000."""
    means = {m: np.mean([r[f"r2_{m}"] for r in results]) for m in METHODS}
    stds = {m: np.std([r[f"r2_{m}"] for r in results]) for m in METHODS}

    fig, ax = plt.subplots(figsize=(7, 5))
    x = np.arange(len(METHODS))
    colors = [COLORS[m] for m in METHODS]
    bars = ax.bar(x, [means[m] for m in METHODS],
                  yerr=[stds[m] for m in METHODS],
                  capsize=5, color=colors, edgecolor='black')

    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS[m] for m in METHODS])
    ax.set_ylabel('R² Score')
    ax.set_title(f'R² Comparison at N={config.N_GATE} (10 seeds)')
    ax.set_ylim(0, 1.1)

    for bar, m in zip(bars, METHODS):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{means[m]:.3f}', ha='center', va='bottom', fontsize=10)

    max_val = max(means.values())
    min_val = min(means.values())
    ax.axhline(y=max_val - config.R2_PAIR_DELTA_MAX, color='gray',
               linestyle='--', alpha=0.5, label=f'±{config.R2_PAIR_DELTA_MAX} threshold')
    ax.axhline(y=min_val + config.R2_PAIR_DELTA_MAX, color='gray',
               linestyle='--', alpha=0.5)

    ax.legend(loc='lower right')

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_pairwise_heatmap(deltas: Dict[str, float], out_path: str) -> None:
    """3x3 heatmap of |R2_i - R2_j| for all method pairs."""
    matrix = np.zeros((3, 3))
    idx = {m: i for i, m in enumerate(METHODS)}

    for key, val in deltas.items():
        a, b = key.split("_")
        matrix[idx[a], idx[b]] = val
        matrix[idx[b], idx[a]] = val

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(matrix, cmap='YlOrRd', vmin=0, vmax=max(0.1, matrix.max()))

    ax.set_xticks(np.arange(3))
    ax.set_yticks(np.arange(3))
    ax.set_xticklabels([METHOD_LABELS[m] for m in METHODS])
    ax.set_yticklabels([METHOD_LABELS[m] for m in METHODS])

    for i in range(3):
        for j in range(3):
            color = 'white' if matrix[i, j] > 0.05 else 'black'
            ax.text(j, i, f'{matrix[i,j]:.3f}', ha='center', va='center', color=color)

    plt.colorbar(im, ax=ax, label='|ΔR²|')
    ax.set_title(f'Pairwise R² Differences (threshold: {config.R2_PAIR_DELTA_MAX})')

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
