import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve


def plot_gate_comparison(auc: float, threshold: float, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["AUC"], [auc], color="steelblue", edgecolor="black")
    ax.axhline(y=threshold, color="red", linestyle="--", label=f"Threshold ({threshold})")
    ax.set_ylim(0, 1)
    ax.set_ylabel("AUC")
    ax.set_title("Gate Comparison: AUC vs Threshold")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_cv_distribution(cv_values: dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = list(cv_values.keys())
    values = [cv_values[k] for k in labels]
    colors = ["salmon" if "background" in k.lower() else "lightgreen" for k in labels]

    ax.bar(labels, values, color=colors, edgecolor="black")
    ax.set_ylabel("CV")
    ax.set_title("CV Distribution by Feature Type")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_roc_curve(cv_values: list, ground_truth: list, out_path: str) -> None:
    scores = -np.array(cv_values)
    fpr, tpr, _ = roc_curve(ground_truth, scores)

    from sklearn.metrics import roc_auc_score
    auc = roc_auc_score(ground_truth, scores)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="steelblue", lw=2, label=f"ROC (AUC = {auc:.2f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve: CV-based Spurious Detection")
    ax.legend(loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


def plot_trajectories(trajectories: dict, out_path: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    n_epochs = len(trajectories["background"][0])
    x = np.arange(1, n_epochs + 1)

    for i, traj in enumerate(trajectories["background"]):
        axes[0].plot(x, traj, marker="o", markersize=3, label=f"Subset {i+1}")
    axes[0].set_xlabel("C checkpoint")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_title("Background (Spurious) - Probe Trajectories")
    axes[0].legend(fontsize=8)

    for i, traj in enumerate(trajectories["bird_type"]):
        axes[1].plot(x, traj, marker="o", markersize=3, label=f"Subset {i+1}")
    axes[1].set_xlabel("C checkpoint")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_title("Bird Type (Core) - Probe Trajectories")
    axes[1].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
