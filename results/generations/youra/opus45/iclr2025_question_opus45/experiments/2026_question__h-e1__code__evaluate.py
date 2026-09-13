"""Evaluation metrics and visualization for SEDP experiment."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score, roc_curve

from config import ExperimentConfig


def compute_metrics(
    probe_proba: np.ndarray,
    se_continuous: np.ndarray,
    se_binary: np.ndarray,
) -> dict:
    """Compute Spearman rho, p-value, and AUROC."""
    rho, p_value = spearmanr(probe_proba, se_continuous)
    auroc = roc_auc_score(se_binary, probe_proba)

    return {
        "spearman_rho": float(rho),
        "p_value": float(p_value),
        "auroc": float(auroc),
    }


def plot_gate_metrics(
    sep_metrics: dict,
    sedp_metrics: dict,
    save_path: str,
) -> None:
    """Bar chart: rho for SEP vs SEDP with threshold line at 0.3."""
    fig, ax = plt.subplots(figsize=(8, 6))

    methods = ["SEP (baseline)", "SEDP (proposed)"]
    rho_values = [sep_metrics["spearman_rho"], sedp_metrics["spearman_rho"]]
    colors = ["#2196F3", "#4CAF50"]

    bars = ax.bar(methods, rho_values, color=colors, width=0.5, edgecolor="black")

    # Add threshold line
    ax.axhline(y=0.3, color="red", linestyle="--", linewidth=2, label="Gate threshold (0.3)")

    # Add value labels on bars
    for bar, val in zip(bars, rho_values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_ylabel("Spearman rho", fontsize=12)
    ax.set_title("SEDP vs SEP: Spearman Correlation with True SE", fontsize=14)
    ax.set_ylim(0, max(rho_values) * 1.2 + 0.1)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved gate metrics plot to {save_path}")


def plot_scatter(
    sep_proba: np.ndarray,
    sedp_proba: np.ndarray,
    se_true: np.ndarray,
    save_path: str,
) -> None:
    """Scatter plot: predicted SE vs true SE for both methods."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # SEP scatter
    axes[0].scatter(se_true, sep_proba, alpha=0.6, c="#2196F3", edgecolors="none")
    axes[0].set_xlabel("True SE", fontsize=11)
    axes[0].set_ylabel("Predicted probability", fontsize=11)
    axes[0].set_title("SEP (baseline)", fontsize=12)
    axes[0].grid(alpha=0.3)

    # SEDP scatter
    axes[1].scatter(se_true, sedp_proba, alpha=0.6, c="#4CAF50", edgecolors="none")
    axes[1].set_xlabel("True SE", fontsize=11)
    axes[1].set_ylabel("Predicted probability", fontsize=11)
    axes[1].set_title("SEDP (proposed)", fontsize=12)
    axes[1].grid(alpha=0.3)

    plt.suptitle("Predicted vs True Semantic Entropy", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved scatter plot to {save_path}")


def plot_roc_curves(
    sep_proba: np.ndarray,
    sedp_proba: np.ndarray,
    se_binary: np.ndarray,
    save_path: str,
) -> None:
    """ROC curves comparison."""
    fig, ax = plt.subplots(figsize=(8, 6))

    # SEP ROC
    fpr_sep, tpr_sep, _ = roc_curve(se_binary, sep_proba)
    auc_sep = roc_auc_score(se_binary, sep_proba)
    ax.plot(fpr_sep, tpr_sep, color="#2196F3", linewidth=2,
            label=f"SEP (AUROC = {auc_sep:.3f})")

    # SEDP ROC
    fpr_sedp, tpr_sedp, _ = roc_curve(se_binary, sedp_proba)
    auc_sedp = roc_auc_score(se_binary, sedp_proba)
    ax.plot(fpr_sedp, tpr_sedp, color="#4CAF50", linewidth=2,
            label=f"SEDP (AUROC = {auc_sedp:.3f})")

    # Diagonal
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1)

    ax.set_xlabel("False Positive Rate", fontsize=11)
    ax.set_ylabel("True Positive Rate", fontsize=11)
    ax.set_title("ROC Curves: High SE Detection", fontsize=14)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved ROC curves to {save_path}")


def save_results(
    sep_metrics: dict,
    sedp_metrics: dict,
    output_path: str,
    gate_pass: bool,
) -> None:
    """Write markdown results table."""
    gate_status = "PASS" if gate_pass else "FAIL"
    gate_emoji = "+" if gate_pass else "-"

    content = f"""# H-E1 Validation Results

## Gate Status: **{gate_status}**

SEDP Spearman rho = {sedp_metrics['spearman_rho']:.4f} {'≥' if gate_pass else '<'} 0.3 threshold

---

## Metrics Summary

| Metric | SEP (baseline) | SEDP (proposed) | Delta |
|--------|----------------|-----------------|-------|
| Spearman rho | {sep_metrics['spearman_rho']:.4f} | {sedp_metrics['spearman_rho']:.4f} | {sedp_metrics['spearman_rho'] - sep_metrics['spearman_rho']:+.4f} |
| p-value | {sep_metrics['p_value']:.2e} | {sedp_metrics['p_value']:.2e} | - |
| AUROC | {sep_metrics['auroc']:.4f} | {sedp_metrics['auroc']:.4f} | {sedp_metrics['auroc'] - sep_metrics['auroc']:+.4f} |

---

## Effect Direction

- SEDP {'>' if sedp_metrics['spearman_rho'] > sep_metrics['spearman_rho'] else '<='} SEP: **{'Confirmed' if sedp_metrics['spearman_rho'] > sep_metrics['spearman_rho'] else 'Not confirmed'}**

---

## Figures

- `figures/gate_metrics.png` - Bar chart with gate threshold
- `figures/scatter.png` - Predicted vs True SE scatter
- `figures/roc_curves.png` - ROC comparison

---

## Gate Check

```
[{gate_emoji}] SEDP rho >= 0.3: {sedp_metrics['spearman_rho']:.4f} {'≥' if gate_pass else '<'} 0.3
```

---

*Generated by h-e1 experiment pipeline*
"""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)
    print(f"Saved results to {output_path}")
