"""Visualization for H-M3"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

H_M3_CODE = os.path.dirname(os.path.abspath(__file__))
H_M3_DIR = os.path.dirname(H_M3_CODE)
FIGURES_DIR = os.path.join(H_M3_DIR, "figures")


def plot_sharpness_vs_rank(task_metrics, rho, out_path=None):
    """Required: scatter (sharpness, effective_rank) per task, rho annotated."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "sharpness_vs_rank.png")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    tasks = list(task_metrics.keys())
    sharpness = [task_metrics[t]["mean_sharpness"] for t in tasks]
    ranks = [task_metrics[t]["effective_rank"] for t in tasks]

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, len(tasks)))

    for i, task in enumerate(tasks):
        ax.scatter(sharpness[i], ranks[i], c=[colors[i]], s=150, label=task, edgecolors='black', linewidth=1.5)

    if len(tasks) >= 2:
        z = np.polyfit(sharpness, ranks, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(sharpness) * 0.9, max(sharpness) * 1.1, 100)
        ax.plot(x_line, p(x_line), "--", color="gray", alpha=0.7, label=f"Linear fit")

    ax.set_xlabel("Sharpness (SAM)", fontsize=12)
    ax.set_ylabel("Effective Rank", fontsize=12)
    ax.set_title(f"Sharpness vs LoRA Effective Rank\nSpearman ρ = {rho:.3f}", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_singular_values(singular_values, out_path=None):
    """Per-task SVD spectrum overlay (line plot, log-y)."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "sv_distribution.png")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    for task, sv_dict in singular_values.items():
        for module_name, svs in sv_dict.items():
            if svs:
                ax.semilogy(svs[:20], label=f"{task} - {module_name.split('.')[-1]}", marker='o', markersize=4)

    ax.set_xlabel("Singular Value Index", fontsize=12)
    ax.set_ylabel("Singular Value (log scale)", fontsize=12)
    ax.set_title("LoRA Singular Value Distribution", fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_generalization_gap(task_metrics, out_path=None):
    """Scatter sharpness vs gen_gap."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "gen_gap.png")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    tasks = list(task_metrics.keys())
    sharpness = [task_metrics[t]["mean_sharpness"] for t in tasks]
    gen_gaps = [task_metrics[t]["gen_gap"] for t in tasks]

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, len(tasks)))

    for i, task in enumerate(tasks):
        ax.scatter(sharpness[i], gen_gaps[i], c=[colors[i]], s=150, label=task, edgecolors='black', linewidth=1.5)

    ax.set_xlabel("Sharpness (SAM)", fontsize=12)
    ax.set_ylabel("Generalization Gap (train - test acc)", fontsize=12)
    ax.set_title("Sharpness vs Generalization Gap", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_training_curves(loss_curves, out_path=None):
    """Per-task loss curve over epochs."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "training_curves.png")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    for task, losses in loss_curves.items():
        epochs = list(range(1, len(losses) + 1))
        ax.plot(epochs, losses, marker='o', label=task, linewidth=2)

    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Loss", fontsize=12)
    ax.set_title("Training Loss Curves", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path


def plot_correlation_matrix(task_metrics, out_path=None):
    """Heatmap: sharpness, effective_rank, gen_gap, train_acc, test_acc pairwise corr."""
    if out_path is None:
        out_path = os.path.join(FIGURES_DIR, "corr_matrix.png")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    tasks = list(task_metrics.keys())

    metrics = ["mean_sharpness", "effective_rank", "gen_gap", "train_acc", "test_acc"]
    labels = ["Sharpness", "Effective Rank", "Gen Gap", "Train Acc", "Test Acc"]

    data = []
    for m in metrics:
        data.append([task_metrics[t].get(m, 0) for t in tasks])

    data = np.array(data)

    if data.shape[1] < 2:
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.text(0.5, 0.5, "Not enough data points\nfor correlation matrix", ha='center', va='center', fontsize=14)
        ax.axis('off')
        plt.savefig(out_path, dpi=150)
        plt.close()
        return out_path

    corr = np.corrcoef(data)

    fig, ax = plt.subplots(figsize=(8, 7))

    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)

    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{corr[i, j]:.2f}", ha='center', va='center', color='black')

    ax.set_title("Metric Correlation Matrix", fontsize=14)
    plt.colorbar(im, ax=ax, label="Correlation")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

    return out_path
