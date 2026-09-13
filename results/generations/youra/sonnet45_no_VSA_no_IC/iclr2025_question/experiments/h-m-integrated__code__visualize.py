"""Visualization suite for h-m-integrated."""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List


def plot_gate_metrics_scatter(results: Dict, save_path: str):
    """
    Gate metrics scatter: Spearman vs AUROC.

    X-axis: Spearman rho
    Y-axis: AUROC
    Lines: threshold at rho=0.2, AUROC=0.55
    """
    plt.figure(figsize=(8, 6))

    methods = list(results.keys())
    spearman_vals = [results[m]["spearman_rho"] for m in methods]
    auroc_vals = [results[m]["auroc"] for m in methods]
    colors = ["gray" if m == "mc_k1" else "C0" for m in methods]

    plt.scatter(spearman_vals, auroc_vals, c=colors, s=100, alpha=0.7)

    # Threshold lines
    plt.axhline(y=0.55, color='r', linestyle='--', label='AUROC threshold (0.55)')
    plt.axvline(x=0.2, color='b', linestyle='--', label='Spearman threshold (0.2)')

    # Labels
    for i, method in enumerate(methods):
        plt.annotate(method, (spearman_vals[i], auroc_vals[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

    plt.xlabel("Spearman ρ")
    plt.ylabel("AUROC")
    plt.title("Gate Metrics: Spearman vs AUROC")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_spearman_comparison(results: Dict, save_path: str):
    """
    Spearman comparison bar chart.

    X-axis: Methods
    Y-axis: Spearman rho
    Line: threshold at 0.2
    """
    plt.figure(figsize=(10, 6))

    methods = list(results.keys())
    spearman_vals = [results[m]["spearman_rho"] for m in methods]
    colors = ["gray" if m == "mc_k1" else "C0" for m in methods]

    bars = plt.bar(methods, spearman_vals, color=colors, alpha=0.7)
    plt.axhline(y=0.2, color='r', linestyle='--', label='Threshold (0.2)')

    plt.xlabel("UQ Method")
    plt.ylabel("Spearman ρ")
    plt.title("Spearman Correlation Comparison")
    plt.xticks(rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_ause_vs_auroc(results: Dict, save_path: str):
    """
    AUSE vs AUROC scatter.

    X-axis: AUSE (lower better)
    Y-axis: AUROC (higher better)
    """
    plt.figure(figsize=(8, 6))

    methods = list(results.keys())
    ause_vals = [results[m]["ause"] for m in methods]
    auroc_vals = [results[m]["auroc"] for m in methods]
    colors = ["gray" if m == "mc_k1" else "C0" for m in methods]

    plt.scatter(ause_vals, auroc_vals, c=colors, s=100, alpha=0.7)

    for i, method in enumerate(methods):
        plt.annotate(method, (ause_vals[i], auroc_vals[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)

    plt.xlabel("AUSE (lower is better)")
    plt.ylabel("AUROC (higher is better)")
    plt.title("AUSE vs AUROC Trade-off")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_sparsification_curves(sparsification_data: Dict, save_path: str):
    """
    Sparsification curves (6 subplots).

    One subplot per method.
    X-axis: Fraction removed
    Y-axis: Error on remaining
    Two lines: Oracle vs Method
    """
    methods = list(sparsification_data.keys())
    n_methods = len(methods)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, method in enumerate(methods):
        data = sparsification_data[method]
        ax = axes[i]

        ax.plot(data["fractions"], data["errors"], label=f"{method}", marker='o')
        ax.plot(data["fractions"], data["oracle_errors"], label="Oracle", linestyle='--', marker='x')

        ax.set_xlabel("Fraction Removed")
        ax.set_ylabel("Error on Remaining")
        ax.set_title(f"{method}")
        ax.legend()
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
