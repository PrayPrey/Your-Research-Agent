#!/usr/bin/env python3
"""Figure generation for h-m3: PBT adaptive contribution analysis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import defaultdict
from pathlib import Path

RESULTS_A = '/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_verifai/docs/youra_research/h-m3/results/experiment_a_results.jsonl'
RESULTS_B = '/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_verifai/docs/youra_research/h-m3/results/experiment_b_results.jsonl'
FIGURES_DIR = Path('/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_verifai/docs/youra_research/h-m3/figures')
FIGURES_DIR.mkdir(exist_ok=True)

def load_joined():
    a = {}
    with open(RESULTS_A) as f:
        for line in f:
            r = json.loads(line)
            a[(r['task_id'], r['model'], r['program_idx'])] = r
    b = {}
    with open(RESULTS_B) as f:
        for line in f:
            r = json.loads(line)
            b[(r['task_id'], r['model'], r['program_idx'])] = r
    joined = []
    for key in a:
        if key in b and not a[key].get('error') and not b[key].get('error'):
            joined.append({
                'task_id': key[0], 'model': key[1],
                'static': a[key]['static_failure_rate'],
                'adaptive': b[key]['adaptive_failure_rate'],
                'contrib': b[key]['adaptive_failure_rate'] - a[key]['static_failure_rate'],
                'task_type': a[key].get('task_type', 'humaneval' if 'HumanEval' in key[0] else 'mbpp')
            })
    return joined

def fig1_task_mean_distribution(joined):
    task_contribs = defaultdict(list)
    for r in joined:
        task_contribs[r['task_id']].append(r['contrib'])
    task_means = np.array([np.mean(v) for v in task_contribs.values()])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(task_means, bins=40, color='steelblue', edgecolor='white', alpha=0.85)
    ax.axvline(task_means.mean(), color='firebrick', linestyle='--', linewidth=1.5,
               label=f'Mean = {task_means.mean():.3f}')
    ax.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5)
    ax.set_xlabel('Mean Adaptive Contribution per Task')
    ax.set_ylabel('Number of Tasks')
    ax.set_title('Distribution of Per-Task Adaptive Contribution\n(PBT − Static Oracle Failure Rate)')
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig1_task_mean_distribution.png', dpi=150)
    plt.close(fig)
    print('fig1 done')

def fig2_per_model(joined):
    model_contribs = defaultdict(list)
    for r in joined:
        model_contribs[r['model']].append(r['contrib'])

    labels = [m.split('__')[-1][:25] for m in model_contribs]
    means = [np.mean(v) for v in model_contribs.values()]
    sems = [np.std(v) / np.sqrt(len(v)) for v in model_contribs.values()]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(labels))
    bars = ax.bar(x, means, yerr=sems, capsize=4, color='steelblue', alpha=0.85)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=9)
    ax.set_ylabel('Mean Adaptive Contribution')
    ax.set_title('Adaptive Contribution by Model')
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig2_per_model.png', dpi=150)
    plt.close(fig)
    print('fig2 done')

def fig3_static_vs_adaptive_scatter(joined):
    # Sample for readability
    rng = np.random.default_rng(0)
    idx = rng.choice(len(joined), min(3000, len(joined)), replace=False)
    sample = [joined[i] for i in idx]
    xs = [r['static'] for r in sample]
    ys = [r['adaptive'] for r in sample]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(xs, ys, alpha=0.15, s=8, color='steelblue')
    lim = max(max(xs), max(ys)) + 0.02
    ax.plot([0, lim], [0, lim], 'r--', linewidth=1, label='y=x (no gain)')
    ax.set_xlabel('Static Failure Rate (Exp A)')
    ax.set_ylabel('Adaptive Failure Rate (Exp B)')
    ax.set_title('Static vs. Adaptive Oracle Failure Rates\n(Points above diagonal = adaptive finds more failures)')
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig3_static_vs_adaptive.png', dpi=150)
    plt.close(fig)
    print('fig3 done')

def fig4_by_task_type(joined):
    type_contribs = defaultdict(list)
    for r in joined:
        type_contribs[r['task_type']].append(r['contrib'])

    fig, axes = plt.subplots(1, len(type_contribs), figsize=(10, 5), sharey=True)
    if len(type_contribs) == 1:
        axes = [axes]
    for ax, (ttype, vals) in zip(axes, type_contribs.items()):
        arr = np.array(vals)
        ax.hist(arr, bins=30, color='steelblue', alpha=0.8, edgecolor='white')
        ax.axvline(arr.mean(), color='firebrick', linestyle='--',
                   label=f'Mean={arr.mean():.3f}')
        ax.set_title(ttype.upper())
        ax.set_xlabel('Adaptive Contribution')
        ax.legend(fontsize=8)
    axes[0].set_ylabel('Count')
    fig.suptitle('Adaptive Contribution by Task Type', y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / 'fig4_by_task_type.png', dpi=150)
    plt.close(fig)
    print('fig4 done')

def main():
    joined = load_joined()
    print(f'Loaded {len(joined)} joined pairs')
    fig1_task_mean_distribution(joined)
    fig2_per_model(joined)
    fig3_static_vs_adaptive_scatter(joined)
    fig4_by_task_type(joined)
    print(f'All figures saved to {FIGURES_DIR}')

if __name__ == '__main__':
    main()
