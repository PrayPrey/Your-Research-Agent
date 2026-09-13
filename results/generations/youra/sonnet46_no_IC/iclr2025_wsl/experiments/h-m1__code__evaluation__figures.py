"""Figure generation for H-M1 validation report."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

COLORS = {'sane': '#666666', 'equi': '#E07020', 'equi_perm': '#2060D0'}
LABELS = {'sane': 'SANE (flat)', 'equi': 'EquiSSL (monomial)',
          'equi_perm': 'EquiSSL-perm (permutation)'}
sns.set_theme(style='whitegrid')


def _save(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved: {path}')


def plot_r2_bar_chart(results, stat_tests, save_path):
    """Figure 1: R² bar chart with error bars and p-value annotations."""
    fig, ax = plt.subplots(figsize=(8, 5))
    models = [m for m in ['sane', 'equi', 'equi_perm'] if m in results]
    means = [results[m].r2_mean for m in models]
    stds = [results[m].r2_std for m in models]
    colors = [COLORS[m] for m in models]
    labels = [LABELS[m] for m in models]

    bars = ax.bar(labels, means, yerr=stds, capsize=5, color=colors, alpha=0.8,
                  error_kw={'linewidth': 2})

    # SANE threshold line
    sane_r2 = results.get('sane', None)
    if sane_r2:
        ax.axhline(sane_r2.r2_mean, color=COLORS['sane'], linestyle='--',
                   alpha=0.6, label=f'SANE baseline R²={sane_r2.r2_mean:.3f}')

    # p-value annotations
    for i, m in enumerate(models):
        if m == 'sane':
            continue
        test = stat_tests.get(m)
        if test:
            y = means[i] + stds[i] + 0.01
            annot = f'p={test.p_value:.3f}' + (' *' if test.significant else '')
            ax.text(i, y, annot, ha='center', fontsize=9)

    ax.set_ylabel('Linear Probe R²')
    ax.set_title('ViT Property Prediction: Graph vs Flat Encoder')
    ax.legend()
    _save(fig, save_path)


def plot_ablation_ladder(results, save_path):
    """Figure 2: Ablation ladder — 3 models comparison."""
    fig, ax = plt.subplots(figsize=(8, 5))
    models = [m for m in ['sane', 'equi_perm', 'equi'] if m in results]
    means = [results[m].r2_mean for m in models]
    stds = [results[m].r2_std for m in models]
    x = np.arange(len(models))
    colors = [COLORS[m] for m in models]
    labels_l = [LABELS[m] for m in models]

    ax.bar(x, means, yerr=stds, capsize=5, color=colors, alpha=0.8,
           error_kw={'linewidth': 2})
    ax.set_xticks(x)
    ax.set_xticklabels(labels_l, rotation=10)
    ax.set_ylabel('Linear Probe R²')
    ax.set_title('Ablation Ladder: Scale Equivariance Effect')
    _save(fig, save_path)


def plot_tsne_comparison(embeddings_dict, n_seeds, save_path):
    """Figure 3: t-SNE 4-panel comparison."""
    try:
        from sklearn.manifold import TSNE
    except ImportError:
        print('  sklearn not available, skipping t-SNE')
        return

    models = ['sane', 'equi_perm', 'equi']
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    combined_embs = []
    combined_labels_m = []

    for mi, m in enumerate(models):
        # Average across seeds
        seed_embs = [embeddings_dict[f'{m}_seed{s}']
                     for s in range(n_seeds) if f'{m}_seed{s}' in embeddings_dict]
        if not seed_embs:
            continue
        avg_emb = np.mean(seed_embs, axis=0)
        tsne = TSNE(n_components=2, perplexity=min(30, len(avg_emb) - 1),
                    max_iter=1000, random_state=42)
        proj = tsne.fit_transform(avg_emb)
        axes[mi].scatter(proj[:, 0], proj[:, 1], c=COLORS[m], alpha=0.6, s=20)
        axes[mi].set_title(LABELS[m])
        axes[mi].axis('off')
        combined_embs.append(avg_emb)
        combined_labels_m.extend([mi] * len(avg_emb))

    # Combined panel
    if combined_embs:
        all_emb = np.concatenate(combined_embs, axis=0)
        tsne2 = TSNE(n_components=2, perplexity=min(30, len(all_emb) - 1),
                     max_iter=1000, random_state=42)
        proj2 = tsne2.fit_transform(all_emb)
        for mi, m in enumerate(models[:len(combined_embs)]):
            mask = np.array(combined_labels_m) == mi
            axes[3].scatter(proj2[mask, 0], proj2[mask, 1],
                            c=COLORS[m], label=LABELS[m], alpha=0.5, s=15)
        axes[3].set_title('Combined')
        axes[3].legend(fontsize=7)
        axes[3].axis('off')

    plt.suptitle('t-SNE: Encoder Latent Spaces on ViT Zoo')
    plt.tight_layout()
    _save(fig, save_path)


def plot_paired_seed_scatter(results, save_path):
    """Figure 4: Per-seed R² vs SANE."""
    fig, ax = plt.subplots(figsize=(7, 5))
    sane = results.get('sane')
    if not sane:
        plt.close(fig); return

    for m in ['equi', 'equi_perm']:
        if m not in results:
            continue
        sane_vals = sane.r2_per_seed[:len(results[m].r2_per_seed)]
        graph_vals = results[m].r2_per_seed
        ax.scatter(sane_vals, graph_vals, color=COLORS[m], label=LABELS[m],
                   s=80, zorder=3)

    lims = [ax.get_xlim(), ax.get_ylim()]
    lo = min(lims[0][0], lims[1][0])
    hi = max(lims[0][1], lims[1][1])
    ax.plot([lo, hi], [lo, hi], 'k--', alpha=0.4, label='diagonal')
    ax.set_xlabel('SANE R² (per seed)')
    ax.set_ylabel('Graph Encoder R² (per seed)')
    ax.set_title('Per-Seed R²: Graph vs SANE')
    ax.legend()
    _save(fig, save_path)


def plot_vit_accuracy_distribution(labels, save_path):
    """Figure 5: Histogram of ViT accuracy values."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(labels, bins=20, color='steelblue', alpha=0.8, edgecolor='white')
    ax.set_xlabel('ViT Model Accuracy')
    ax.set_ylabel('Count')
    ax.set_title(f'ViT Zoo Accuracy Distribution (N={len(labels)})')
    _save(fig, save_path)


def generate_all_figures(results, stat_tests, embeddings_dict, labels,
                         figures_dir, n_seeds):
    os.makedirs(figures_dir, exist_ok=True)
    plot_r2_bar_chart(results, stat_tests,
                      os.path.join(figures_dir, 'fig1_r2_bar.png'))
    plot_ablation_ladder(results,
                         os.path.join(figures_dir, 'fig2_ablation.png'))
    plot_tsne_comparison(embeddings_dict, n_seeds,
                         os.path.join(figures_dir, 'fig3_tsne.png'))
    plot_paired_seed_scatter(results,
                             os.path.join(figures_dir, 'fig4_seed_scatter.png'))
    plot_vit_accuracy_distribution(labels,
                                   os.path.join(figures_dir, 'fig5_acc_dist.png'))
