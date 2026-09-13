import os
import logging
from itertools import combinations

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from config import PARADIGMS, GATE_MIN_DIFF


def _savefig(fig, out_dir, filename):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    logging.info(f"Figure saved: {path}")


def plot_ratio_bar(ratios, pair_results, out_dir):
    """Bar chart mean±std ratio per paradigm with p-value annotations."""
    paradigms = list(ratios.keys())
    means = [np.mean(ratios[p]) for p in paradigms]
    stds = [np.std(ratios[p], ddof=1) for p in paradigms]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(paradigms))
    bars = ax.bar(x, means, yerr=stds, capsize=5, color='steelblue', alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels([p.upper() for p in paradigms])
    ax.set_ylabel('Spurious / Task Probe Accuracy Ratio')
    ax.set_title('h-e1: Spurious/Task Ratio by Paradigm (mean ± std, 5 seeds)')

    # Annotate significant pairs
    max_y = max(m + s for m, s in zip(means, stds)) + 0.05
    sig_pairs = [r for r in pair_results if r['p_bonf'] < 0.05 and r['mean_diff'] >= GATE_MIN_DIFF]
    y_offset = max_y
    for r in sig_pairs:
        p1, p2 = r['pair'].split('_vs_')
        if p1 in paradigms and p2 in paradigms:
            i, j = paradigms.index(p1), paradigms.index(p2)
            ax.annotate(
                f"p={r['p_bonf']:.3f}*",
                xy=((x[i] + x[j]) / 2, y_offset),
                ha='center', fontsize=8,
            )
            ax.plot([x[i], x[j]], [y_offset - 0.005, y_offset - 0.005], 'k-', lw=0.8)
            y_offset += 0.03

    ax.set_ylim(0, max(y_offset + 0.05, 1.3))
    _savefig(fig, out_dir, 'ratio_bar.png')


def plot_acc_heatmap(acc_records, out_dir):
    """2x4 heatmap: spurious_acc and task_acc per paradigm (mean across seeds)."""
    paradigms = PARADIGMS
    data = np.zeros((2, len(paradigms)))
    for r in acc_records:
        pi = paradigms.index(r['paradigm'])
        # accumulate then average
        data[0, pi] += r['spurious_acc']
        data[1, pi] += r['task_acc']
    counts = {p: sum(1 for r in acc_records if r['paradigm'] == p) for p in paradigms}
    for pi, p in enumerate(paradigms):
        n = counts[p] or 1
        data[0, pi] /= n
        data[1, pi] /= n

    fig, ax = plt.subplots(figsize=(8, 3))
    im = ax.imshow(data, aspect='auto', vmin=0.5, vmax=1.0, cmap='YlOrRd')
    ax.set_xticks(range(len(paradigms)))
    ax.set_xticklabels([p.upper() for p in paradigms])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Spurious Acc', 'Task Acc'])
    plt.colorbar(im, ax=ax)
    for i in range(2):
        for j in range(len(paradigms)):
            ax.text(j, i, f'{data[i, j]:.3f}', ha='center', va='center', fontsize=9)
    ax.set_title('Mean Probe Accuracy per Paradigm')
    _savefig(fig, out_dir, 'acc_heatmap.png')


def plot_acc_scatter(acc_records, out_dir):
    """Scatter spurious_acc vs task_acc, colored by paradigm."""
    colors = {'erm': 'tab:blue', 'moco': 'tab:orange', 'dino': 'tab:green', 'barlowtwins': 'tab:red'}
    fig, ax = plt.subplots(figsize=(6, 5))
    for paradigm in PARADIGMS:
        pts = [(r['task_acc'], r['spurious_acc']) for r in acc_records if r['paradigm'] == paradigm]
        if pts:
            xs, ys = zip(*pts)
            ax.scatter(xs, ys, label=paradigm.upper(), color=colors.get(paradigm, 'gray'), s=60, alpha=0.8)
    ax.set_xlabel('Task Probe Accuracy')
    ax.set_ylabel('Spurious Probe Accuracy')
    ax.set_title('Spurious vs Task Accuracy (5 seeds)')
    ax.legend()
    _savefig(fig, out_dir, 'acc_scatter.png')


def plot_pvalue_matrix(pair_results, paradigms, out_dir):
    """4x4 symmetric Bonferroni p-value matrix."""
    n = len(paradigms)
    mat = np.ones((n, n))
    pair_map = {r['pair']: r['p_bonf'] for r in pair_results}
    for i, p1 in enumerate(paradigms):
        for j, p2 in enumerate(paradigms):
            if i == j:
                mat[i, j] = np.nan
            else:
                key1 = f'{p1}_vs_{p2}'
                key2 = f'{p2}_vs_{p1}'
                mat[i, j] = pair_map.get(key1, pair_map.get(key2, 1.0))

    fig, ax = plt.subplots(figsize=(5, 4))
    masked = np.ma.masked_invalid(mat)
    im = ax.imshow(masked, vmin=0, vmax=1.0, cmap='RdYlGn_r')
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    labels = [p.upper() for p in paradigms]
    ax.set_xticklabels(labels, rotation=30)
    ax.set_yticklabels(labels)
    plt.colorbar(im, ax=ax, label='Bonferroni p-value')
    for i in range(n):
        for j in range(n):
            if not np.isnan(mat[i, j]):
                ax.text(j, i, f'{mat[i, j]:.3f}', ha='center', va='center', fontsize=7)
    ax.set_title('Pairwise Bonferroni p-values')
    _savefig(fig, out_dir, 'pvalue_matrix.png')


def plot_ratio_violin(ratios, out_dir):
    """Violin/box plot of ratio distribution per paradigm."""
    paradigms = list(ratios.keys())
    data = [ratios[p] for p in paradigms]
    fig, ax = plt.subplots(figsize=(7, 5))
    parts = ax.violinplot(data, positions=range(len(paradigms)), showmedians=True)
    ax.set_xticks(range(len(paradigms)))
    ax.set_xticklabels([p.upper() for p in paradigms])
    ax.set_ylabel('Spurious / Task Ratio')
    ax.set_title('Ratio Distribution per Paradigm (5 seeds)')
    _savefig(fig, out_dir, 'ratio_violin.png')
