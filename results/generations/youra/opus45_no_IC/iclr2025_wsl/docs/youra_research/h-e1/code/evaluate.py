import json
import os
import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Any

from model import flatten_weights


def compute_r2(
    model: torch.nn.Module,
    loader: DataLoader,
    model_kind: str,
    device: torch.device
) -> Tuple[np.ndarray, np.ndarray, float]:
    """Compute R2 score for model predictions."""
    model.eval()
    all_preds = []
    all_targets = []

    with torch.no_grad():
        for batch, labels in loader:
            labels = labels.to(device)

            if model_kind == "mlp":
                x = flatten_weights(batch).to(device)
                pred = model(x).squeeze(-1)
            else:
                batch = batch.to(device)
                pred = model(batch).squeeze(-1)

            all_preds.append(pred.cpu().numpy())
            all_targets.append(labels.cpu().numpy())

    preds = np.concatenate(all_preds)
    targets = np.concatenate(all_targets)
    r2 = r2_score(targets, preds)

    return preds, targets, r2


def compare_models(nfn_result: Tuple, mlp_result: Tuple, threshold: float = 0.05) -> Dict:
    """Compare NFN and MLP results."""
    _, _, nfn_r2 = nfn_result
    _, _, mlp_r2 = mlp_result

    difference = nfn_r2 - mlp_r2
    hypothesis_supported = difference > threshold

    return {
        "nfn_r2": float(nfn_r2),
        "mlp_r2": float(mlp_r2),
        "difference": float(difference),
        "threshold": threshold,
        "hypothesis_supported": hypothesis_supported
    }


def plot_r2_comparison(nfn_r2: float, mlp_r2: float, threshold: float, out_path: str) -> None:
    """Plot R2 comparison bar chart."""
    fig, ax = plt.subplots(figsize=(8, 6))

    models = ['NFN', 'MLP-Matched']
    r2_scores = [nfn_r2, mlp_r2]
    colors = ['#2ecc71', '#e74c3c']

    bars = ax.bar(models, r2_scores, color=colors, edgecolor='black', linewidth=1.2)

    ax.axhline(y=mlp_r2 + threshold, color='#3498db', linestyle='--', linewidth=2,
               label=f'Threshold (MLP + {threshold})')

    ax.set_ylabel('R² Score', fontsize=12)
    ax.set_title('NFN vs MLP-Matched: Weight Space Accuracy Prediction', fontsize=14)
    ax.set_ylim(0, 1)
    ax.legend()

    for bar, score in zip(bars, r2_scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{score:.3f}', ha='center', va='bottom', fontsize=11)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_scatter(preds: np.ndarray, targets: np.ndarray, title: str, out_path: str) -> None:
    """Plot predicted vs actual scatter."""
    fig, ax = plt.subplots(figsize=(7, 7))

    ax.scatter(targets, preds, alpha=0.6, edgecolors='black', linewidth=0.5)

    min_val = min(targets.min(), preds.min())
    max_val = max(targets.max(), preds.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Ideal')

    ax.set_xlabel('Actual Accuracy', fontsize=12)
    ax.set_ylabel('Predicted Accuracy', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend()
    ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_residuals(preds: np.ndarray, targets: np.ndarray, title: str, out_path: str) -> None:
    """Plot residual distribution."""
    residuals = preds - targets

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals, bins=30, edgecolor='black', alpha=0.7)
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2)

    ax.set_xlabel('Residual (Predicted - Actual)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title(title, fontsize=14)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_learning_curves(history: Dict, title: str, out_path: str) -> None:
    """Plot training/validation loss curves."""
    fig, ax = plt.subplots(figsize=(8, 5))

    epochs = range(1, len(history['train_loss']) + 1)
    ax.plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=2)
    ax.plot(epochs, history['val_loss'], 'r-', label='Val Loss', linewidth=2)

    ax.set_xlabel('Epoch', fontsize=12)
    ax.set_ylabel('MSE Loss', fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.legend()
    ax.set_yscale('log')

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    plt.close()


def save_results_json(results: Dict, out_path: str) -> None:
    """Save results to JSON file."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
