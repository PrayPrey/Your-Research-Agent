"""AUROC computation, results saving, and figure generation."""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def compute_metrics(results: list) -> dict:
    """
    Compute AUROC and std for SMC-NLI and SMC-Embed.
    results: list of {"label": int, "smc_nli": float, "smc_embed": float}
    Returns dict with smc_nli_auroc, smc_embed_auroc, smc_nli_std, smc_embed_std.
    """
    labels = np.array([r["label"] for r in results])
    nli_scores = np.array([r["smc_nli"] for r in results])
    embed_scores = np.array([r["smc_embed"] for r in results])

    # Lower SMC-NLI = more hallucinated → negate for AUROC
    smc_nli_auroc = roc_auc_score(labels, -nli_scores)
    smc_embed_auroc = roc_auc_score(labels, -embed_scores)

    return {
        "smc_nli_auroc": float(smc_nli_auroc),
        "smc_embed_auroc": float(smc_embed_auroc),
        "smc_nli_std": float(np.std(nli_scores)),
        "smc_embed_std": float(np.std(embed_scores)),
        "n_questions": len(results),
        "n_correct": int((labels == 0).sum()),
        "n_hallucinated": int((labels == 1).sum()),
        "smc_nli_mean_correct": float(nli_scores[labels == 0].mean()),
        "smc_nli_mean_hallucinated": float(nli_scores[labels == 1].mean()),
    }


def save_results(results: list, metrics: dict, path: str = "outputs/results.json") -> None:
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    payload = {"metrics": metrics, "results": results}
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Results saved to {path}")


def plot_figures(results: list, metrics: dict, fig_dir: str = "figures/") -> None:
    os.makedirs(fig_dir, exist_ok=True)

    labels = np.array([r["label"] for r in results])
    nli_scores = np.array([r["smc_nli"] for r in results])
    embed_scores = np.array([r["smc_embed"] for r in results])

    # Figure 1: AUROC bar chart
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ["Random\nBaseline", "SMC-NLI\nAUROC", "SMC-Embed\nAUROC"]
    vals = [0.50, metrics["smc_nli_auroc"], metrics["smc_embed_auroc"]]
    colors = ["gray", "steelblue", "darkorange"]
    ax.bar(bars, vals, color=colors, alpha=0.8)
    ax.axhline(0.60, color="red", linestyle="--", label="Gate threshold (0.60)")
    ax.set_ylim(0, 1)
    ax.set_ylabel("AUROC")
    ax.set_title("H-E1: SMC-NLI vs Baselines")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "auroc_comparison.png"), dpi=150)
    plt.close()

    # Figure 2: SMC-NLI score distribution by label
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(nli_scores[labels == 0], bins=40, alpha=0.6, label="Correct (label=0)", color="steelblue")
    ax.hist(nli_scores[labels == 1], bins=40, alpha=0.6, label="Hallucinated (label=1)", color="salmon")
    ax.set_xlabel("SMC-NLI Score")
    ax.set_ylabel("Count")
    ax.set_title("SMC-NLI Score Distribution by Label")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "smc_nli_distribution.png"), dpi=150)
    plt.close()

    # Figure 3: ROC curves
    fig, ax = plt.subplots(figsize=(6, 6))
    fpr_nli, tpr_nli, _ = roc_curve(labels, -nli_scores)
    fpr_emb, tpr_emb, _ = roc_curve(labels, -embed_scores)
    ax.plot(fpr_nli, tpr_nli, label=f"SMC-NLI (AUC={metrics['smc_nli_auroc']:.3f})", color="steelblue")
    ax.plot(fpr_emb, tpr_emb, label=f"SMC-Embed (AUC={metrics['smc_embed_auroc']:.3f})", color="darkorange")
    ax.plot([0, 1], [0, 1], "k--", label="Random (AUC=0.50)")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    ax.set_title("ROC Curves: H-E1")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "roc_curves.png"), dpi=150)
    plt.close()

    # Figure 4: SMC-NLI vs SMC-Embed scatter
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(nli_scores[labels == 0], embed_scores[labels == 0],
               alpha=0.3, s=10, label="Correct", color="steelblue")
    ax.scatter(nli_scores[labels == 1], embed_scores[labels == 1],
               alpha=0.3, s=10, label="Hallucinated", color="salmon")
    ax.set_xlabel("SMC-NLI Score")
    ax.set_ylabel("SMC-Embed Score")
    ax.set_title("SMC-NLI vs SMC-Embed (per question)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "nli_vs_embed_scatter.png"), dpi=150)
    plt.close()

    print(f"Saved 4 figures to {fig_dir}")
