"""
Visualization utilities for experiment results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List
import os

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12


def plot_training_curves(
    history: Dict[str, List[float]],
    save_path: str,
    title: str = "Training Curves"
):
    """Plot training loss curves."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Plot losses
    if 'train_loss' in history:
        axes[0].plot(history['train_loss'], label='Train Loss', linewidth=2)
    if 'val_loss' in history:
        axes[0].plot(history['val_loss'], label='Val Loss', linewidth=2)

    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot metrics
    metric_keys = [k for k in history.keys() if 'loss' not in k]
    for key in metric_keys:
        axes[1].plot(history[key], label=key, linewidth=2)

    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Metric Value')
    axes[1].set_title('Training Metrics')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_model_comparison(
    results: Dict[str, Dict[str, float]],
    save_path: str,
    title: str = "Model Comparison"
):
    """Plot comparison of different models."""
    models = list(results.keys())
    metrics = list(results[models[0]].keys())

    # Create subplots for each metric
    n_metrics = len(metrics)
    n_cols = min(3, n_metrics)
    n_rows = (n_metrics + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
    if n_rows == 1 and n_cols == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    for i, metric in enumerate(metrics):
        values = [results[model][metric] for model in models]

        axes[i].bar(models, values, alpha=0.7, edgecolor='black')
        axes[i].set_xlabel('Model')
        axes[i].set_ylabel(metric)
        axes[i].set_title(metric.replace('_', ' ').title())
        axes[i].tick_params(axis='x', rotation=45)
        axes[i].grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for j, v in enumerate(values):
            axes[i].text(j, v, f'{v:.3f}', ha='center', va='bottom', fontsize=10)

    # Hide extra subplots
    for i in range(n_metrics, len(axes)):
        axes[i].axis('off')

    plt.suptitle(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_symmetry_analysis(
    base_embeddings: np.ndarray,
    variant_embeddings: np.ndarray,
    transform_types: List[str],
    save_path: str
):
    """Plot symmetry invariance analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Compute similarities
    similarities = []
    labels = []

    for i, base_emb in enumerate(base_embeddings):
        for j, variant_emb in enumerate(variant_embeddings):
            if j // 10 == i:  # Match base with its variants
                sim = np.dot(base_emb, variant_emb) / (
                    np.linalg.norm(base_emb) * np.linalg.norm(variant_emb) + 1e-8
                )
                similarities.append(sim)
                labels.append(transform_types[j % 10])

    # Plot histogram
    axes[0].hist(similarities, bins=50, alpha=0.7, edgecolor='black')
    axes[0].axvline(np.mean(similarities), color='red', linestyle='--',
                    linewidth=2, label=f'Mean: {np.mean(similarities):.3f}')
    axes[0].set_xlabel('Cosine Similarity')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Symmetry Invariance Distribution')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot by transformation type
    unique_types = list(set(labels))
    type_similarities = {t: [] for t in unique_types}

    for sim, label in zip(similarities, labels):
        type_similarities[label].append(sim)

    boxplot_data = [type_similarities[t] for t in unique_types]
    bp = axes[1].boxplot(boxplot_data, labels=unique_types, patch_artist=True)

    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)

    axes[1].set_xlabel('Transformation Type')
    axes[1].set_ylabel('Cosine Similarity')
    axes[1].set_title('Similarity by Transformation Type')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_backdoor_detection_roc(
    clean_distances: np.ndarray,
    backdoor_distances: np.ndarray,
    save_path: str
):
    """Plot ROC curve for backdoor detection."""
    from sklearn.metrics import roc_curve, auc

    # Create labels
    labels = np.array([0] * len(clean_distances) + [1] * len(backdoor_distances))
    distances = np.concatenate([clean_distances, backdoor_distances])

    # Compute ROC curve
    fpr, tpr, thresholds = roc_curve(labels, distances)
    roc_auc = auc(fpr, tpr)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # ROC curve
    axes[0].plot(fpr, tpr, linewidth=2, label=f'ROC (AUC = {roc_auc:.3f})')
    axes[0].plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
    axes[0].set_xlabel('False Positive Rate')
    axes[0].set_ylabel('True Positive Rate')
    axes[0].set_title('ROC Curve for Backdoor Detection')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Distance distributions
    axes[1].hist(clean_distances, bins=30, alpha=0.6, label='Clean', edgecolor='black')
    axes[1].hist(backdoor_distances, bins=30, alpha=0.6, label='Backdoored', edgecolor='black')
    axes[1].axvline(np.mean(clean_distances), color='blue', linestyle='--', linewidth=2)
    axes[1].axvline(np.mean(backdoor_distances), color='orange', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Distance to Clean Centroid')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Distance Distribution')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_embedding_visualization(
    embeddings: np.ndarray,
    labels: List[str],
    save_path: str,
    method: str = 'tsne'
):
    """Visualize embeddings using dimensionality reduction."""
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA

    # Reduce to 2D
    if method == 'tsne':
        reducer = TSNE(n_components=2, random_state=42)
        embeddings_2d = reducer.fit_transform(embeddings)
    else:
        reducer = PCA(n_components=2)
        embeddings_2d = reducer.fit_transform(embeddings)

    # Plot
    plt.figure(figsize=(12, 8))

    unique_labels = list(set(labels))
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

    for i, label in enumerate(unique_labels):
        mask = np.array([l == label for l in labels])
        plt.scatter(
            embeddings_2d[mask, 0],
            embeddings_2d[mask, 1],
            c=[colors[i]],
            label=label,
            alpha=0.6,
            s=50,
            edgecolors='black',
            linewidth=0.5
        )

    plt.xlabel(f'{method.upper()} Component 1')
    plt.ylabel(f'{method.upper()} Component 2')
    plt.title(f'Embedding Visualization ({method.upper()})')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_results_table(
    results: Dict[str, Dict[str, float]],
    save_path: str
):
    """Create and save results table as CSV."""
    df = pd.DataFrame(results).T
    df = df.round(4)
    df.to_csv(save_path)
    return df


if __name__ == "__main__":
    print("Testing visualization functions...")

    # Test training curves
    history = {
        'train_loss': np.random.rand(50) * 2,
        'val_loss': np.random.rand(50) * 2.5,
        'accuracy': np.random.rand(50) * 0.8 + 0.2
    }
    plot_training_curves(history, 'test_training.png')
    print("Training curves plot saved")

    # Test model comparison
    results = {
        'Model A': {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.88},
        'Model B': {'accuracy': 0.92, 'precision': 0.90, 'recall': 0.91},
        'Model C': {'accuracy': 0.78, 'precision': 0.75, 'recall': 0.80}
    }
    plot_model_comparison(results, 'test_comparison.png')
    print("Model comparison plot saved")

    # Clean up test files
    import os
    for f in ['test_training.png', 'test_comparison.png']:
        if os.path.exists(f):
            os.remove(f)

    print("All visualization tests passed!")
