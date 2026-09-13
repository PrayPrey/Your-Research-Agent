"""Visualization for H-E1 experiment."""

from typing import Dict

import matplotlib.pyplot as plt
import numpy as np


def plot_auc_comparison(results: Dict, stats: Dict, out_path: str) -> None:
    """Bar chart comparing AUC across methods and architectures.

    Args:
        results: {method: {arch: [aucs_per_seed]}}
        stats: Gate check statistics
        out_path: Output file path
    """
    methods = list(results.keys())
    x = np.arange(len(methods))
    width = 0.35

    bert_means = []
    bert_stds = []
    gpt2_means = []
    gpt2_stds = []

    for method in methods:
        bert_aucs = results[method].get("bert", [0])
        gpt2_aucs = results[method].get("gpt2", [0])

        bert_means.append(np.mean(bert_aucs))
        bert_stds.append(np.std(bert_aucs) / np.sqrt(len(bert_aucs)))
        gpt2_means.append(np.mean(gpt2_aucs))
        gpt2_stds.append(np.std(gpt2_aucs) / np.sqrt(len(gpt2_aucs)))

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width/2, bert_means, width, yerr=bert_stds,
                   label='BERT', color='steelblue', capsize=5)
    bars2 = ax.bar(x + width/2, gpt2_means, width, yerr=gpt2_stds,
                   label='GPT-2', color='darkorange', capsize=5)

    ax.set_xlabel('Attribution Method', fontsize=12)
    ax.set_ylabel('Mislabeled Detection AUC', fontsize=12)
    ax.set_title('Attribution Method Performance by Architecture', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([m.upper() for m in methods])
    ax.legend()
    ax.set_ylim(0.4, 1.0)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Random')

    # Add significance markers
    for i, method in enumerate(methods):
        if method in stats["methods"]:
            p = stats["methods"][method]["p_value"]
            if p < 0.001:
                sig = "***"
            elif p < 0.01:
                sig = "**"
            elif p < 0.05:
                sig = "*"
            else:
                sig = ""

            if sig:
                max_y = max(bert_means[i] + bert_stds[i], gpt2_means[i] + gpt2_stds[i])
                ax.annotate(sig, xy=(i, max_y + 0.02), ha='center', fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_method_arch_heatmap(results: Dict, out_path: str) -> None:
    """Heatmap of AUC scores (3 methods x 2 architectures).

    Args:
        results: {method: {arch: [aucs_per_seed]}}
        out_path: Output file path
    """
    methods = list(results.keys())
    archs = ["bert", "gpt2"]

    data = np.zeros((len(methods), len(archs)))
    for i, method in enumerate(methods):
        for j, arch in enumerate(archs):
            aucs = results[method].get(arch, [0])
            data[i, j] = np.mean(aucs)

    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(data, cmap='RdYlGn', vmin=0.5, vmax=0.9)

    ax.set_xticks(np.arange(len(archs)))
    ax.set_yticks(np.arange(len(methods)))
    ax.set_xticklabels([a.upper() for a in archs])
    ax.set_yticklabels([m.upper() for m in methods])

    # Add values
    for i in range(len(methods)):
        for j in range(len(archs)):
            ax.text(j, i, f"{data[i, j]:.3f}", ha="center", va="center",
                   color="black", fontsize=12)

    ax.set_title("Mislabeled Detection AUC\n(Method × Architecture)", fontsize=12)
    plt.colorbar(im, ax=ax, label="AUC")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")


def plot_diff_significance(results: Dict, stats: Dict, out_path: str) -> None:
    """Bar chart of AUC differences (GPT2 - BERT) with p-values.

    Args:
        results: {method: {arch: [aucs_per_seed]}}
        stats: Gate check statistics
        out_path: Output file path
    """
    methods = list(results.keys())

    diffs = []
    p_values = []

    for method in methods:
        if method in stats["methods"]:
            diffs.append(stats["methods"][method]["auc_diff"])
            p_values.append(stats["methods"][method]["p_value"])
        else:
            diffs.append(0)
            p_values.append(1)

    fig, ax = plt.subplots(figsize=(8, 5))

    colors = ['green' if p < 0.05 else 'gray' for p in p_values]
    bars = ax.bar(methods, diffs, color=colors, edgecolor='black')

    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='+5% threshold')
    ax.axhline(y=-0.05, color='red', linestyle='--', alpha=0.5, label='-5% threshold')

    ax.set_xlabel('Attribution Method', fontsize=12)
    ax.set_ylabel('AUC Difference (GPT-2 - BERT)', fontsize=12)
    ax.set_title('Architecture Effect on Attribution Method Performance', fontsize=14)
    ax.set_xticklabels([m.upper() for m in methods])

    # Add p-values
    for i, (method, p) in enumerate(zip(methods, p_values)):
        y_pos = diffs[i] + 0.01 if diffs[i] >= 0 else diffs[i] - 0.02
        ax.annotate(f"p={p:.3f}", xy=(i, y_pos), ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_path}")
