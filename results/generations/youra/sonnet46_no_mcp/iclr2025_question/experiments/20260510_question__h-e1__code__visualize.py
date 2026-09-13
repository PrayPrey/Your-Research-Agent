from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve


METHOD_COLORS = {
    "token_entropy_mean": "#4C72B0",       # blue
    "semantic_entropy": "#55A868",          # green
    "selfcheckgpt_bertscore_n5": "#DD8452", # orange
}

METHOD_LABELS = {
    "token_entropy_mean": "Token Entropy (mean)",
    "semantic_entropy": "Semantic Entropy",
    "selfcheckgpt_bertscore_n5": "SelfCheckGPT-BERTScore",
}


def plot_auroc_bar_chart(
    auroc_map: Dict[str, float],
    ci_map: Dict[str, Tuple[float, float]],
    save_path: str,
) -> None:
    methods = list(auroc_map.keys())
    aurocs = [auroc_map[m] for m in methods]
    labels = [METHOD_LABELS.get(m, m) for m in methods]
    colors = [METHOD_COLORS.get(m, "gray") for m in methods]

    yerr_lower = [auroc_map[m] - ci_map[m][0] for m in methods]
    yerr_upper = [ci_map[m][1] - auroc_map[m] for m in methods]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(methods))
    ax.bar(x, aurocs, color=colors, alpha=0.85,
           yerr=[yerr_lower, yerr_upper], capsize=5, error_kw={"elinewidth": 1.5})
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylim(0.4, 1.0)
    ax.set_ylabel("AUROC")
    ax.set_title("AUROC per UQ Method (with 95% Bootstrap CI)\nH-E1: HaluEval-QA, LLaMA-2-7B-chat")
    ax.axhline(0.5, color="black", linestyle="--", linewidth=0.8, alpha=0.5, label="Random")
    ax.legend(fontsize=9)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_roc_curves_overlay(
    labels: List[int],
    scores_map: Dict[str, List[float]],
    auroc_map: Dict[str, float],
    save_path: str,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    for method, scores in scores_map.items():
        fpr, tpr, _ = roc_curve(labels, scores)
        auc_val = auroc_map.get(method, 0.0)
        label = f"{METHOD_LABELS.get(method, method)} (AUC={auc_val:.3f})"
        color = METHOD_COLORS.get(method, "gray")
        ax.plot(fpr, tpr, color=color, label=label, linewidth=2)

    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8, alpha=0.5, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves — UQ Methods\nH-E1: HaluEval-QA, LLaMA-2-7B-chat")
    ax.legend(fontsize=9, loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
