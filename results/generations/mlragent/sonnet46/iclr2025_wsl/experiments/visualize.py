"""
Visualization utilities for SymAE experiments.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import r2_score


def plot_training_curves(histories, model_names, save_path):
    """Plot training and validation loss curves for all models."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    colors = plt.cm.Set1(np.linspace(0, 0.8, len(histories)))

    for i, (hist, name, color) in enumerate(zip(histories, model_names, colors)):
        if "train_loss" not in hist:
            continue
        epochs = range(1, len(hist["train_loss"]) + 1)
        axes[0].plot(epochs, hist["train_loss"], label=f"{name} (train)", color=color, linestyle="-", linewidth=2)
        if "val_loss" in hist and len(hist["val_loss"]) > 0:
            axes[0].plot(epochs, hist["val_loss"], label=f"{name} (val)", color=color, linestyle="--", linewidth=2)

    axes[0].set_xlabel("Epoch", fontsize=12)
    axes[0].set_ylabel("Total Loss", fontsize=12)
    axes[0].set_title("Training and Validation Loss Curves", fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=10)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_yscale('log')

    for i, (hist, name, color) in enumerate(zip(histories, model_names, colors)):
        if "train_rec_loss" not in hist:
            continue
        epochs = range(1, len(hist["train_rec_loss"]) + 1)
        axes[1].plot(epochs, hist["train_rec_loss"], label=f"{name} rec (train)", color=color, linestyle="-", linewidth=2)
        if "val_rec_loss" in hist and len(hist["val_rec_loss"]) > 0:
            axes[1].plot(epochs, hist["val_rec_loss"], label=f"{name} rec (val)", color=color, linestyle="--", linewidth=2)

    axes[1].set_xlabel("Epoch", fontsize=12)
    axes[1].set_ylabel("Reconstruction Loss", fontsize=12)
    axes[1].set_title("Reconstruction Loss Curves", fontsize=14, fontweight='bold')
    axes[1].legend(fontsize=10)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_yscale('log')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_property_prediction_curves(histories, model_names, save_path):
    """Plot property prediction loss over training."""
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = plt.cm.Set1(np.linspace(0, 0.8, len(histories)))

    for hist, name, color in zip(histories, model_names, colors):
        if "train_prop_loss" not in hist:
            continue
        epochs = range(1, len(hist["train_prop_loss"]) + 1)
        ax.plot(epochs, hist["train_prop_loss"], label=f"{name} (train)", color=color, linestyle="-", linewidth=2)
        if "val_prop_loss" in hist and len(hist["val_prop_loss"]) > 0:
            ax.plot(epochs, hist["val_prop_loss"], label=f"{name} (val)", color=color, linestyle="--", linewidth=2)

    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Property Prediction Loss (MSE)", fontsize=12)
    ax.set_title("Property Prediction Loss During Training", fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_r2_comparison(method_names, r2_scores, mae_scores, save_path):
    """Bar chart comparing property prediction R² across methods."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    colors = plt.cm.Set2(np.linspace(0, 0.8, len(method_names)))

    # R² scores
    bars = axes[0].bar(method_names, r2_scores, color=colors, edgecolor='black', linewidth=1.2)
    for bar, val in zip(bars, r2_scores):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    axes[0].set_ylim(0, max(max(r2_scores) * 1.15, 0.5))
    axes[0].set_xlabel("Method", fontsize=12)
    axes[0].set_ylabel("R² Score", fontsize=12)
    axes[0].set_title("Test Accuracy Prediction: R² Score\n(Higher is Better)", fontsize=13, fontweight='bold')
    axes[0].axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
    axes[0].grid(axis='y', alpha=0.3)
    axes[0].tick_params(axis='x', rotation=15)

    # MAE scores
    bars = axes[1].bar(method_names, mae_scores, color=colors, edgecolor='black', linewidth=1.2)
    for bar, val in zip(bars, mae_scores):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.001,
                     f'{val:.4f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    axes[1].set_xlabel("Method", fontsize=12)
    axes[1].set_ylabel("MAE", fontsize=12)
    axes[1].set_title("Test Accuracy Prediction: MAE\n(Lower is Better)", fontsize=13, fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    axes[1].tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_latent_space(Z_dict, labels, save_path, method="tsne"):
    """Visualize latent spaces of different methods using t-SNE or PCA."""
    n_methods = len(Z_dict)
    fig, axes = plt.subplots(1, n_methods, figsize=(6 * n_methods, 5))

    if n_methods == 1:
        axes = [axes]

    labels_arr = np.array(labels)
    vmin, vmax = labels_arr.min(), labels_arr.max()

    for ax, (name, Z) in zip(axes, Z_dict.items()):
        if Z.shape[1] > 2:
            if method == "tsne" and len(Z) >= 30:
                reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(Z)-1))
                Z_2d = reducer.fit_transform(Z)
            else:
                reducer = PCA(n_components=2, random_state=42)
                Z_2d = reducer.fit_transform(Z)
        else:
            Z_2d = Z

        sc = ax.scatter(Z_2d[:, 0], Z_2d[:, 1], c=labels_arr, cmap='viridis',
                        s=25, alpha=0.7, vmin=vmin, vmax=vmax)
        plt.colorbar(sc, ax=ax, label='Test Accuracy')
        ax.set_xlabel("Dim 1", fontsize=11)
        ax.set_ylabel("Dim 2", fontsize=11)
        ax.set_title(f"{name} Latent Space\n(colored by test accuracy)", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    plt.suptitle("Latent Space Visualization (t-SNE/PCA projection)", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_scatter_predictions(y_true_dict, y_pred_dict, save_path):
    """Scatter plots of predicted vs actual test accuracy."""
    n_methods = len(y_true_dict)
    fig, axes = plt.subplots(1, n_methods, figsize=(6 * n_methods, 5))

    if n_methods == 1:
        axes = [axes]

    for ax, (name, y_true) in zip(axes, y_true_dict.items()):
        y_pred = y_pred_dict[name]
        r2 = r2_score(y_true, y_pred)
        ax.scatter(y_true, y_pred, alpha=0.6, s=20, color='steelblue', edgecolors='white', linewidths=0.5)
        lo, hi = min(y_true.min(), y_pred.min()), max(y_true.max(), y_pred.max())
        ax.plot([lo, hi], [lo, hi], 'r--', linewidth=2, label='Perfect prediction')
        ax.set_xlabel("True Test Accuracy", fontsize=11)
        ax.set_ylabel("Predicted Test Accuracy", fontsize=11)
        ax.set_title(f"{name}\nR² = {r2:.3f}", fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Predicted vs. True Test Accuracy", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_accuracy_distribution(labels, save_path):
    """Plot the distribution of test accuracies in the model zoo."""
    fig, ax = plt.subplots(figsize=(8, 5))
    labels_arr = np.array(labels)
    ax.hist(labels_arr, bins=30, color='steelblue', edgecolor='black', alpha=0.8)
    ax.axvline(labels_arr.mean(), color='red', linestyle='--', linewidth=2,
               label=f'Mean={labels_arr.mean():.3f}')
    ax.set_xlabel("Test Accuracy", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Distribution of Test Accuracies in Model Zoo", fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")


def plot_reconstruction_quality(rec_errors, method_names, save_path):
    """Box plot of reconstruction errors across methods."""
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = plt.cm.Set2(np.linspace(0, 0.8, len(method_names)))

    bp = ax.boxplot(rec_errors, labels=method_names, patch_artist=True,
                    medianprops=dict(color='black', linewidth=2))

    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_xlabel("Method", fontsize=12)
    ax.set_ylabel("Reconstruction MSE (per sample)", fontsize=12)
    ax.set_title("Weight Reconstruction Quality", fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {save_path}")
