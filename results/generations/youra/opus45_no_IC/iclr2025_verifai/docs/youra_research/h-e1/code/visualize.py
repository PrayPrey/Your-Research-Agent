"""Visualization for H-E1 experiment results."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib_venn import venn3
import os

import config


def plot_jaccard_bar(overlaps: dict[str, float], threshold: float, out_path: str) -> None:
    """Bar chart showing pairwise Jaccard indices with threshold line."""
    pairs = ["grammar_vs_static", "grammar_vs_smt", "static_vs_smt"]
    values = [overlaps.get(p, 0.0) for p in pairs]
    labels = ["Grammar vs\nStatic", "Grammar vs\nSMT", "Static vs\nSMT"]

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ['#4CAF50' if v < threshold else '#F44336' for v in values]
    bars = ax.bar(labels, values, color=colors, edgecolor='black', linewidth=1.2)

    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')

    ax.set_ylabel('Jaccard Index', fontsize=12)
    ax.set_title('H-E1: Error Class Independence\n(All values below threshold = PASS)', fontsize=14)
    ax.set_ylim(0, max(0.5, max(values) * 1.2))

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_venn(sets: dict[str, set], out_path: str) -> None:
    """3-circle Venn diagram of grammar/static/smt improved sets."""
    grammar = sets.get("grammar", set())
    static = sets.get("static", set())
    smt = sets.get("smt", set())

    fig, ax = plt.subplots(figsize=(10, 8))

    v = venn3(
        [grammar, static, smt],
        set_labels=('Grammar\nConstraints', 'Static\nAnalysis', 'SMT\nRepair'),
        ax=ax
    )

    if v:
        for text in v.set_labels:
            if text:
                text.set_fontsize(11)
                text.set_fontweight('bold')
        for text in v.subset_labels:
            if text:
                text.set_fontsize(10)

    ax.set_title('H-E1: Overlap of Improved Task IDs\nby Verification Strategy', fontsize=14)

    info_text = f"Grammar: {len(grammar)} | Static: {len(static)} | SMT: {len(smt)}"
    ax.text(0.5, -0.1, info_text, ha='center', va='top', transform=ax.transAxes, fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_per_model_comparison(overlaps_by_model: dict[str, dict], out_path: str) -> None:
    """Grouped bar chart comparing Jaccard values across models."""
    pairs = ["grammar_vs_static", "grammar_vs_smt", "static_vs_smt"]
    pair_labels = ["Grammar vs Static", "Grammar vs SMT", "Static vs SMT"]
    models = list(overlaps_by_model.keys())

    if not models:
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    x = range(len(pairs))
    width = 0.35

    colors = ['#2196F3', '#FF9800']

    for i, model in enumerate(models[:2]):
        model_overlaps = overlaps_by_model.get(model, {})
        values = [model_overlaps.get(p, 0.0) for p in pairs]
        offset = width * (i - 0.5)
        bars = ax.bar([xi + offset for xi in x], values, width,
                     label=model.split('/')[-1], color=colors[i % len(colors)])

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=9)

    ax.axhline(y=config.JACCARD_THRESHOLD, color='red', linestyle='--',
               linewidth=2, label=f'Threshold ({config.JACCARD_THRESHOLD})')

    ax.set_xticks(x)
    ax.set_xticklabels(pair_labels, fontsize=10)
    ax.set_ylabel('Jaccard Index', fontsize=12)
    ax.set_title('H-E1: Per-Model Jaccard Comparison', fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, 0.5)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()
