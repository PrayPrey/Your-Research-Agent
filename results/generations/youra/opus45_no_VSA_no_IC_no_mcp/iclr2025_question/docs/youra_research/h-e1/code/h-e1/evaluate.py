import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import config

def compute_auroc(labels: np.ndarray, scores: np.ndarray) -> float:
    if len(np.unique(labels)) < 2:
        return 0.5
    return roc_auc_score(labels, scores)

def bootstrap_ci(labels: np.ndarray, scores: np.ndarray, n_bootstrap: int = 1000, seed: int = 42) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    n = len(labels)
    aurocs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        l_boot, s_boot = labels[idx], scores[idx]
        if len(np.unique(l_boot)) < 2:
            continue
        aurocs.append(roc_auc_score(l_boot, s_boot))
    if not aurocs:
        return 0.5, 0.5
    return np.percentile(aurocs, 2.5), np.percentile(aurocs, 97.5)

def plot_roc_curves(labels: np.ndarray, entropy: np.ndarray, consistency: np.ndarray, path: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    for name, scores in [("Entropy", entropy), ("Consistency (neg)", -consistency)]:
        fpr, tpr, _ = roc_curve(labels, scores)
        auc = roc_auc_score(labels, scores) if len(np.unique(labels)) >= 2 else 0.5
        ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", label="Random")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title("ROC Curves")
    ax.legend()
    fig.savefig(path, dpi=150)
    plt.close(fig)
