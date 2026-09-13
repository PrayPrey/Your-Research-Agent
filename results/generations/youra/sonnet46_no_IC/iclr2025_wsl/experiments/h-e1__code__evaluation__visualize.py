"""
Visualization: t-SNE plots, MMD comparison bar chart, distance histogram, training curves.
"""
import os
import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_tsne(train_z: torch.Tensor, vit_z: torch.Tensor,
              title: str, save_path: str) -> None:
    """2D t-SNE of train vs ViT latent spaces."""
    from sklearn.manifold import TSNE

    train_np = train_z.cpu().numpy()
    vit_np = vit_z.cpu().numpy()

    # Subsample for speed
    max_pts = 1000
    if len(train_np) > max_pts:
        idx = np.random.choice(len(train_np), max_pts, replace=False)
        train_np = train_np[idx]
    if len(vit_np) > max_pts:
        idx = np.random.choice(len(vit_np), max_pts, replace=False)
        vit_np = vit_np[idx]

    all_z = np.vstack([train_np, vit_np])
    n_train = len(train_np)

    tsne = TSNE(n_components=2, perplexity=min(30, len(all_z) - 1),
                random_state=42, max_iter=300)
    emb = tsne.fit_transform(all_z)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(emb[:n_train, 0], emb[:n_train, 1], c='steelblue', alpha=0.5,
               s=15, label='Train (MLP/CNN)')
    ax.scatter(emb[n_train:, 0], emb[n_train:, 1], c='tomato', alpha=0.7,
               s=20, label='Test (ViT-like)')
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=9)
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_mmd_comparison(mmd_sane: float, mmd_equi: float,
                        ratio: float, save_path: str) -> None:
    """Bar chart: SANE vs EquiSSL MMD with ratio annotation."""
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(['SANE (flat)', 'EquiSSL (graph)'],
                  [mmd_sane, mmd_equi],
                  color=['#E74C3C', '#2ECC71'], width=0.4, edgecolor='black')
    ax.set_ylabel('MMD (train → ViT)')
    ax.set_title(f'Distribution Shift: MMD Comparison\nRatio = {ratio:.2f}x '
                 f'({"PASS ✓" if ratio >= 2.0 else "WARN" if ratio >= 1.5 else "STOP ✗"})',
                 fontsize=11)
    for bar, val in zip(bars, [mmd_sane, mmd_equi]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                f'{val:.4f}', ha='center', va='bottom', fontsize=10)
    ax.axhline(0, color='black', linewidth=0.5)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_distance_histogram(train_z: torch.Tensor, vit_z: torch.Tensor,
                            save_path: str) -> None:
    """L2 distance from ViT test points to nearest training point."""
    train_np = train_z.cpu().numpy()
    vit_np = vit_z.cpu().numpy()

    # Subsample
    if len(train_np) > 500:
        train_np = train_np[np.random.choice(len(train_np), 500, replace=False)]

    # Compute L2 distances
    from sklearn.metrics import pairwise_distances
    dists = pairwise_distances(vit_np[:200], train_np[:200], metric='euclidean')
    min_dists = dists.min(axis=1)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(min_dists, bins=30, color='steelblue', edgecolor='white', alpha=0.8)
    ax.set_xlabel('Min L2 Distance (ViT → nearest train)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of ViT Test Points to Training Set')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_training_curves(log_dir: str, lambda_list: list, seed: int,
                         save_path: str) -> None:
    """Training curves for lambda sweep."""
    import csv

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    colors = plt.cm.viridis(np.linspace(0, 1, len(lambda_list)))

    for lam, color in zip(lambda_list, colors):
        csv_path = os.path.join(log_dir, f'training_log_lam{lam}_seed{seed}.csv')
        if not os.path.exists(csv_path):
            continue
        epochs, losses = [], []
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                epochs.append(int(row['epoch']))
                losses.append(float(row['ntxent_loss']))
        axes[0].plot(epochs, losses, label=f'λ={lam}', color=color)

    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Train Loss')
    axes[0].set_title('EquiSSL Training Curves (λ sweep)')
    axes[0].legend(fontsize=8)

    # Val loss
    for lam, color in zip(lambda_list, colors):
        csv_path = os.path.join(log_dir, f'training_log_lam{lam}_seed{seed}.csv')
        if not os.path.exists(csv_path):
            continue
        epochs, val_losses = [], []
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                epochs.append(int(row['epoch']))
                val_losses.append(float(row.get('val_loss', row['ntxent_loss'])))
        axes[1].plot(epochs, val_losses, label=f'λ={lam}', color=color)

    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Val Loss')
    axes[1].set_title('Validation Loss (λ sweep)')
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
