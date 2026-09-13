"""Visualization functions for CARE experiment results."""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import roc_curve, precision_recall_curve
import os


def plot_coverage_vs_alpha(coverage_results, output_path):
    """
    Plot empirical coverage rate vs nominal 1-alpha for CARE (UQM).
    Shows calibration quality.
    """
    alphas = sorted(coverage_results.keys())
    nominal = [1 - a for a in alphas]
    empirical = [coverage_results[a] for a in alphas]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(nominal, nominal, "k--", label="Ideal (empirical = nominal)", lw=1.5)
    ax.plot(nominal, empirical, "bo-", label="CARE (UQM)", markersize=8, lw=2)

    ax.fill_between(nominal,
                    [n - 0.02 for n in nominal],
                    [n + 0.02 for n in nominal],
                    alpha=0.15, color="gray", label="±2% tolerance band")

    ax.set_xlabel("Nominal Coverage (1 - α)", fontsize=13)
    ax.set_ylabel("Empirical Coverage Rate", fontsize=13)
    ax.set_title("Conformal Prediction Coverage Calibration\n(CARE Uncertainty Quantification Module)", fontsize=12)
    ax.legend(fontsize=11)
    ax.set_xlim(0.65, 1.0)
    ax.set_ylim(0.60, 1.05)
    ax.grid(True, alpha=0.3)
    ax.annotate(
        f"Max deviation: {max(abs(e - n) for e, n in zip(empirical, nominal)):.3f}",
        xy=(0.05, 0.92), xycoords="axes fraction", fontsize=10,
        bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.7)
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_precision_recall_comparison(all_probs, all_labels, names, output_path):
    """Plot precision-recall curves for all methods."""
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    for (name, probs), color in zip(zip(names, all_probs), colors):
        labels_arr = np.array(all_labels)
        probs_arr = np.array(probs)
        prec, rec, thresholds = precision_recall_curve(labels_arr, probs_arr)
        # F1 at optimal threshold
        f1s = 2 * prec * rec / (prec + rec + 1e-9)
        best_idx = np.argmax(f1s)
        best_f1 = f1s[best_idx]

        # Area under PR curve
        from sklearn.metrics import auc as sk_auc
        try:
            auc_pr = sk_auc(rec, prec)
        except Exception:
            auc_pr = np.sum(np.diff(rec) * prec[:-1])

        ax.plot(rec, prec, color=color, lw=2,
                label=f"{name} (AUC={abs(auc_pr):.3f}, F1={best_f1:.3f})")
        ax.scatter([rec[best_idx]], [prec[best_idx]], color=color, s=80, zorder=5)

    # Random baseline
    pos_rate = np.mean(all_labels)
    ax.axhline(y=pos_rate, color="gray", linestyle="--", lw=1, label=f"Random (P={pos_rate:.2f})")

    ax.set_xlabel("Recall", fontsize=13)
    ax.set_ylabel("Precision", fontsize=13)
    ax.set_title("Precision-Recall Curves: CARE vs. Baselines", fontsize=13)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_roc_comparison(all_probs, all_labels, names, output_path):
    """Plot ROC curves for all methods."""
    fig, ax = plt.subplots(figsize=(7, 6))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    for (name, probs), color in zip(zip(names, all_probs), colors):
        labels_arr = np.array(all_labels)
        fpr, tpr, _ = roc_curve(labels_arr, probs)
        from sklearn.metrics import auc
        auroc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{name} (AUC={auroc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random (AUC=0.500)")
    ax.set_xlabel("False Positive Rate", fontsize=13)
    ax.set_ylabel("True Positive Rate", fontsize=13)
    ax.set_title("ROC Curves: CARE vs. Baselines", fontsize=13)
    ax.legend(loc="lower right", fontsize=9)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_metrics_comparison(all_metrics, output_path):
    """Bar chart comparing F1, Precision, Recall, AUROC across methods."""
    names = [m["name"] for m in all_metrics]
    metrics_keys = ["precision", "recall", "f1", "auroc"]
    metric_labels = ["Precision", "Recall", "F1 Score", "AUROC"]

    x = np.arange(len(names))
    width = 0.2
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (key, label, color) in enumerate(zip(metrics_keys, metric_labels, colors)):
        values = [m.get(key, 0) for m in all_metrics]
        bars = ax.bar(x + i * width, values, width, label=label, color=color, alpha=0.85)
        # Add value labels
        for bar, val in zip(bars, values):
            if not np.isnan(val):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                        f"{val:.3f}", ha="center", va="bottom", fontsize=7.5, rotation=45)

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("Score", fontsize=13)
    ax.set_title("Performance Comparison: CARE vs. Baselines", fontsize=13)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=10)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_ambiguity_distribution(decisions_dict, output_path):
    """
    Bar chart showing distribution of safe/ambiguous/unsafe decisions
    for different alpha values.
    """
    alphas = sorted(decisions_dict.keys())
    safe_rates = []
    ambig_rates = []
    unsafe_rates = []

    for alpha in alphas:
        decisions = decisions_dict[alpha]
        n = len(decisions)
        safe_rates.append(sum(1 for d in decisions if d == "safe") / n)
        ambig_rates.append(sum(1 for d in decisions if d == "ambiguous") / n)
        unsafe_rates.append(sum(1 for d in decisions if d == "unsafe") / n)

    x = np.arange(len(alphas))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x - width, safe_rates, width, label="Safe", color="#4CAF50", alpha=0.85)
    b2 = ax.bar(x, ambig_rates, width, label="Ambiguous", color="#FFC107", alpha=0.85)
    b3 = ax.bar(x + width, unsafe_rates, width, label="Unsafe", color="#F44336", alpha=0.85)

    ax.set_xlabel("Alpha (α)", fontsize=13)
    ax.set_ylabel("Fraction of Predictions", fontsize=13)
    ax.set_title("Tripartite Decision Distribution by Confidence Level (α)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f"α={a}" for a in alphas], fontsize=10)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_domain_adaptation_results(domain_results, output_path):
    """
    Bar chart showing F1 improvement with DAPL for each domain.
    """
    domains = list(domain_results.keys())
    f1_base = [domain_results[d]["f1_base"] for d in domains]
    f1_dapl = [domain_results[d]["f1_dapl"] for d in domains]
    regulations = [domain_results[d].get("regulation", d) for d in domains]

    x = np.arange(len(domains))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    b1 = ax.bar(x - width/2, f1_base, width, label="CARE (No DAPL)", color="#2196F3", alpha=0.85)
    b2 = ax.bar(x + width/2, f1_dapl, width, label="CARE (With DAPL)", color="#4CAF50", alpha=0.85)

    for bar, val in zip(b1, f1_base):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    for bar, val in zip(b2, f1_dapl):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    # Annotate delta
    for i, d in enumerate(domains):
        delta = domain_results[d]["f1_delta"]
        y_pos = max(f1_base[i], f1_dapl[i]) + 0.04
        ax.annotate(f"Δ={delta:+.3f}", xy=(x[i], y_pos), ha="center",
                    fontsize=10, color="darkgreen" if delta > 0 else "red",
                    fontweight="bold")

    ax.set_xlabel("Domain", fontsize=13)
    ax.set_ylabel("F1 Score", fontsize=13)
    ax.set_title("Domain Adaptation (DAPL): F1 Score Comparison", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{d.title()}\n({reg})" for d, reg in zip(domains, regulations)],
        fontsize=11
    )
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_ece_comparison(ece_results, output_path):
    """Bar chart comparing ECE across methods (lower is better)."""
    names = list(ece_results.keys())
    eces = [ece_results[n] for n in names]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#4CAF50" if "CARE" in n else "#2196F3" for n in names]
    bars = ax.bar(names, eces, color=colors, alpha=0.85)

    for bar, val in zip(bars, eces):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                f"{val:.4f}", ha="center", va="bottom", fontsize=10)

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("Expected Calibration Error (ECE)", fontsize=13)
    ax.set_title("Calibration Quality: ECE Comparison (Lower is Better)", fontsize=12)
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=10)
    ax.set_ylim(0, max(eces) * 1.3)
    ax.grid(True, axis="y", alpha=0.3)

    # Highlight CARE bars
    care_patch = mpatches.Patch(color="#4CAF50", alpha=0.85, label="CARE variants")
    base_patch = mpatches.Patch(color="#2196F3", alpha=0.85, label="Baselines")
    ax.legend(handles=[care_patch, base_patch], fontsize=11)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_explanation_faithfulness(faithfulness_per_category, output_path):
    """
    Bar chart of explanation faithfulness scores per risk category.
    """
    categories = list(faithfulness_per_category.keys())
    scores = [faithfulness_per_category[c] for c in categories]
    cat_labels = [c.replace("_", "\n").title() for c in categories]

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(categories)))
    bars = ax.bar(cat_labels, scores, color=colors, alpha=0.9)

    for bar, val in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=11)

    ax.axhline(y=0.87, color="red", linestyle="--", lw=1.5,
               label="Target threshold (0.87)")
    ax.set_xlabel("Risk Category", fontsize=13)
    ax.set_ylabel("Faithfulness Score", fontsize=13)
    ax.set_title("Explanation Faithfulness by Risk Category\n(EGM Evaluation)", fontsize=12)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def plot_ablation_study(ablation_results, output_path):
    """
    Bar chart of CARE ablation: full CARE vs. CARE-NoUQ vs. CARE-NoExp vs. baselines.
    """
    names = [r["name"] for r in ablation_results]
    f1_vals = [r["f1"] for r in ablation_results]
    auroc_vals = [r["auroc"] for r in ablation_results]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 5))
    b1 = ax.bar(x - width/2, f1_vals, width, label="F1 Score", color="#4CAF50", alpha=0.85)
    b2 = ax.bar(x + width/2, auroc_vals, width, label="AUROC", color="#2196F3", alpha=0.85)

    for bar, val in zip(b1, f1_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=8.5)
    for bar, val in zip(b2, auroc_vals):
        if not np.isnan(val):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=8.5)

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("Score", fontsize=13)
    ax.set_title("Ablation Study: CARE Components", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=20, ha="right", fontsize=9)
    ax.legend(fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")
