"""Visualization module for H-E1 experiment."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA


def plot_gate_metric(residual_ratio: float, threshold: float, out_path: str) -> str:
    """Bar chart of residual_ratio vs threshold line."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 4))

    color = 'green' if residual_ratio > threshold else 'red'
    ax.bar(['Residual Ratio'], [residual_ratio], color=color, alpha=0.7)
    ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold})')

    status = 'PASS' if residual_ratio > threshold else 'FAIL'
    ax.set_title(f'Gate Metric: {status}', fontsize=14)
    ax.set_ylabel('Residual Variance Ratio')
    ax.legend()
    ax.set_ylim(0, max(residual_ratio * 1.5, threshold * 1.5))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    return out_path


def plot_accuracy_heatmap(class_wise_acc: np.ndarray, out_path: str, max_models: int = 100) -> str:
    """Heatmap of class-wise accuracy (sampled if too many models)."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Sample if too many models
    if class_wise_acc.shape[0] > max_models:
        idx = np.linspace(0, class_wise_acc.shape[0] - 1, max_models, dtype=int)
        data = class_wise_acc[idx]
    else:
        data = class_wise_acc

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(data, cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Accuracy'})
    ax.set_xlabel('Class')
    ax.set_ylabel('Model')
    ax.set_title('Class-wise Accuracy Heatmap')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    return out_path


def plot_variance_decomposition(residual_variance: float, total_variance: float, out_path: str) -> str:
    """Pie chart of variance decomposition."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    explained = total_variance - residual_variance
    if total_variance == 0:
        sizes = [1, 0]
    else:
        sizes = [explained, residual_variance]

    labels = ['Baseline Explained', 'Residual']
    colors = ['#66b3ff', '#ff9999']
    explode = (0, 0.1)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax.set_title('Variance Decomposition')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    return out_path


def plot_per_class_variance(per_class_var: np.ndarray, out_path: str) -> str:
    """Bar chart of per-class variance."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    cifar10_classes = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                       'dog', 'frog', 'horse', 'ship', 'truck']

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(cifar10_classes, per_class_var, color='steelblue', alpha=0.7)

    ax.set_xlabel('Class')
    ax.set_ylabel('Variance')
    ax.set_title('Per-Class Accuracy Variance')
    ax.set_xticklabels(cifar10_classes, rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    return out_path


def plot_model_clustering(class_wise_acc: np.ndarray, overall_acc: np.ndarray, out_path: str) -> str:
    """PCA scatter of class-wise profiles colored by overall accuracy."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    pca = PCA(n_components=2)
    embedding = pca.fit_transform(class_wise_acc)

    fig, ax = plt.subplots(figsize=(8, 6))
    scatter = ax.scatter(embedding[:, 0], embedding[:, 1], c=overall_acc,
                         cmap='viridis', alpha=0.6, s=10)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Overall Accuracy')

    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)')
    ax.set_title('Model Clustering by Class-wise Accuracy Profile')

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()

    return out_path
