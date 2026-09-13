"""Figure generation for H-M2."""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict
from pathlib import Path

import config


def plot_gate_comparison(results: List[Dict], n: int, out_path: str) -> None:
    """Bar chart: NFN vs MLP mean R2 with error bars at given N."""
    rows = [r for r in results if r["n"] == n]
    nfn_scores = [r["r2_nfn"] for r in rows]
    mlp_scores = [r["r2_mlp"] for r in rows]

    means = [np.mean(nfn_scores), np.mean(mlp_scores)]
    stds = [np.std(nfn_scores), np.std(mlp_scores)]

    fig, ax = plt.subplots(figsize=(6, 5))
    x = [0, 1]
    colors = ['#2ecc71', '#e74c3c']
    bars = ax.bar(x, means, yerr=stds, capsize=5, color=colors, edgecolor='black')

    ax.set_xticks(x)
    ax.set_xticklabels(['NFN', 'MLP'])
    ax.set_ylabel('R² Score')
    ax.set_title(f'Gate Comparison at N={n}')
    ax.set_ylim(0, 1)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{mean:.3f}', ha='center', va='bottom', fontsize=10)

    delta = means[0] - means[1]
    ax.text(0.5, 0.05, f'Delta: {delta:.3f}', transform=ax.transAxes,
            ha='center', fontsize=12, fontweight='bold')

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_learning_curve(results: List[Dict], n_values: List[int], out_path: str) -> None:
    """R2 vs N for both methods."""
    nfn_means, nfn_stds = [], []
    mlp_means, mlp_stds = [], []

    for n in n_values:
        rows = [r for r in results if r["n"] == n]
        nfn_scores = [r["r2_nfn"] for r in rows]
        mlp_scores = [r["r2_mlp"] for r in rows]
        nfn_means.append(np.mean(nfn_scores))
        nfn_stds.append(np.std(nfn_scores))
        mlp_means.append(np.mean(mlp_scores))
        mlp_stds.append(np.std(mlp_scores))

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.errorbar(n_values, nfn_means, yerr=nfn_stds, marker='o', label='NFN', capsize=3)
    ax.errorbar(n_values, mlp_means, yerr=mlp_stds, marker='s', label='MLP', capsize=3)

    ax.set_xscale('log')
    ax.set_xlabel('Training Set Size (N)')
    ax.set_ylabel('R² Score')
    ax.set_title('Learning Curve: NFN vs MLP')
    ax.legend()
    ax.grid(True, alpha=0.3)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_seed_scatter(results: List[Dict], n: int, out_path: str) -> None:
    """Per-seed scatter: NFN R2 vs MLP R2."""
    rows = [r for r in results if r["n"] == n]
    nfn_scores = [r["r2_nfn"] for r in rows]
    mlp_scores = [r["r2_mlp"] for r in rows]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(mlp_scores, nfn_scores, s=60, alpha=0.7, edgecolors='black')

    lim = [min(min(mlp_scores), min(nfn_scores)) - 0.05,
           max(max(mlp_scores), max(nfn_scores)) + 0.05]
    ax.plot(lim, lim, 'k--', alpha=0.5, label='y=x')

    ax.set_xlabel('MLP R²')
    ax.set_ylabel('NFN R²')
    ax.set_title(f'Per-Seed Comparison at N={n}')
    ax.legend()
    ax.set_xlim(lim)
    ax.set_ylim(lim)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_box_distribution(results: List[Dict], n: int, out_path: str) -> None:
    """Box plot of R2 distributions at given N."""
    rows = [r for r in results if r["n"] == n]
    nfn_scores = [r["r2_nfn"] for r in rows]
    mlp_scores = [r["r2_mlp"] for r in rows]

    fig, ax = plt.subplots(figsize=(6, 5))
    bp = ax.boxplot([nfn_scores, mlp_scores], patch_artist=True)
    ax.set_xticklabels(['NFN', 'MLP'])

    colors = ['#2ecc71', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)

    ax.set_ylabel('R² Score')
    ax.set_title(f'R² Distribution at N={n}')

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
