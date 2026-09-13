import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
import torch.nn as nn

from data.loader import ZooData, make_loader
from training.train import predict_all


def plot_spearman_bar(results: dict, threshold: float, save_dir: str):
    names = list(results.keys())
    test_rs = [results[n]["test_r"] for n in names]
    colors = ["#2ecc71" if r > threshold else "#e74c3c" for r in test_rs]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, test_rs, color=colors, edgecolor="k", linewidth=0.8)
    ax.axhline(threshold, color="navy", linestyle="--", linewidth=1.5,
               label=f"Gate threshold = {threshold}")
    ax.set_ylabel("Test Spearman r (gap)")
    ax.set_title("H-E1: Encoder Spearman r on Generalization Gap (Test Set)")
    ax.set_ylim(-0.1, 1.05)
    ax.legend()
    for bar, r in zip(bars, test_rs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{r:.3f}", ha="center", va="bottom", fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "encoder_gap_spearman.png"), dpi=150)
    plt.close()


def plot_best_scatter(model: nn.Module, zoo: ZooData, split: str,
                      encoder_name: str, device: str, save_dir: str):
    loader = make_loader(zoo, split, batch_size=128, shuffle=False)
    preds, targets = predict_all(model, loader, device)
    preds = np.array(preds)
    targets = np.array(targets)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(targets, preds, alpha=0.3, s=5, color="#3498db")
    lo = min(targets.min(), preds.min())
    hi = max(targets.max(), preds.max())
    ax.plot([lo, hi], [lo, hi], "r--", linewidth=1.5, label="y=x")
    ax.set_xlabel("True gap")
    ax.set_ylabel("Predicted gap")
    ax.set_title(f"Best encoder: {encoder_name} (test set)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "best_encoder_scatter.png"), dpi=150)
    plt.close()


def plot_gap_histogram(zoo: ZooData, save_dir: str):
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(zoo.gap, bins=60, color="#9b59b6", edgecolor="k", linewidth=0.5)
    ax.set_xlabel("Generalization gap (train_acc - test_acc)")
    ax.set_ylabel("Count")
    ax.set_title("H-E1: Gap distribution across zoo")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "gap_distribution.png"), dpi=150)
    plt.close()


def plot_audit_scatter(zoo: ZooData, audit_r: float, save_dir: str):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(-zoo.test_acc, zoo.gap, alpha=0.2, s=3, color="#e67e22")
    ax.set_xlabel("-test_acc")
    ax.set_ylabel("gap = train_acc - test_acc")
    ax.set_title(f"A1 Audit: Spearman(gap, -test_acc) = {audit_r:.4f}")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "a1_audit_scatter.png"), dpi=150)
    plt.close()


def plot_training_curves(curves: dict, save_dir: str):
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12"]
    for (name, curve), color in zip(curves.items(), colors):
        ax.plot(curve, label=name, color=color, linewidth=1.5)
    ax.axhline(0.5, color="navy", linestyle="--", linewidth=1.2, label="Gate (r=0.5)")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Val Spearman r (gap)")
    ax.set_title("H-E1: Training curves — val Spearman per encoder")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "training_curves.png"), dpi=150)
    plt.close()
