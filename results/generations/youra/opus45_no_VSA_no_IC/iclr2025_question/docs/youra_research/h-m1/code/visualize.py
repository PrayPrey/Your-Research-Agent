"""Visualization for h-m1."""

import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve
from sklearn.calibration import calibration_curve

from config import FIGURES_DIR, AUROC_PASS_THRESHOLD


def _ensure_dir():
    os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_gate_metric(auroc: float, threshold: float, out_path: str = None) -> None:
    """Mandatory: bar chart AUROC vs threshold."""
    _ensure_dir()
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "gate.png")

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['green' if auroc >= threshold else 'red', 'gray']
    bars = ax.bar(['AUROC', 'Threshold'], [auroc, threshold], color=colors)
    ax.axhline(y=threshold, color='black', linestyle='--', alpha=0.7)
    ax.set_ylim(0, 1)
    ax.set_ylabel('Score')
    ax.set_title(f'Gate Check: {"PASS" if auroc >= threshold else "FAIL"}')
    for bar, val in zip(bars, [auroc, threshold]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_roc_curve(y_true: list, y_pred_proba: np.ndarray, out_path: str = None) -> None:
    """ROC curve."""
    _ensure_dir()
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "roc.png")

    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, 'b-', linewidth=2)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve (Cross-Dataset Transfer)')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_layer_analysis(layer_aurocs: dict, out_path: str = None) -> None:
    """Line plot: layer_idx vs AUROC."""
    _ensure_dir()
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "layer_analysis.png")

    layers = sorted(layer_aurocs.keys())
    aurocs = [layer_aurocs[l] for l in layers]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(layers, aurocs, 'bo-', linewidth=2, markersize=8)
    ax.axhline(y=AUROC_PASS_THRESHOLD, color='green', linestyle='--', label=f'Threshold={AUROC_PASS_THRESHOLD}')
    ax.set_xlabel('Layer Index')
    ax.set_ylabel('AUROC')
    ax.set_title('Layer Ablation: AUROC by Layer')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_calibration(y_true: list, y_pred_proba: np.ndarray, out_path: str = None) -> None:
    """Reliability diagram."""
    _ensure_dir()
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "calibration.png")

    prob_true, prob_pred = calibration_curve(y_true, y_pred_proba, n_bins=10, strategy='uniform')

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(prob_pred, prob_true, 'bo-', linewidth=2, markersize=8, label='Probe')
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect calibration')
    ax.set_xlabel('Mean Predicted Probability')
    ax.set_ylabel('Fraction of Positives')
    ax.set_title('Calibration Curve')
    ax.legend()
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")


def plot_distribution_comparison(train_proba: np.ndarray, eval_proba: np.ndarray, out_path: str = None) -> None:
    """Overlaid histograms: train vs eval probe outputs."""
    _ensure_dir()
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "dist.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(train_proba, bins=30, alpha=0.5, label='TriviaQA (train)', density=True)
    ax.hist(eval_proba, bins=30, alpha=0.5, label='TruthfulQA (eval)', density=True)
    ax.set_xlabel('Probe Output (P(high SE))')
    ax.set_ylabel('Density')
    ax.set_title('Probe Output Distribution: Train vs Eval')
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved: {out_path}")
