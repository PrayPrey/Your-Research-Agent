"""H-M3 Visualization Suite - F1 Retention Charts and Interaction Plots"""
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import os
from config import FIGURE_DPI, FIGURE_SIZE, PALETTE

def plot_f1_retention_bars(results: dict, out_dir: str) -> str:
    """Required: F1 retention bar chart by condition."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    lengths = sorted(set(int(k.split("_")[1]) for k in results.keys()))
    x = np.arange(len(lengths))
    width = 0.35

    mohawk_means = []
    cab_means = []
    mohawk_errs = []
    cab_errs = []

    for length in lengths:
        mohawk_key = f"mohawk_{length}"
        cab_key = f"cab_{length}"

        m_scores = results.get(mohawk_key, {}).get("retention", [0])
        c_scores = results.get(cab_key, {}).get("retention", [0])

        mohawk_means.append(np.mean(m_scores))
        cab_means.append(np.mean(c_scores))
        mohawk_errs.append(1.96 * np.std(m_scores) / np.sqrt(len(m_scores)) if len(m_scores) > 1 else 0)
        cab_errs.append(1.96 * np.std(c_scores) / np.sqrt(len(c_scores)) if len(c_scores) > 1 else 0)

    bars1 = ax.bar(x - width/2, mohawk_means, width, yerr=mohawk_errs, label='MOHAWK',
                   color=PALETTE["mohawk"], capsize=5)
    bars2 = ax.bar(x + width/2, cab_means, width, yerr=cab_errs, label='CAB',
                   color=PALETTE["cab"], capsize=5)

    ax.set_xlabel('Sequence Length')
    ax.set_ylabel('F1 Retention (%)')
    ax.set_title('F1 Retention: MOHAWK vs CAB by Sequence Length')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{l//1000}K' for l in lengths])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    path = os.path.join(out_dir, "f1_retention_bars.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIGURE_DPI)
    plt.close()
    return path

def plot_interaction(results: dict, out_dir: str) -> str:
    """Required: Interaction plot (lines for MOHAWK vs CAB across lengths)."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    lengths = sorted(set(int(k.split("_")[1]) for k in results.keys()))

    mohawk_means = [np.mean(results.get(f"mohawk_{l}", {}).get("retention", [0])) for l in lengths]
    cab_means = [np.mean(results.get(f"cab_{l}", {}).get("retention", [0])) for l in lengths]

    x_labels = [f'{l//1000}K' for l in lengths]

    ax.plot(x_labels, mohawk_means, 'o-', color=PALETTE["mohawk"], label='MOHAWK', linewidth=2, markersize=8)
    ax.plot(x_labels, cab_means, 's-', color=PALETTE["cab"], label='CAB', linewidth=2, markersize=8)

    ax.set_xlabel('Sequence Length')
    ax.set_ylabel('F1 Retention (%)')
    ax.set_title('Interaction Effect: Objective × Length')
    ax.legend()
    ax.grid(alpha=0.3)

    if len(lengths) >= 2:
        for i in range(len(lengths)):
            diff = cab_means[i] - mohawk_means[i]
            ax.annotate(f'{diff:+.1f}', xy=(i, (mohawk_means[i] + cab_means[i])/2),
                       fontsize=9, ha='center', va='bottom')

    path = os.path.join(out_dir, "interaction_plot.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIGURE_DPI)
    plt.close()
    return path

def plot_per_task_breakdown(results: dict, task_scores: dict, out_dir: str) -> str:
    """Optional: Per-task F1 breakdown."""
    fig, ax = plt.subplots(figsize=(10, 6))

    tasks = list(task_scores.keys())
    x = np.arange(len(tasks))
    width = 0.35

    mohawk_scores = [np.mean(task_scores[t].get("mohawk", [0])) * 100 for t in tasks]
    cab_scores = [np.mean(task_scores[t].get("cab", [0])) * 100 for t in tasks]

    ax.bar(x - width/2, mohawk_scores, width, label='MOHAWK', color=PALETTE["mohawk"])
    ax.bar(x + width/2, cab_scores, width, label='CAB', color=PALETTE["cab"])

    ax.set_xlabel('Task')
    ax.set_ylabel('F1 Score (%)')
    ax.set_title('Per-Task F1 Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=45, ha='right')
    ax.legend()

    path = os.path.join(out_dir, "per_task_breakdown.png")
    plt.tight_layout()
    plt.savefig(path, dpi=FIGURE_DPI)
    plt.close()
    return path

def generate_all_figures(results: dict, task_scores: dict, out_dir: str) -> List[str]:
    """Generate all required and optional figures."""
    os.makedirs(out_dir, exist_ok=True)
    figures = []

    figures.append(plot_f1_retention_bars(results, out_dir))
    figures.append(plot_interaction(results, out_dir))

    if task_scores:
        figures.append(plot_per_task_breakdown(results, task_scores, out_dir))

    return figures
