# visualize.py - 4 required figures
import os
import numpy as np
import matplotlib.pyplot as plt
from config import CONFIG


def plot_gate_metrics(cv_results, save_path=None):
    """Bar chart of AUROC per fold + mean with threshold line."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "gate_metrics.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fold_aurocs = cv_results["fold_aurocs"]
    mean_auroc = cv_results["mean_auroc"]
    threshold = CONFIG["auroc_threshold"]

    fig, ax = plt.subplots(figsize=(8, 5))
    x_labels = [f"Fold {i+1}" for i in range(len(fold_aurocs))] + ["Mean"]
    x_pos = list(range(len(x_labels)))
    values = fold_aurocs + [mean_auroc]
    colors = ["green" if v > threshold else "red" for v in values]

    ax.bar(x_pos, values, color=colors, alpha=0.7, edgecolor="black")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels)
    ax.axhline(y=threshold, color="orange", linestyle="--", label=f"Threshold ({threshold})")
    ax.set_xlabel("Fold")
    ax.set_ylabel("AUROC")
    ax.set_title("NTI Gate Metrics: AUROC per Fold")
    ax.set_ylim(0.4, 0.8)
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_entropy_heatmap(trajectory, save_path=None, max_samples=100):
    """Entropy trajectory heatmap (layer × sample)."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "entropy_heatmap.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Subsample for visualization
    if len(trajectory) > max_samples:
        idx = np.random.choice(len(trajectory), max_samples, replace=False)
        trajectory = trajectory[idx]

    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(trajectory.T, aspect="auto", cmap="viridis")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Layer (24-32)")
    ax.set_yticks(range(9))
    ax.set_yticklabels([f"L{i}" for i in range(24, 33)])
    ax.set_title("Entropy Trajectory Heatmap")
    plt.colorbar(im, ax=ax, label="Entropy")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_nti_distribution(nti_scores, labels, save_path=None):
    """NTI distribution histogram (correct vs hallucinated)."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "nti_distribution.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    correct_nti = nti_scores[labels == 1]
    wrong_nti = nti_scores[labels == 0]

    ax.hist(correct_nti, bins=30, alpha=0.6, label="Correct", color="green", density=True)
    ax.hist(wrong_nti, bins=30, alpha=0.6, label="Incorrect", color="red", density=True)
    ax.set_xlabel("NTI Score")
    ax.set_ylabel("Density")
    ax.set_title("NTI Distribution: Correct vs Incorrect Answers")
    ax.legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path


def plot_roc_curves(cv_results, save_path=None):
    """ROC curves per fold + mean."""
    save_path = save_path or os.path.join(CONFIG["figures_dir"], "roc_curves.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot each fold
    for i, (fpr, tpr) in enumerate(cv_results["roc_curves"]):
        auroc = cv_results["fold_aurocs"][i]
        ax.plot(fpr, tpr, alpha=0.5, label=f"Fold {i+1} (AUC={auroc:.3f})")

    # Diagonal
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random")

    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"ROC Curves (Mean AUC={cv_results['mean_auroc']:.3f})")
    ax.legend(loc="lower right", fontsize=8)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    return save_path
