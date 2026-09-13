"""
visualize.py - 5 figure generation functions for H-E1 experiment.
"""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


VIZ_CONFIG = {
    "dpi": 300,
    "format": "png",
    # Group colors: G0=landbird/land, G1=landbird/water, G2=waterbird/land, G3=waterbird/water
    # Colorblind-safe palette
    "group_colors": {
        0: "#4477AA",
        1: "#EE6677",
        2: "#228833",
        3: "#CCBB44",
    },
    "threshold_linestyle": "--",
    "threshold_color": "red",
    "threshold_alpha": 0.7,
    "figsize_gate_metrics":  (12, 4),
    "figsize_trajectory":    (8, 5),
    "figsize_distribution":  (8, 5),
    "figsize_heatmap":       (8, 6),
    "figsize_feature_norms": (8, 5),
}

GROUP_LABELS = {0: 'G0 (LB/Land)', 1: 'G1 (LB/Water)', 2: 'G2 (WB/Land)', 3: 'G3 (WB/Water)'}
COLLECTION_EPOCHS = [1, 3, 5, 10]


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)


def plot_gate_metrics(
    per_epoch_metrics: dict,
    output_path: str,
) -> None:
    """
    3-panel bar chart: (a) ratio, (b) AUC, (c) balance_deviation
    across collection epochs. Dashed threshold lines at 3.0, 0.70, 0.10.
    """
    _ensure_dir(output_path)
    epochs = sorted(per_epoch_metrics.keys())
    ratios = [per_epoch_metrics[e].get('ratio', float('nan')) for e in epochs]
    aucs   = [per_epoch_metrics[e].get('auc', float('nan')) for e in epochs]
    bal_devs = [per_epoch_metrics[e].get('balance_deviation', float('nan')) for e in epochs]
    epoch_labels = [f'Epoch {e}' for e in epochs]

    cfg = VIZ_CONFIG
    fig, axes = plt.subplots(1, 3, figsize=cfg['figsize_gate_metrics'])
    fig.suptitle('H-E1 Gate Metrics Across Epochs', fontsize=12, fontweight='bold')

    # (a) ratio
    ax = axes[0]
    ax.bar(epoch_labels, ratios, color=cfg['group_colors'][1], alpha=0.8)
    ax.axhline(3.0, color=cfg['threshold_color'], linestyle=cfg['threshold_linestyle'],
               alpha=cfg['threshold_alpha'], label='Threshold (3.0)')
    ax.set_title('(a) g_tilde Ratio\n(minority / majority)')
    ax.set_ylabel('Ratio')
    ax.legend(fontsize=8)
    ax.set_ylim(bottom=0)

    # (b) AUC
    ax = axes[1]
    ax.bar(epoch_labels, aucs, color=cfg['group_colors'][2], alpha=0.8)
    ax.axhline(0.70, color=cfg['threshold_color'], linestyle=cfg['threshold_linestyle'],
               alpha=cfg['threshold_alpha'], label='Threshold (0.70)')
    ax.set_title('(b) AUC\n(g_tilde -> minority)')
    ax.set_ylabel('AUC')
    ax.legend(fontsize=8)
    ax.set_ylim(0, 1)

    # (c) balance deviation
    ax = axes[2]
    ax.bar(epoch_labels, bal_devs, color=cfg['group_colors'][3], alpha=0.8)
    ax.axhline(0.10, color=cfg['threshold_color'], linestyle=cfg['threshold_linestyle'],
               alpha=cfg['threshold_alpha'], label='Threshold (0.10)')
    ax.set_title('(c) Balance Deviation\n(top-25% subset)')
    ax.set_ylabel('Max |P(place|y) - 0.5|')
    ax.legend(fontsize=8)
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    fig.savefig(output_path, dpi=cfg['dpi'], bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_trajectory(
    per_epoch_metrics: dict,
    output_path: str,
) -> None:
    """
    Line plot of mean g_tilde per group (G0-G3) across collection epochs.
    Log-scale y-axis.
    """
    _ensure_dir(output_path)
    epochs = sorted(per_epoch_metrics.keys())
    cfg = VIZ_CONFIG

    fig, ax = plt.subplots(figsize=cfg['figsize_trajectory'])
    for g in range(4):
        values = [per_epoch_metrics[e].get(f'g_tilde_mean_G{g}', float('nan')) for e in epochs]
        ax.plot(epochs, values, marker='o', color=cfg['group_colors'][g],
                label=GROUP_LABELS[g], linewidth=2, markersize=6)

    ax.set_yscale('log')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Mean g_tilde (log scale)')
    ax.set_title('H-E1: Per-Group g_tilde Trajectory Across Epochs')
    ax.legend()
    ax.set_xticks(epochs)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=cfg['dpi'], bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_distribution(
    gradnorm_data: dict,
    output_path: str,
) -> None:
    """
    Overlaid KDE: minority (G1+G2) vs majority (G0+G3) g_tilde at T_id=5.
    """
    _ensure_dir(output_path)
    g_tilde = gradnorm_data['g_tilde']
    group_labels = gradnorm_data['group_labels']

    minority_mask = (group_labels == 1) | (group_labels == 2)
    minority_vals = g_tilde[minority_mask]
    majority_vals = g_tilde[~minority_mask]

    cfg = VIZ_CONFIG
    fig, ax = plt.subplots(figsize=cfg['figsize_distribution'])

    sns.kdeplot(majority_vals, ax=ax, color=cfg['group_colors'][0], label='Majority (G0+G3)',
                fill=True, alpha=0.3, linewidth=2)
    sns.kdeplot(minority_vals, ax=ax, color=cfg['group_colors'][1], label='Minority (G1+G2)',
                fill=True, alpha=0.3, linewidth=2)

    ax.set_xlabel('g_tilde (normalized gradient norm)')
    ax.set_ylabel('Density')
    ax.set_title('H-E1: g_tilde Distribution at Epoch 5\nMinority vs Majority')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=cfg['dpi'], bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_balance_heatmap(
    gradnorm_data: dict,
    output_path: str,
) -> None:
    """
    4x2 heatmap: group (G0-G3) x class (0,1) in top-25% selected subset vs full training set.
    """
    _ensure_dir(output_path)
    g_tilde = gradnorm_data['g_tilde']
    group_labels = gradnorm_data['group_labels']
    class_labels = gradnorm_data['class_labels']
    N = len(g_tilde)

    top_k = max(1, int(0.25 * N))
    top_k_idx = np.argsort(g_tilde)[-top_k:]

    # Build 4x2 count matrices: rows=groups, cols=classes
    full_counts = np.zeros((4, 2), dtype=float)
    top_counts = np.zeros((4, 2), dtype=float)

    for g in range(4):
        for c in range(2):
            mask_full = (group_labels == g) & (class_labels == c)
            full_counts[g, c] = mask_full.sum()

            sel_g = group_labels[top_k_idx]
            sel_c = class_labels[top_k_idx]
            mask_top = (sel_g == g) & (sel_c == c)
            top_counts[g, c] = mask_top.sum()

    cfg = VIZ_CONFIG
    fig, axes = plt.subplots(1, 2, figsize=cfg['figsize_heatmap'])

    group_names = [GROUP_LABELS[g] for g in range(4)]
    class_names = ['Class 0\n(Landbird)', 'Class 1\n(Waterbird)']

    # Normalize to proportions
    full_prop = full_counts / (full_counts.sum() + 1e-8)
    top_prop  = top_counts  / (top_counts.sum() + 1e-8)

    sns.heatmap(full_prop, ax=axes[0], annot=True, fmt='.3f',
                xticklabels=class_names, yticklabels=group_names,
                cmap='Blues', vmin=0, vmax=full_prop.max())
    axes[0].set_title('Full Training Set\nGroup x Class Proportions')
    axes[0].set_ylabel('Group')

    sns.heatmap(top_prop, ax=axes[1], annot=True, fmt='.3f',
                xticklabels=class_names, yticklabels=group_names,
                cmap='Oranges', vmin=0, vmax=top_prop.max())
    axes[1].set_title('Top-25% by g_tilde\nGroup x Class Proportions')

    fig.suptitle('H-E1: Balance Heatmap (Epoch 5)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    fig.savefig(output_path, dpi=cfg['dpi'], bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_feature_norms(
    gradnorm_data: dict,
    output_path: str,
) -> None:
    """
    Box plots of ||h(x_i)|| per group at T_id=5 (BatchNorm equalization check).
    """
    _ensure_dir(output_path)
    h_norm = gradnorm_data['h_norm']
    group_labels = gradnorm_data['group_labels']

    cfg = VIZ_CONFIG
    fig, ax = plt.subplots(figsize=cfg['figsize_feature_norms'])

    data_per_group = []
    labels_per_group = []
    colors = []
    for g in range(4):
        mask = group_labels == g
        if mask.sum() > 0:
            data_per_group.append(h_norm[mask])
            labels_per_group.append(GROUP_LABELS[g])
            colors.append(cfg['group_colors'][g])

    bp = ax.boxplot(data_per_group, labels=labels_per_group, patch_artist=True,
                    showfliers=False, notch=False)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('||h(x_i)|| (Feature L2 Norm)')
    ax.set_title('H-E1: Feature Norms per Group at Epoch 5\n(BatchNorm Equalization Check)')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    fig.savefig(output_path, dpi=cfg['dpi'], bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {output_path}")
