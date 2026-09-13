"""Visualization: t-SNE, bar charts, AMI-vs-epoch, cluster composition."""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from typing import Dict

GROUP_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]


def plot_gate_metrics(results: Dict, output_path: str) -> None:
    datasets = list(results.keys())
    amis = [results[d]['ami'] for d in datasets]
    purities = [results[d]['worst_purity'] for d in datasets]

    x = np.arange(len(datasets))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, amis, width, label='AMI', color='#1f77b4')
    bars2 = ax.bar(x + width/2, purities, width, label='Worst Purity', color='#ff7f0e')
    ax.axhline(0.5, color='blue', linestyle='--', label='AMI threshold (0.5)')
    ax.axhline(0.75, color='orange', linestyle='--', label='Purity threshold (0.75)')
    ax.set_xticks(x)
    ax.set_xticklabels(datasets)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel('Score')
    ax.set_title('Gate Metrics: AMI and Worst-Cluster Purity')
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f'Saved: {output_path}')


def plot_tsne(embeddings: np.ndarray, labels: np.ndarray,
              color_by: str, title: str, output_path: str) -> None:
    n = min(len(embeddings), 5000)
    idx = np.random.RandomState(42).choice(len(embeddings), n, replace=False)
    emb_sub = embeddings[idx]
    lab_sub = labels[idx]

    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    proj = tsne.fit_transform(emb_sub)

    unique_labels = np.unique(lab_sub)
    fig, ax = plt.subplots(figsize=(12, 8))
    for lbl in unique_labels:
        mask = lab_sub == lbl
        color = GROUP_COLORS[int(lbl) % len(GROUP_COLORS)]
        ax.scatter(proj[mask, 0], proj[mask, 1], c=color, label=str(lbl),
                   alpha=0.5, s=5)
    ax.set_title(title)
    ax.legend(markerscale=3, title=color_by)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f'Saved: {output_path}')


def plot_cluster_composition(group_ids: np.ndarray, cluster_assignments: np.ndarray,
                              dataset_name: str, output_path: str) -> None:
    k = len(np.unique(cluster_assignments))
    n_groups = len(np.unique(group_ids))
    data = np.zeros((k, n_groups))
    for c in range(k):
        mask = cluster_assignments == c
        if mask.sum() == 0:
            continue
        counts = np.bincount(group_ids[mask], minlength=n_groups)
        data[c] = counts / mask.sum()

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(k)
    for g in range(n_groups):
        ax.bar(range(k), data[:, g], bottom=bottom,
               color=GROUP_COLORS[g % len(GROUP_COLORS)], label=f'Group {g}')
        bottom += data[:, g]
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Fraction')
    ax.set_title(f'Cluster Composition — {dataset_name}')
    ax.set_xticks(range(k))
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f'Saved: {output_path}')


def plot_ami_vs_epoch(epoch_ami_dict: Dict[int, float], dataset_name: str,
                      output_path: str) -> None:
    epochs = sorted(epoch_ami_dict.keys())
    amis = [epoch_ami_dict[e] for e in epochs]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(epochs, amis, marker='o', color='#1f77b4')
    ax.axhline(0.5, color='red', linestyle='--', label='Threshold (0.5)')
    ax.set_xlabel('Epoch')
    ax.set_ylabel('AMI')
    ax.set_title(f'AMI vs Epoch — {dataset_name}')
    ax.legend()
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f'Saved: {output_path}')


def generate_all_figures(results: Dict, embeddings_dir: str, figures_dir: str) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    # Gate metrics bar chart
    plot_gate_metrics(results, os.path.join(figures_dir, 'metrics_bar.png'))

    for dataset_name in results.keys():
        emb_path = os.path.join(embeddings_dir, f'{dataset_name}_epoch5.npy')
        grp_path = os.path.join(embeddings_dir, f'{dataset_name}_group_ids.npy')
        lab_path = os.path.join(embeddings_dir, f'{dataset_name}_labels.npy')
        if not os.path.exists(emb_path):
            print(f'Embeddings not found for {dataset_name}, skipping t-SNE')
            continue

        embeddings = np.load(emb_path)
        group_ids = np.load(grp_path)
        labels = np.load(lab_path)
        cluster_assignments = results[dataset_name].get('cluster_assignments')
        if cluster_assignments is None:
            from cluster import run_kmeans
            cluster_assignments = run_kmeans(embeddings)

        plot_tsne(embeddings, labels, 'class',
                  f't-SNE by Class — {dataset_name}',
                  os.path.join(figures_dir, f'tsne_class_{dataset_name}.png'))
        plot_tsne(embeddings, group_ids, 'group',
                  f't-SNE by Group — {dataset_name}',
                  os.path.join(figures_dir, f'tsne_group_{dataset_name}.png'))
        plot_tsne(embeddings, cluster_assignments, 'cluster',
                  f't-SNE by Cluster — {dataset_name}',
                  os.path.join(figures_dir, f'tsne_cluster_{dataset_name}.png'))
        plot_cluster_composition(group_ids, cluster_assignments, dataset_name,
                                 os.path.join(figures_dir, f'cluster_composition_{dataset_name}.png'))
