"""Visualization and plotting"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
from sklearn.manifold import TSNE


def plot_gate_metrics(
    targets: Dict[str, float],
    actuals: Dict[str, float],
    save_path: str
):
    """Bar chart: target vs actual for gate metrics"""
    metrics = ['Reconstruction Error', 'Frozen-K Gen', 'Kernel Robustness']
    target_values = [
        targets['reconstruction_error'],
        targets['frozen_k_generalization'],
        targets['kernel_robustness']
    ]
    actual_values = [
        actuals['reconstruction_error'],
        actuals['frozen_k_generalization'],
        actuals['kernel_robustness']
    ]

    x = np.arange(len(metrics))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width/2, target_values, width, label='Target', color='lightblue')
    bars2 = ax.bar(x + width/2, actual_values, width, label='Actual', color='orange')

    ax.set_ylabel('Value (%)')
    ax.set_title('Gate Metrics: Target vs Actual')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Add pass/fail annotations
    for i, (target, actual) in enumerate(zip(target_values, actual_values)):
        if i < 2:  # Reconstruction and Frozen-K (lower is better)
            passed = actual < target
        else:  # Kernel robustness (higher is better)
            passed = actual >= target

        color = 'green' if passed else 'red'
        status = 'PASS' if passed else 'FAIL'
        ax.text(x[i] + width/2, actual + 1, status, ha='center', color=color, fontweight='bold')

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_training_curves(history: Dict[str, List[float]], save_path: str):
    """Training/val loss curves over epochs"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss curves
    axes[0].plot(history['train_loss'], label='Train Loss', color='blue')
    axes[0].plot(history['val_loss'], label='Val Loss', color='orange')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training and Validation Loss')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Loss components
    axes[1].plot(history['recon_loss'], label='Reconstruction Loss', color='green')
    axes[1].plot(history['equiv_loss'], label='Equivariance Loss', color='red')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].set_title('Loss Components')
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_quotient_space_tsne(
    embeddings: np.ndarray,
    arch_labels: np.ndarray,
    save_path: str
):
    """t-SNE projection colored by architecture family"""
    tsne = TSNE(n_components=2, perplexity=30, max_iter=1000, random_state=42)
    embeddings_2d = tsne.fit_transform(embeddings)

    colors = {0: 'blue', 1: 'orange', 2: 'green'}
    arch_names = {0: 'CNN', 1: 'Transformer', 2: 'RNN'}

    plt.figure(figsize=(10, 8))
    for arch_idx in [0, 1, 2]:
        mask = arch_labels == arch_idx
        plt.scatter(
            embeddings_2d[mask, 0],
            embeddings_2d[mask, 1],
            c=colors[arch_idx],
            label=arch_names[arch_idx],
            alpha=0.6,
            s=50
        )

    plt.xlabel('t-SNE Dimension 1')
    plt.ylabel('t-SNE Dimension 2')
    plt.title('Quotient Space Visualization (t-SNE)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_reconstruction_error_distribution(errors: np.ndarray, save_path: str):
    """Histogram of reconstruction errors"""
    plt.figure(figsize=(10, 6))
    plt.hist(errors, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    plt.xlabel('Reconstruction Error (%)')
    plt.ylabel('Frequency')
    plt.title('Reconstruction Error Distribution')
    plt.axvline(errors.mean(), color='red', linestyle='--', label=f'Mean: {errors.mean():.2f}%')
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_k_dimensionality_analysis(k_values: List[int], errors: List[float], save_path: str):
    """Line plot: K vs reconstruction error"""
    plt.figure(figsize=(10, 6))
    plt.plot(k_values, errors, marker='o', linewidth=2, markersize=8, color='purple')
    plt.xlabel('K (Quotient Space Dimension)')
    plt.ylabel('Reconstruction Error (%)')
    plt.title('K Dimensionality Analysis')
    plt.axhline(10.0, color='red', linestyle='--', label='Target (10%)')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
