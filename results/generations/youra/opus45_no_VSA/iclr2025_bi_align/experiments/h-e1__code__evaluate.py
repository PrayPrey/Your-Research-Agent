import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve
import config


def compute_auroc(y_true, y_score):
    """Compute AUROC; handle edge cases."""
    y_true = np.array(y_true)
    y_score = np.array(y_score)
    if len(np.unique(y_true)) < 2:
        return 0.5
    return roc_auc_score(y_true, y_score)


def evaluate_all_proxies(detector_results):
    """Compute AUROC for each proxy."""
    results = {}
    for proxy, (y_true, y_score) in detector_results.items():
        results[proxy] = compute_auroc(y_true, y_score)
    return results


def plot_auroc_bar(results, out_path):
    """Bar chart of AUROC per proxy with target line."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    proxies = list(results.keys())
    aurocs = [results[p] for p in proxies]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(proxies, aurocs, color="steelblue", edgecolor="black")
    plt.axhline(y=config.AUROC_TARGET, color="red", linestyle="--", label=f"Target ({config.AUROC_TARGET})")
    plt.axhline(y=config.AUROC_BASELINE_MIN, color="gray", linestyle=":", label=f"Baseline ({config.AUROC_BASELINE_MIN})")
    plt.ylim(0, 1)
    plt.ylabel("AUROC")
    plt.xlabel("Agency Proxy Type")
    plt.title("Agency Proxy Detection AUROC")
    plt.legend()
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curves(detector_results, out_path):
    """2x2 ROC curve subplots."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes = axes.flatten()

    for i, (proxy, (y_true, y_score)) in enumerate(detector_results.items()):
        ax = axes[i]
        y_true = np.array(y_true)
        y_score = np.array(y_score)
        if len(np.unique(y_true)) < 2:
            ax.plot([0, 1], [0, 1], "k--")
            ax.set_title(f"{proxy}\n(single class)")
        else:
            fpr, tpr, _ = roc_curve(y_true, y_score)
            auroc = roc_auc_score(y_true, y_score)
            ax.plot(fpr, tpr, color="steelblue", lw=2, label=f"AUROC={auroc:.3f}")
            ax.plot([0, 1], [0, 1], "k--", lw=1)
            ax.set_title(proxy)
            ax.legend(loc="lower right")
        ax.set_xlabel("FPR")
        ax.set_ylabel("TPR")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
