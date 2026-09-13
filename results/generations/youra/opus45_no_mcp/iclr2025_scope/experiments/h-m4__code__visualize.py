"""Visualization for H-M4: correlation plots and summary dashboard"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress

from config import FIGURES_DIR


def plot_density_vs_delta(results_table: dict, correlation_result: dict, out_path: str = None):
    """Main figure: scatter density vs accuracy_delta with regression line."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "density_vs_delta.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    data = correlation_result["data"]
    densities = data["densities"]
    deltas = data["accuracy_deltas"]
    tasks = data["tasks"]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(densities, deltas, s=100, c='steelblue', edgecolors='navy', linewidths=1.5, zorder=3)

    for i, task in enumerate(tasks):
        ax.annotate(task.upper(), (densities[i], deltas[i]),
                    textcoords="offset points", xytext=(5, 5), fontsize=10)

    if len(densities) >= 2:
        slope, intercept, _, _, _ = linregress(densities, deltas)
        x_line = np.linspace(min(densities) - 0.1, max(densities) + 0.1, 100)
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r--', linewidth=2, label=f'Regression (slope={slope:.3f})')

    rho = correlation_result["primary"]["rho"]
    p_value = correlation_result["primary"]["p_value"]
    gate_pass = correlation_result["primary"]["gate_pass"]

    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)

    ax.set_xlabel("Retrieval Density", fontsize=12)
    ax.set_ylabel("Accuracy Delta (Mamba - Transformer)", fontsize=12)
    ax.set_title(f"H-M4: Task-Dependent Transformation\nSpearman ρ = {rho:.3f}, p = {p_value:.4f} ({'PASS' if gate_pass else 'FAIL'})",
                 fontsize=14)

    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_architecture_comparison(results_table: dict, out_path: str = None):
    """Bar chart: Transformer vs Mamba accuracy per task."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "architecture_comparison.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    sorted_tasks = sorted(results_table.keys(), key=lambda t: results_table[t]["density"])

    transformer_accs = [results_table[t]["transformer"]["accuracy"] for t in sorted_tasks]
    mamba_accs = [results_table[t]["mamba"]["accuracy"] for t in sorted_tasks]

    x = np.arange(len(sorted_tasks))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, transformer_accs, width, label='Transformer', color='steelblue')
    bars2 = ax.bar(x + width/2, mamba_accs, width, label='Mamba', color='coral')

    ax.set_ylabel('Accuracy')
    ax.set_xlabel('Task (sorted by retrieval density)')
    ax.set_title('Architecture Comparison: Transformer vs Mamba')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{t.upper()}\n(d={results_table[t]['density']})" for t in sorted_tasks])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_sharpness_delta_by_task(results_table: dict, out_path: str = None):
    """Sharpness delta per task."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "sharpness_delta.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    sorted_tasks = sorted(results_table.keys(), key=lambda t: results_table[t]["density"])
    sharpness_deltas = [results_table[t]["delta"]["sharpness_delta"] for t in sorted_tasks]

    fig, ax = plt.subplots(figsize=(8, 5))

    colors = ['green' if d < 0 else 'red' for d in sharpness_deltas]
    bars = ax.bar(sorted_tasks, sharpness_deltas, color=colors)

    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_ylabel('Sharpness Delta (Mamba - Transformer)')
    ax.set_xlabel('Task')
    ax.set_title('Sharpness Delta by Task')
    ax.grid(True, alpha=0.3, axis='y')

    for i, (task, delta) in enumerate(zip(sorted_tasks, sharpness_deltas)):
        ax.annotate(f'{delta:.4f}', (i, delta),
                    textcoords="offset points", xytext=(0, 5 if delta >= 0 else -15),
                    ha='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_summary_dashboard(results_table: dict, correlation_result: dict, out_path: str = None):
    """Summary dashboard with all metrics."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "summary_dashboard.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    sorted_tasks = sorted(results_table.keys(), key=lambda t: results_table[t]["density"])
    data = correlation_result["data"]

    ax = axes[0, 0]
    ax.scatter(data["densities"], data["accuracy_deltas"], s=80, c='steelblue')
    for i, task in enumerate(data["tasks"]):
        ax.annotate(task.upper(), (data["densities"][i], data["accuracy_deltas"][i]),
                    textcoords="offset points", xytext=(5, 5), fontsize=9)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel("Retrieval Density")
    ax.set_ylabel("Accuracy Delta")
    ax.set_title(f"Density vs Delta (ρ={correlation_result['primary']['rho']:.3f})")
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    transformer_accs = [results_table[t]["transformer"]["accuracy"] for t in sorted_tasks]
    mamba_accs = [results_table[t]["mamba"]["accuracy"] for t in sorted_tasks]
    x = np.arange(len(sorted_tasks))
    width = 0.35
    ax.bar(x - width/2, transformer_accs, width, label='Transformer')
    ax.bar(x + width/2, mamba_accs, width, label='Mamba')
    ax.set_xticks(x)
    ax.set_xticklabels([t[:4].upper() for t in sorted_tasks])
    ax.legend()
    ax.set_title("Accuracy by Architecture")
    ax.grid(True, alpha=0.3, axis='y')

    ax = axes[1, 0]
    sharpness_deltas = [results_table[t]["delta"]["sharpness_delta"] for t in sorted_tasks]
    colors = ['green' if d < 0 else 'red' for d in sharpness_deltas]
    ax.bar([t[:4].upper() for t in sorted_tasks], sharpness_deltas, color=colors)
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_title("Sharpness Delta")
    ax.grid(True, alpha=0.3, axis='y')

    ax = axes[1, 1]
    metrics = ['acc_δ ρ', 'sharp_δ ρ', 'rank_δ ρ']
    values = [
        correlation_result["primary"]["rho"],
        correlation_result["ablations"]["sharpness_delta"]["rho"],
        correlation_result["ablations"]["rank_delta"]["rho"],
    ]
    colors = ['green' if abs(v) >= 0.7 else 'orange' for v in values]
    ax.barh(metrics, values, color=colors)
    ax.axvline(x=0.7, color='red', linestyle='--', label='Threshold')
    ax.axvline(x=-0.7, color='red', linestyle='--')
    ax.set_xlim(-1.1, 1.1)
    ax.set_title("Correlation Coefficients")
    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')

    plt.suptitle(f"H-M4 Summary: Gate {'PASS' if correlation_result['primary']['gate_pass'] else 'FAIL'}",
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def generate_all_figures(results_table: dict, correlation_result: dict):
    """Generate all figures."""
    figures = []

    fig_path = plot_density_vs_delta(results_table, correlation_result)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_architecture_comparison(results_table)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_sharpness_delta_by_task(results_table)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    fig_path = plot_summary_dashboard(results_table, correlation_result)
    figures.append(fig_path)
    print(f"  Saved: {fig_path}")

    return figures
