"""Visualization suite for H-M4."""

import os
import importlib.util
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

# Import H-M4 config using importlib
H_M4_PATH = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("m4_config", os.path.join(H_M4_PATH, "config.py"))
m4_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m4_config)

FIGURES_DIR = m4_config.FIGURES_DIR
DEGRADATION_THRESHOLD = m4_config.DEGRADATION_THRESHOLD
JS_DIVERGENCE = m4_config.JS_DIVERGENCE


def plot_gate_bar(mean_degradation: float, threshold: float, out_path: str) -> None:
    """Bar chart showing mean degradation vs gate threshold."""
    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ['#e74c3c' if mean_degradation > threshold else '#3498db']
    ax.bar(['Mean Degradation'], [mean_degradation], color=colors, edgecolor='black', linewidth=2)
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')

    ax.set_ylabel('AUROC Degradation', fontsize=12)
    ax.set_title('H-M4: Cross-Cluster Transfer Degradation\n(Gate: Mean > 0.15)', fontsize=14)
    ax.legend()
    ax.set_ylim(0, max(mean_degradation * 1.3, threshold * 1.5))

    # Add value label
    ax.text(0, mean_degradation + 0.01, f'{mean_degradation:.3f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_within_vs_cross_box(within: List[float], cross: List[float], out_path: str) -> None:
    """Box plot comparing H-M3 (within-cluster) vs H-M4 (cross-cluster) degradations."""
    fig, ax = plt.subplots(figsize=(8, 6))

    data = [within, cross]
    bp = ax.boxplot(data, labels=['Within-Cluster\n(H-M3)', 'Cross-Cluster\n(H-M4)'], patch_artist=True)

    colors = ['#3498db', '#e74c3c']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('AUROC Degradation', fontsize=12)
    ax.set_title('Transfer Degradation: Within vs Cross Cluster', fontsize=14)
    ax.axhline(y=0.08, color='blue', linestyle=':', alpha=0.5, label='H-M3 threshold (0.08)')
    ax.axhline(y=0.15, color='red', linestyle='--', alpha=0.5, label='H-M4 threshold (0.15)')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_per_pair_degradation(transfer_results: List[dict], out_path: str) -> None:
    """Bar chart of per-pair degradation."""
    fig, ax = plt.subplots(figsize=(10, 6))

    pairs = [f"{r['source']}→{r['target']}" for r in transfer_results]
    degradations = [r['degradation'] for r in transfer_results]

    colors = ['#e74c3c' if d > DEGRADATION_THRESHOLD else '#f39c12' for d in degradations]
    ax.bar(pairs, degradations, color=colors, edgecolor='black', linewidth=1.5)
    ax.axhline(y=DEGRADATION_THRESHOLD, color='red', linestyle='--', linewidth=2, label=f'Threshold ({DEGRADATION_THRESHOLD})')

    ax.set_ylabel('AUROC Degradation', fontsize=12)
    ax.set_xlabel('Transfer Pair', fontsize=12)
    ax.set_title('H-M4: Per-Pair Cross-Cluster Degradation', fontsize=14)
    ax.legend()
    plt.xticks(rotation=15, ha='right')

    # Add value labels
    for i, (pair, deg) in enumerate(zip(pairs, degradations)):
        ax.text(i, deg + 0.01, f'{deg:.3f}', ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_js_divergence_scatter(transfer_results: List[dict], js_map: Dict, out_path: str) -> None:
    """Scatter plot: JS-divergence vs degradation."""
    fig, ax = plt.subplots(figsize=(8, 6))

    js_values = []
    degradations = []
    labels = []

    for r in transfer_results:
        pair = (r['source'], r['target'])
        if pair in js_map:
            js_values.append(js_map[pair])
            degradations.append(r['degradation'])
            labels.append(f"{r['source']}→{r['target']}")

    ax.scatter(js_values, degradations, s=100, c='#e74c3c', edgecolors='black', linewidth=1.5, alpha=0.8)

    for i, label in enumerate(labels):
        ax.annotate(label, (js_values[i], degradations[i]), textcoords="offset points", xytext=(5, 5), fontsize=9)

    ax.set_xlabel('JS-Divergence', fontsize=12)
    ax.set_ylabel('AUROC Degradation', fontsize=12)
    ax.set_title('JS-Divergence vs Transfer Degradation', fontsize=14)
    ax.axhline(y=DEGRADATION_THRESHOLD, color='red', linestyle='--', alpha=0.5, label=f'Gate threshold ({DEGRADATION_THRESHOLD})')
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def generate_all_figures(transfer_results: List[dict], agg: dict, within_degradations: List[float]) -> None:
    """Generate all H-M4 figures."""
    cross_degradations = [r["degradation"] for r in transfer_results]

    plot_gate_bar(agg["mean_degradation"], DEGRADATION_THRESHOLD, os.path.join(FIGURES_DIR, "gate_bar.png"))
    plot_within_vs_cross_box(within_degradations, cross_degradations, os.path.join(FIGURES_DIR, "within_vs_cross_box.png"))
    plot_per_pair_degradation(transfer_results, os.path.join(FIGURES_DIR, "per_pair_degradation.png"))
    plot_js_divergence_scatter(transfer_results, JS_DIVERGENCE, os.path.join(FIGURES_DIR, "js_divergence_scatter.png"))
