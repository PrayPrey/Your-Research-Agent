"""Visualization for H-M3."""

import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List
from config import FIGURES_DIR, DEGRADATION_THRESHOLD


def plot_degradation_bar(transfer_results: List[dict], out_path: str = None) -> None:
    """Bar chart of AUROC degradation per transfer pair."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "degradation_bar.png")

    labels = [f"{r['source'][:3]}→{r['target'][:3]}" for r in transfer_results]
    degradations = [r["degradation"] for r in transfer_results]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(labels)), degradations, color='steelblue')

    for i, bar in enumerate(bars):
        if degradations[i] > DEGRADATION_THRESHOLD:
            bar.set_color('coral')

    ax.axhline(y=DEGRADATION_THRESHOLD, color='red', linestyle='--', label=f'Threshold ({DEGRADATION_THRESHOLD})')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('AUROC Degradation (source - target)')
    ax.set_xlabel('Transfer Direction')
    ax.set_title('H-M3: Within-Cluster Threshold Transfer Degradation')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_transfer_heatmap(transfer_results: List[dict], benchmarks: List[str], out_path: str = None) -> None:
    """Heatmap of transfer AUROC."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "transfer_heatmap.png")

    n = len(benchmarks)
    matrix = np.full((n, n), np.nan)

    for r in transfer_results:
        i = benchmarks.index(r["source"])
        j = benchmarks.index(r["target"])
        matrix[i, j] = r["target_auroc"]

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap='RdYlGn', vmin=0.5, vmax=1.0)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([b[:6] for b in benchmarks], rotation=45, ha='right')
    ax.set_yticklabels([b[:6] for b in benchmarks])
    ax.set_xlabel('Target')
    ax.set_ylabel('Source')
    ax.set_title('H-M3: Transfer AUROC (Source→Target)')

    for i in range(n):
        for j in range(n):
            if not np.isnan(matrix[i, j]):
                ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center', fontsize=8)

    plt.colorbar(im, ax=ax, label='AUROC')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
