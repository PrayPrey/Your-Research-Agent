import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import scipy.stats
from config import PARADIGMS, FIGURES_DIR


def plot_gate_metrics(wb_results, celeba_results, save_path, figsize=(8, 5)):
    paradigms = ['erm', 'moco']
    datasets = {'Waterbirds': wb_results, 'CelebA': celeba_results}
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(datasets))
    width = 0.35
    for i, (paradigm, color) in enumerate(zip(paradigms, ['steelblue', 'coral'])):
        means = [np.mean(ds[paradigm]) for ds in datasets.values()]
        stds  = [np.std(ds[paradigm])  for ds in datasets.values()]
        ax.bar(x + i*width, means, width, yerr=stds, label=paradigm.upper(),
               color=color, capsize=5, alpha=0.85)
    ax.set_xticks(x + width/2)
    ax.set_xticklabels(list(datasets.keys()))
    ax.set_ylabel('Spurious / Task Probe Accuracy Ratio')
    ax.set_title('H-D1: MoCo-v3 vs ERM Spurious Encoding Ratio')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[viz] Saved gate_metrics → {save_path}")


def plot_interaction(wb_results, celeba_results, save_path, figsize=(10, 6)):
    datasets = {'Waterbirds': wb_results, 'CelebA': celeba_results}
    colors = {'erm': 'steelblue', 'moco': 'coral', 'dino': 'forestgreen',
              'barlowtwins': 'mediumpurple'}
    fig, ax = plt.subplots(figsize=figsize)
    x = np.arange(len(datasets))
    width = 0.2
    for i, paradigm in enumerate(PARADIGMS):
        means, stds = [], []
        for ds in datasets.values():
            if paradigm in ds:
                means.append(np.mean(ds[paradigm]))
                stds.append(np.std(ds[paradigm]))
            else:
                means.append(np.nan)
                stds.append(0)
        offset = (i - 1.5) * width
        ax.bar(x + offset, means, width, yerr=stds,
               label=paradigm.upper(), color=colors[paradigm], capsize=4, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(list(datasets.keys()))
    ax.set_ylabel('Spurious / Task Probe Accuracy Ratio')
    ax.set_title('H-D1: All Paradigms × Dataset Interaction')
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[viz] Saved interaction_plot → {save_path}")


def plot_directional_test(analysis_results, save_path):
    wb = analysis_results['wb_primary']
    ca = analysis_results['ca_primary']

    tests = [
        ('WB: MoCo-ERM\n(directional)', wb['diff_mean'], wb['moco_mean'], wb['erm_mean'],
         wb['t'], wb['p_directional'], 5-1),
        ('CelebA: MoCo-ERM\n(null test)', ca['diff_mean'], ca['moco_mean'], ca['erm_mean'],
         ca['t'], ca['p_two_sided'], 5-1),
    ]

    fig, ax = plt.subplots(figsize=(8, 4))
    for i, (label, diff, m_mean, e_mean, t, p, df) in enumerate(tests):
        se = abs(diff / (t + 1e-10))
        ci = scipy.stats.t.interval(0.95, df=df, loc=diff, scale=se)
        color = 'steelblue' if i == 0 else 'coral'
        ax.barh(i, diff, xerr=[[diff - ci[0]], [ci[1] - diff]],
                color=color, alpha=0.8, capsize=5)
        ax.text(diff + 0.001, i, f'p={p:.3f}', va='center', fontsize=9)
    ax.axvline(0, color='black', linewidth=1, linestyle='--')
    ax.set_yticks(range(len(tests)))
    ax.set_yticklabels([t[0] for t in tests])
    ax.set_xlabel('MoCo Mean Ratio − ERM Mean Ratio')
    ax.set_title('H-D1: Directional Test Results')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[viz] Saved directional_test → {save_path}")


def plot_seed_distributions(wb_results, celeba_results, save_path):
    datasets = {'Waterbirds': wb_results, 'CelebA': celeba_results}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    colors = {'erm': 'steelblue', 'moco': 'coral', 'dino': 'forestgreen',
              'barlowtwins': 'mediumpurple'}

    for ax, (dname, ds) in zip(axes, datasets.items()):
        for j, paradigm in enumerate(PARADIGMS):
            if paradigm in ds:
                vals = ds[paradigm]
                ax.scatter([j]*len(vals), vals, color=colors[paradigm],
                           alpha=0.7, s=50, zorder=3)
                ax.boxplot(vals, positions=[j], widths=0.4,
                           patch_artist=True,
                           boxprops=dict(facecolor=colors[paradigm], alpha=0.3),
                           medianprops=dict(color='black'))
        ax.set_xticks(range(len(PARADIGMS)))
        ax.set_xticklabels([p.upper() for p in PARADIGMS], rotation=15)
        ax.set_title(dname)
        ax.set_ylabel('Spurious / Task Ratio')
        ax.grid(axis='y', alpha=0.3)

    plt.suptitle('H-D1: Ratio Distributions (5 seeds per paradigm)', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"[viz] Saved seed_distributions → {save_path}")


def generate_all_figures(wb_results, celeba_results, analysis_results,
                         figures_dir=None, wga_data=None):
    if figures_dir is None:
        figures_dir = FIGURES_DIR
    os.makedirs(figures_dir, exist_ok=True)

    paths = []
    plot_gate_metrics(wb_results, celeba_results,
                      os.path.join(figures_dir, 'gate_metrics.png'))
    paths.append('gate_metrics.png')

    plot_interaction(wb_results, celeba_results,
                     os.path.join(figures_dir, 'interaction_plot.png'))
    paths.append('interaction_plot.png')

    plot_directional_test(analysis_results,
                          os.path.join(figures_dir, 'directional_test.png'))
    paths.append('directional_test.png')

    plot_seed_distributions(wb_results, celeba_results,
                            os.path.join(figures_dir, 'seed_distributions.png'))
    paths.append('seed_distributions.png')

    return paths
