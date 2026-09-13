"""Figure generation for h-e1 experiment."""

import os
import numpy as np
import matplotlib.pyplot as plt
import config


def plot_correlation_heatmap(correlations, out_path):
    """Plot heatmap of pairwise correlations."""
    methods = ['trak', 'tracin', 'kronfluence']
    n = len(methods)

    # Build matrix
    matrix = np.eye(n)
    for i, m1 in enumerate(methods):
        for j, m2 in enumerate(methods):
            if i < j:
                key = f'{m1}_vs_{m2}'
                if key in correlations:
                    r = correlations[key]['pearson']
                    matrix[i, j] = r
                    matrix[j, i] = r

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap='coolwarm', vmin=-1, vmax=1)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels([m.upper() for m in methods])
    ax.set_yticklabels([m.upper() for m in methods])

    # Annotate cells
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f'{matrix[i, j]:.3f}', ha='center', va='center',
                   color='white' if abs(matrix[i, j]) > 0.5 else 'black')

    plt.colorbar(im, label='Pearson r')
    plt.title('Attribution Method Correlation Matrix')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_pairwise_scatter(scores_dict, out_dir):
    """Plot scatter plots for each method pair."""
    methods = list(scores_dict.keys())

    for i, m1 in enumerate(methods):
        for m2 in methods[i+1:]:
            s1 = scores_dict[m1].flatten()
            s2 = scores_dict[m2].flatten()

            # Subsample for plotting
            n = min(10000, len(s1))
            idx = np.random.choice(len(s1), n, replace=False)

            fig, ax = plt.subplots(figsize=(6, 6))
            ax.scatter(s1[idx], s2[idx], alpha=0.3, s=1)
            ax.set_xlabel(f'{m1.upper()} scores')
            ax.set_ylabel(f'{m2.upper()} scores')
            ax.set_title(f'{m1.upper()} vs {m2.upper()}')

            out_path = os.path.join(out_dir, f'scatter_{m1}_vs_{m2}.png')
            plt.tight_layout()
            plt.savefig(out_path, dpi=150)
            plt.close()
            print(f"Saved: {out_path}")


def plot_score_distributions(scores_dict, out_path):
    """Plot score distributions for each method."""
    methods = list(scores_dict.keys())

    fig, axes = plt.subplots(1, len(methods), figsize=(4*len(methods), 4))
    if len(methods) == 1:
        axes = [axes]

    for ax, method in zip(axes, methods):
        scores = scores_dict[method].flatten()
        scores = scores[np.isfinite(scores)]

        ax.hist(scores, bins=100, alpha=0.7, density=True)
        ax.set_xlabel('Influence score')
        ax.set_ylabel('Density')
        ax.set_title(f'{method.upper()} distribution')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def generate_all_figures(scores_dict, correlations):
    """Generate all required figures."""
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    plot_correlation_heatmap(
        correlations,
        os.path.join(config.FIGURES_DIR, 'correlation_heatmap.png')
    )
    plot_pairwise_scatter(scores_dict, config.FIGURES_DIR)
    plot_score_distributions(
        scores_dict,
        os.path.join(config.FIGURES_DIR, 'distributions.png')
    )
