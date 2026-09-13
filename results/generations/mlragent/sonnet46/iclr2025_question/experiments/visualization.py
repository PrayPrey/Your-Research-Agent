"""Visualization utilities for HalluConform experiment."""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.metrics import roc_curve, precision_recall_curve

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def plot_nonconformity_distribution(cal_results, hc_model, save_path):
    """Plot distribution of nonconformity scores for correct vs hallucinated samples."""
    X = np.array([
        [r["token_entropy"], r["attention_consistency"], r["hidden_divergence"]]
        for r in cal_results
    ])
    X_scaled = hc_model.scaler.transform(X)
    scores = hc_model.lr.predict_proba(X_scaled)[:, 1]
    y_true = np.array([1 - r["correct"] for r in cal_results])

    correct_scores = scores[y_true == 0]
    hal_scores = scores[y_true == 1]

    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.linspace(0, 1, 30)
    ax.hist(correct_scores, bins=bins, alpha=0.7, label="Correct (factual)", color="#2196F3", density=True)
    ax.hist(hal_scores, bins=bins, alpha=0.7, label="Hallucinated", color="#F44336", density=True)
    ax.axvline(hc_model.threshold_, color="black", linestyle="--", linewidth=2,
               label=f"Threshold (α={hc_model.alpha:.2f})")
    ax.set_xlabel("Nonconformity Score", fontsize=13)
    ax.set_ylabel("Density", fontsize=13)
    ax.set_title("Nonconformity Score Distribution\n(Calibration Set)", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_roc_curves(method_results, test_results, save_path):
    """Plot ROC curves for all methods."""
    y_true = np.array([1 - r["correct"] for r in test_results])

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = ["#1976D2", "#388E3C", "#F57C00", "#7B1FA2", "#C62828"]

    for (name, preds), color in zip(method_results.items(), colors):
        scores = np.array([p["nonconformity_score"] for p in preds])
        if len(np.unique(y_true)) > 1:
            fpr_arr, tpr_arr, _ = roc_curve(y_true, scores)
            from sklearn.metrics import auc
            auroc = auc(fpr_arr, tpr_arr)
            ax.plot(fpr_arr, tpr_arr, label=f"{name} (AUC={auroc:.3f})", color=color, linewidth=2)
        else:
            ax.plot([0, 1], [0, 1], label=f"{name}", color=color, linewidth=2)

    ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Random")
    ax.set_xlabel("False Positive Rate", fontsize=13)
    ax.set_ylabel("True Positive Rate", fontsize=13)
    ax.set_title("ROC Curves: Hallucination Detection", fontsize=14)
    ax.legend(fontsize=10, loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_pr_curves(method_results, test_results, save_path):
    """Plot Precision-Recall curves for all methods."""
    y_true = np.array([1 - r["correct"] for r in test_results])

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = ["#1976D2", "#388E3C", "#F57C00", "#7B1FA2", "#C62828"]

    for (name, preds), color in zip(method_results.items(), colors):
        scores = np.array([p["nonconformity_score"] for p in preds])
        if len(np.unique(y_true)) > 1:
            prec_arr, rec_arr, _ = precision_recall_curve(y_true, scores)
            from sklearn.metrics import auc
            auprc = auc(rec_arr, prec_arr)
            ax.plot(rec_arr, prec_arr, label=f"{name} (AP={auprc:.3f})", color=color, linewidth=2)
        else:
            baseline_rate = float(y_true.mean())
            ax.axhline(baseline_rate, label=f"{name} (baseline)", color=color, linestyle="--")

    baseline_rate = float(y_true.mean())
    ax.axhline(baseline_rate, color="gray", linestyle="--", linewidth=1, label=f"Baseline ({baseline_rate:.2f})")
    ax.set_xlabel("Recall", fontsize=13)
    ax.set_ylabel("Precision", fontsize=13)
    ax.set_title("Precision-Recall Curves: Hallucination Detection", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_method_comparison(all_metrics, save_path):
    """Bar chart comparing methods on AUROC, AUPRC, F1."""
    methods = list(all_metrics.keys())
    metric_names = ["auroc", "auprc", "f1"]
    metric_labels = ["AUROC", "AUPRC", "F1 Score"]
    colors = ["#2196F3", "#4CAF50", "#FF9800"]

    x = np.arange(len(methods))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, (metric, label, color) in enumerate(zip(metric_names, metric_labels, colors)):
        values = [all_metrics[m].get(metric, 0) for m in methods]
        bars = ax.bar(x + i * width, values, width, label=label, color=color, alpha=0.85)
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("Score", fontsize=13)
    ax.set_title("Hallucination Detection Performance Comparison", fontsize=14)
    ax.set_xticks(x + width)
    ax.set_xticklabels(methods, rotation=15, ha="right", fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_coverage_verification(coverage_data, save_path):
    """Plot empirical vs theoretical coverage for different alpha values."""
    alphas = [d["alpha"] for d in coverage_data]
    theoretical = [d["theoretical_coverage"] for d in coverage_data]
    empirical = [d["empirical_coverage"] for d in coverage_data]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(theoretical, theoretical, "k--", linewidth=1.5, label="Perfect calibration")
    ax.scatter(theoretical, empirical, s=100, color="#1976D2", zorder=5, label="HalluConform")
    ax.plot(theoretical, empirical, color="#1976D2", linewidth=1.5, alpha=0.7)

    # Annotate alpha values
    for i, (t, e, a) in enumerate(zip(theoretical, empirical, alphas)):
        ax.annotate(f"α={a:.2f}", (t, e), textcoords="offset points", xytext=(5, 5), fontsize=9)

    ax.set_xlabel("Theoretical Coverage (1 - α)", fontsize=13)
    ax.set_ylabel("Empirical Coverage", fontsize=13)
    ax.set_title("Coverage Verification: Conformal Prediction Guarantee", fontsize=14)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.7, 1.02)
    ax.set_ylim(0.7, 1.02)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_domain_performance(domain_metrics_by_method, save_path):
    """Plot per-domain performance for each method."""
    methods = list(domain_metrics_by_method.keys())
    # Gather all domains
    domains = sorted(set(
        d for m_dm in domain_metrics_by_method.values() for d in m_dm.keys()
    ))

    x = np.arange(len(domains))
    width = 0.8 / len(methods)
    colors = ["#1976D2", "#388E3C", "#F57C00", "#7B1FA2"]

    fig, ax = plt.subplots(figsize=(9, 6))
    for i, (method, color) in enumerate(zip(methods, colors)):
        dm = domain_metrics_by_method[method]
        values = [dm.get(d, {}).get("auroc", 0) for d in domains]
        offset = (i - len(methods) / 2 + 0.5) * width
        bars = ax.bar(x + offset, values, width * 0.9, label=method, color=color, alpha=0.85)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                    f"{val:.2f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Domain", fontsize=13)
    ax.set_ylabel("AUROC", fontsize=13)
    ax.set_title("Per-Domain Hallucination Detection AUROC", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([d.capitalize() for d in domains], fontsize=12)
    ax.set_ylim(0, 1.1)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_signal_importance(weights, save_path):
    """Plot learned signal weights."""
    signals = list(weights.keys())
    values = list(weights.values())
    colors = ["#2196F3" if v >= 0 else "#F44336" for v in values]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(signals, values, color=colors, alpha=0.85)
    for bar, val in zip(bars, values):
        ax.text(val + 0.001 * np.sign(val), bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", ha="left" if val >= 0 else "right", fontsize=10)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Logistic Regression Coefficient", fontsize=13)
    ax.set_title("HalluConform: Learned Signal Importance", fontsize=14)
    ax.grid(True, alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_fpr_fnr_comparison(all_metrics, save_path):
    """Plot FPR and FNR comparison across methods."""
    methods = list(all_metrics.keys())
    fpr_vals = [all_metrics[m]["fpr"] for m in methods]
    fnr_vals = [all_metrics[m]["fnr"] for m in methods]

    x = np.arange(len(methods))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, fpr_vals, width, label="FPR (False Positive Rate)",
                   color="#FF9800", alpha=0.85)
    bars2 = ax.bar(x + width / 2, fnr_vals, width, label="FNR (False Negative Rate)",
                   color="#F44336", alpha=0.85)

    for bar, val in zip(bars1, fpr_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=8)
    for bar, val in zip(bars2, fnr_vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Method", fontsize=13)
    ax.set_ylabel("Rate", fontsize=13)
    ax.set_title("False Positive Rate and False Negative Rate Comparison", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(methods, rotation=15, ha="right", fontsize=10)
    ax.set_ylim(0, 1.0)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")


def plot_adaptive_threshold(test_results, hc_model, save_path):
    """Plot nonconformity scores by domain and risk level with adaptive thresholds."""
    from config import ALPHA_RISK
    domains = list(set(r["domain"] for r in test_results))
    risk_levels = list(set(r["risk_level"] for r in test_results))
    domain_colors = {"factual": "#2196F3", "medical": "#F44336", "legal": "#4CAF50"}

    X = np.array([
        [r["token_entropy"], r["attention_consistency"], r["hidden_divergence"]]
        for r in test_results
    ])
    X_scaled = hc_model.scaler.transform(X)
    scores = hc_model.lr.predict_proba(X_scaled)[:, 1]

    fig, ax = plt.subplots(figsize=(10, 6))

    for domain in domains:
        mask = [r["domain"] == domain for r in test_results]
        dom_scores = scores[np.array(mask)]
        ax.scatter(range(len(dom_scores)), dom_scores, alpha=0.5,
                   color=domain_colors.get(domain, "gray"), label=f"{domain} domain", s=20)

    # Draw thresholds for each risk level
    risk_colors = {"low": "blue", "medium": "orange", "high": "red"}
    for rl in set(r["risk_level"] for r in test_results):
        t = hc_model.get_threshold(rl)
        alpha_eff = ALPHA_RISK.get(rl, hc_model.alpha)
        ax.axhline(t, color=risk_colors.get(rl, "black"), linestyle="--", linewidth=1.5,
                   label=f"Threshold ({rl} risk, α={alpha_eff:.2f})")

    ax.set_xlabel("Sample Index", fontsize=13)
    ax.set_ylabel("Nonconformity Score", fontsize=13)
    ax.set_title("Adaptive Thresholds by Domain Risk Level", fontsize=14)
    ax.legend(fontsize=9, loc="upper right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {save_path}")
