import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve


def plot_auroc_comparison(results: dict, out_path: str) -> None:
    """Bar chart: VC vs TE vs SE AUROC with 95% CI error bars."""
    methods = ["VC\n(Llama-2-7B-Chat)", "TE\n(Token Entropy)", "SE\n(Semantic Entropy)"]
    aurocs = [results["auroc_vc"], results["auroc_te"], results["auroc_se"]]

    ci = results.get("auroc_vc_ci", [aurocs[0], aurocs[0]])
    yerr_vc = [[aurocs[0] - ci[0]], [ci[1] - aurocs[0]]]
    yerr_te = [[0], [0]]
    yerr_se = [[0], [0]]
    yerrs = [yerr_vc, yerr_te, yerr_se]

    colors = ["#e74c3c", "#3498db", "#2ecc71"]
    fig, ax = plt.subplots(figsize=(7, 5))

    for i, (method, auroc, yerr, color) in enumerate(zip(methods, aurocs, yerrs, colors)):
        ax.bar(i, auroc, color=color, alpha=0.8,
               yerr=[[yerr[0][0]], [yerr[1][0]]] if i == 0 else None,
               capsize=5, label=method)
        ax.text(i, auroc + 0.01, f"{auroc:.3f}", ha="center", va="bottom", fontsize=10)

    gate_passed = results.get("gate_passed", False)
    gate_str = "PASS" if gate_passed else "FAIL"
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods)
    ax.set_ylabel("AUROC")
    ax.set_ylim(0, 0.7)
    ax.set_title(f"AUROC Comparison: VC vs TE vs SE\nGate: {gate_str} (VC < TE AND VC < SE)")
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Random (0.5)")
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_confidence_histogram(vc_confidences: list, out_path: str) -> None:
    """Histogram of raw 0-100% confidence scores."""
    conf_pct = [c * 100.0 for c in vc_confidences]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(conf_pct, bins=20, color="#e74c3c", alpha=0.7, edgecolor="black")
    ax.axvline(x=50, color="blue", linestyle="--", label="50%")
    ax.axvline(x=np.mean(conf_pct), color="orange", linestyle="-", label=f"Mean={np.mean(conf_pct):.1f}%")
    ax.set_xlabel("Verbalized Confidence (%)")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of VC Confidence Scores\n(Llama-2-7B-Chat on TriviaQA dev)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_roc_curves(
    vc_uncertainties: list,
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    out_path: str,
) -> None:
    """ROC curves for VC, TE, SE overlaid."""
    qids = list(em_labels.keys())
    labels = [em_labels[q] for q in qids]

    fig, ax = plt.subplots(figsize=(6, 6))

    # VC ROC
    fpr, tpr, _ = roc_curve(labels, vc_uncertainties)
    ax.plot(fpr, tpr, color="#e74c3c", lw=2, label="VC")

    # TE ROC (if available)
    if te_scores:
        te_vals = [te_scores.get(q, 0.5) for q in qids]
        fpr_te, tpr_te, _ = roc_curve(labels, te_vals)
        ax.plot(fpr_te, tpr_te, color="#3498db", lw=2, label="TE")

    # SE ROC (if available)
    if se_scores:
        se_vals = [se_scores.get(q, 0.5) for q in qids]
        fpr_se, tpr_se, _ = roc_curve(labels, se_vals)
        ax.plot(fpr_se, tpr_se, color="#2ecc71", lw=2, label="SE")

    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: VC vs TE vs SE")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_reliability_diagram(vc_confidences: list, em_labels: dict, out_path: str) -> None:
    """ECE reliability diagram: mean confidence vs accuracy per bin."""
    confs = np.array(vc_confidences)
    labels = np.array(list(em_labels.values()), dtype=float)

    n_bins = 10
    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    bin_conf, bin_acc, bin_count = [], [], []

    for i in range(n_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        mask = (confs >= lo) & (confs <= hi) if i == n_bins - 1 else (confs >= lo) & (confs < hi)
        if mask.sum() == 0:
            continue
        bin_conf.append(confs[mask].mean())
        bin_acc.append(labels[mask].mean())
        bin_count.append(mask.sum())

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Perfect calibration")
    ax.bar(bin_conf, bin_acc, width=0.08, alpha=0.6, color="#e74c3c", label="VC accuracy")
    ax.set_xlabel("Mean Predicted Confidence")
    ax.set_ylabel("Fraction Correct")
    ax.set_title("Reliability Diagram (ECE Calibration)\nVC Confidence vs Actual Accuracy")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def plot_scatter_vc_em(vc_confidences: list, em_labels: dict, out_path: str) -> None:
    """Scatter: VC confidence vs EM correctness for 98 questions."""
    qids = list(em_labels.keys())
    labels = [em_labels[q] for q in qids]
    confs = vc_confidences

    correct = [c for c, l in zip(confs, labels) if l == 1]
    wrong = [c for c, l in zip(confs, labels) if l == 0]

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(range(len(correct)), correct, alpha=0.6, color="#2ecc71", s=20, label="Correct (EM=1)")
    ax.scatter(range(len(wrong)), wrong, alpha=0.6, color="#e74c3c", s=20, label="Wrong (EM=0)")
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("Question Index")
    ax.set_ylabel("VC Confidence")
    ax.set_ylim(0, 1.05)
    ax.set_title("VC Confidence vs EM Correctness (98 Questions)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    vc_uncertainties: list,
    vc_confidences: list,
    se_scores: dict,
    te_scores: dict,
    em_labels: dict,
    results: dict,
    figures_dir: str,
) -> None:
    os.makedirs(figures_dir, exist_ok=True)
    plot_auroc_comparison(results, os.path.join(figures_dir, "auroc_comparison.png"))
    plot_confidence_histogram(vc_confidences, os.path.join(figures_dir, "confidence_histogram.png"))
    plot_roc_curves(vc_uncertainties, se_scores, te_scores, em_labels, os.path.join(figures_dir, "roc_curves.png"))
    plot_reliability_diagram(vc_confidences, em_labels, os.path.join(figures_dir, "ece_calibration.png"))
    plot_scatter_vc_em(vc_confidences, em_labels, os.path.join(figures_dir, "failure_scatter.png"))
    print(f"All 5 figures saved to {figures_dir}/")
