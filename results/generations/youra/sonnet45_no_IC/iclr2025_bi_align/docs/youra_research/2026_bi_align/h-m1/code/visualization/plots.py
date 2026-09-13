"""
Visualization Module
Generate plots for representation analysis
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.manifold import TSNE
from typing import Dict
import torch

sns.set_style("whitegrid")

def plot_gate_metrics(metrics: Dict, thresholds: Dict, save_path: str):
    """
    Plot gate metrics comparison (MANDATORY figure).

    Args:
        metrics: Actual metric values
        thresholds: Target thresholds
        save_path: Where to save the figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())

    # Extract thresholds
    threshold_values = []
    for name in metric_names:
        thresh = thresholds[name]
        if isinstance(thresh, tuple):  # Range check
            threshold_values.append(np.mean(thresh))
        else:
            threshold_values.append(thresh)

    # Determine pass/fail
    colors = []
    for i, name in enumerate(metric_names):
        value = metric_values[i]
        thresh = thresholds[name]

        if isinstance(thresh, tuple):  # Range check
            passed = thresh[0] <= value <= thresh[1]
        elif name == 'CKA Similarity':  # Lower is better
            passed = value <= thresh
        else:  # Higher is better
            passed = value >= thresh

        colors.append('green' if passed else 'red')

    # Plot bars
    x = np.arange(len(metric_names))
    width = 0.35

    bars1 = ax.bar(x - width/2, threshold_values, width, label='Target', color='lightblue', alpha=0.7)
    bars2 = ax.bar(x + width/2, metric_values, width, label='Actual', color=colors)

    # Add value labels
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}',
                ha='center', va='bottom', fontsize=10)

    ax.set_xlabel('Metrics', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Gate Metrics: H-M1 (SHOULD_WORK)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metric_names)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_tsne(hidden_states: Dict, labels: Dict, save_path: str):
    """
    Plot t-SNE visualization of representation spaces.

    Args:
        hidden_states: Dict of {model_name: hidden_states tensor}
        labels: Dict of {label_name: labels tensor}
        save_path: Where to save the figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Combine all hidden states
    all_hidden = torch.cat([
        hidden_states['joint'],
        hidden_states['dpo'],
        hidden_states['attr']
    ], dim=0).numpy()

    # Create model labels
    n_samples = hidden_states['joint'].shape[0]
    model_labels = (
        ['Joint'] * n_samples +
        ['DPO'] * n_samples +
        ['Attr'] * n_samples
    )

    # Compute t-SNE
    print("  Computing t-SNE (this may take a minute)...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=30)
    embeddings = tsne.fit_transform(all_hidden)

    # Plot 1: Colored by model type
    colors_model = {'Joint': 'blue', 'DPO': 'red', 'Attr': 'green'}
    for model in ['Joint', 'DPO', 'Attr']:
        mask = np.array(model_labels) == model
        axes[0].scatter(
            embeddings[mask, 0],
            embeddings[mask, 1],
            c=colors_model[model],
            label=model,
            alpha=0.6,
            s=20
        )
    axes[0].set_title('Representation Space (by Model)', fontsize=14)
    axes[0].set_xlabel('t-SNE Dimension 1')
    axes[0].set_ylabel('t-SNE Dimension 2')
    axes[0].legend()

    # Plot 2: Colored by preference label (Joint only)
    joint_embeddings = embeddings[:n_samples]
    pref_labels = labels['preference'].numpy()

    scatter = axes[1].scatter(
        joint_embeddings[:, 0],
        joint_embeddings[:, 1],
        c=pref_labels,
        cmap='coolwarm',
        alpha=0.6,
        s=20
    )
    axes[1].set_title('Joint Model Representations (by Preference)', fontsize=14)
    axes[1].set_xlabel('t-SNE Dimension 1')
    axes[1].set_ylabel('t-SNE Dimension 2')
    plt.colorbar(scatter, ax=axes[1], label='Preference (0=Rejected, 1=Chosen)')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_probing_curves(
    pref_train_history: list,
    pref_val_history: list,
    attr_train_history: list,
    attr_val_history: list,
    save_path: str
):
    """
    Plot probing learning curves.

    Args:
        pref_train_history: Preference probe training accuracy
        pref_val_history: Preference probe validation accuracy
        attr_train_history: Attribute probe training R²
        attr_val_history: Attribute probe validation R²
        save_path: Where to save the figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    epochs = range(1, len(pref_train_history) + 1)

    # Preference probe
    axes[0].plot(epochs, pref_train_history, label='Train', marker='o', markersize=4)
    axes[0].plot(epochs, pref_val_history, label='Validation', marker='s', markersize=4)
    axes[0].axhline(y=0.70, color='r', linestyle='--', label='Threshold (70%)')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].set_title('Preference Probing Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Attribute probe
    axes[1].plot(epochs, attr_train_history, label='Train', marker='o', markersize=4)
    axes[1].plot(epochs, attr_val_history, label='Validation', marker='s', markersize=4)
    axes[1].axhline(y=0.60, color='r', linestyle='--', label='Threshold (0.60)')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('R² Score')
    axes[1].set_title('Attribute Regression R²')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_cka_heatmap(cka_results: Dict, save_path: str):
    """
    Plot CKA similarity heatmap.

    Args:
        cka_results: Dictionary of CKA scores
        save_path: Where to save the figure
    """
    # Create matrix
    models = ['Joint', 'DPO', 'Attr']
    matrix = np.zeros((3, 3))

    matrix[0, 0] = cka_results['joint_joint']
    matrix[1, 1] = cka_results['dpo_dpo']
    matrix[2, 2] = cka_results['attr_attr']

    matrix[0, 1] = matrix[1, 0] = cka_results['joint_dpo']
    matrix[0, 2] = matrix[2, 0] = cka_results['joint_attr']
    matrix[1, 2] = matrix[2, 1] = cka_results['dpo_attr']

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.3f',
        cmap='YlOrRd',
        xticklabels=models,
        yticklabels=models,
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'CKA Similarity'},
        ax=ax
    )
    ax.set_title('CKA Representation Similarity Matrix', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_gradient_distribution(cosine_sims: list, save_path: str):
    """
    Plot gradient alignment distribution.

    Args:
        cosine_sims: List of cosine similarities
        save_path: Where to save the figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(cosine_sims, bins=20, alpha=0.7, color='blue', edgecolor='black')
    ax.axvline(x=np.mean(cosine_sims), color='red', linestyle='--', label=f'Mean: {np.mean(cosine_sims):.3f}')
    ax.axvspan(-0.5, 0.5, alpha=0.2, color='green', label='Target Range [-0.5, 0.5]')

    ax.set_xlabel('Cosine Similarity')
    ax.set_ylabel('Frequency')
    ax.set_title('Gradient Alignment Distribution (DPO vs Attr)', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
