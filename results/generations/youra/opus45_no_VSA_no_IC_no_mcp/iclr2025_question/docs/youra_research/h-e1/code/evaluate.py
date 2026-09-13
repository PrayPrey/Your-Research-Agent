"""Evaluation: AUROC, bootstrap CI, plotting."""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve
from config import CONFIG


def compute_auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    """Compute AUROC."""
    if len(np.unique(labels)) < 2:
        return 0.5
    return roc_auc_score(labels, scores)


def bootstrap_ci(
    labels: np.ndarray,
    scores: np.ndarray,
    n_bootstrap: int = None,
    seed: int = None
) -> tuple[float, float]:
    """Compute bootstrap 95% CI for AUROC."""
    n_bootstrap = n_bootstrap or CONFIG["N_BOOTSTRAP"]
    seed = seed or CONFIG["SEED"]

    rng = np.random.default_rng(seed)
    aurocs = []
    n = len(labels)

    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        if len(np.unique(labels[idx])) < 2:
            continue
        aurocs.append(roc_auc_score(labels[idx], scores[idx]))

    if not aurocs:
        return 0.5, 0.5

    return float(np.percentile(aurocs, 2.5)), float(np.percentile(aurocs, 97.5))


def plot_roc_curves(
    labels: np.ndarray,
    entropy: np.ndarray,
    consistency: np.ndarray,
    path: str
) -> None:
    """Plot ROC curves for both methods."""
    fig, ax = plt.subplots(figsize=(8, 6))

    # Entropy ROC
    fpr_e, tpr_e, _ = roc_curve(labels, entropy)
    auc_e = compute_auroc(labels, entropy)
    ax.plot(fpr_e, tpr_e, label=f"Entropy (AUROC={auc_e:.3f})")

    # Consistency ROC (flip sign: lower consistency = more hallucinated)
    fpr_c, tpr_c, _ = roc_curve(labels, -consistency)
    auc_c = compute_auroc(labels, -consistency)
    ax.plot(fpr_c, tpr_c, label=f"Consistency (AUROC={auc_c:.3f})")

    ax.plot([0, 1], [0, 1], "k--", label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: Entropy vs Consistency")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
