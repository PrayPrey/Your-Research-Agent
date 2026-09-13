import os
import torch
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def evaluate_auroc(probe, hidden_states: torch.Tensor, labels: torch.Tensor) -> tuple:
    probe.eval()
    with torch.no_grad():
        preds = probe(hidden_states).squeeze().numpy()
    labels_np = labels.numpy()
    auroc = roc_auc_score(labels_np, preds)
    return auroc, preds, labels_np


def plot_gate_comparison(auroc: float, baseline: float, gate: float, out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(["Probe AUROC", "Random Baseline", "Gate Threshold"],
                  [auroc, baseline, gate],
                  color=["#2196F3", "#9E9E9E", "#FF5722"])

    for bar, val in zip(bars, [auroc, baseline, gate]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=12)

    ax.set_ylabel("AUROC")
    ax.set_ylim(0, 1)
    ax.axhline(y=gate, color="#FF5722", linestyle="--", alpha=0.7, label=f"Gate: {gate}")
    ax.set_title("Probe AUROC vs Gate Threshold")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curve(labels: np.ndarray, preds: np.ndarray, auroc: float, out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    fpr, tpr, _ = roc_curve(labels, preds)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(fpr, tpr, color="#2196F3", lw=2, label=f"ROC (AUROC = {auroc:.3f})")
    ax.plot([0, 1], [0, 1], color="#9E9E9E", lw=2, linestyle="--", label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve")
    ax.legend(loc="lower right")
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_loss_curve(losses: list, out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(range(1, len(losses)+1), losses, marker="o", color="#2196F3", lw=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("BCE Loss")
    ax.set_title("Training Loss Curve")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_hidden_state_pca(hidden_states: torch.Tensor, labels: torch.Tensor, out_path: str, n_samples: int = 5000):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    if hidden_states.shape[0] > n_samples:
        indices = np.random.choice(hidden_states.shape[0], n_samples, replace=False)
        h = hidden_states[indices].numpy()
        l = labels[indices].numpy()
    else:
        h = hidden_states.numpy()
        l = labels.numpy()

    pca = PCA(n_components=2)
    coords = pca.fit_transform(h)

    fig, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(coords[:, 0], coords[:, 1], c=l, cmap="coolwarm", alpha=0.5, s=10)
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_title("Hidden States PCA (colored by correctness)")
    plt.colorbar(scatter, label="Correct")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
