import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve


def evaluate_ssi_discrimination(ssi_clean: list[float], ssi_contaminated: list[float]) -> dict:
    labels = [0] * len(ssi_clean) + [1] * len(ssi_contaminated)
    scores = ssi_clean + ssi_contaminated

    auc = roc_auc_score(labels, scores)

    mean_clean = np.mean(ssi_clean)
    mean_cont = np.mean(ssi_contaminated)
    pooled_std = np.sqrt((np.var(ssi_clean) + np.var(ssi_contaminated)) / 2)
    cohens_d = (mean_cont - mean_clean) / (pooled_std + 1e-8)

    return {
        "auc": float(auc),
        "cohens_d": float(cohens_d),
        "mean_ssi_clean": float(mean_clean),
        "mean_ssi_contaminated": float(mean_cont),
    }


def plot_gate_metrics(achieved_auc: float, target: float, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(["Target AUC", "Achieved AUC"], [target, achieved_auc],
                  color=["gray", "green" if achieved_auc >= target else "red"])
    ax.axhline(y=target, color="black", linestyle="--", label=f"Target: {target}")
    ax.set_ylabel("AUC")
    ax.set_title("Gate Metrics: AUC Target vs Achieved")
    ax.set_ylim(0, 1.0)
    for bar, val in zip(bars, [target, achieved_auc]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f"{val:.3f}",
                ha="center", va="bottom", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "gate_metrics.png"), dpi=150)
    plt.close()


def plot_ssi_distribution(ssi_clean, ssi_low, ssi_high, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    data = [ssi_clean, ssi_low, ssi_high]
    labels = ["Clean (0%)", "Low (10%)", "High (50%)"]
    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    colors = ["lightblue", "lightyellow", "lightcoral"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_ylabel("SSI Score")
    ax.set_title("SSI Distribution by Contamination Level")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "ssi_distribution.png"), dpi=150)
    plt.close()


def plot_roc_curve(ssi_clean, ssi_contaminated, auc_score, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)
    labels = [0] * len(ssi_clean) + [1] * len(ssi_contaminated)
    scores = ssi_clean + ssi_contaminated
    fpr, tpr, _ = roc_curve(labels, scores)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(fpr, tpr, color="blue", lw=2, label=f"ROC (AUC = {auc_score:.3f})")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve: SSI-based Contamination Detection")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "roc_curve.png"), dpi=150)
    plt.close()


def plot_contamination_level_analysis(levels: list[float], mean_ssi: list[float], figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([l * 100 for l in levels], mean_ssi, marker="o", linewidth=2, markersize=10, color="blue")
    ax.set_xlabel("Contamination Level (%)")
    ax.set_ylabel("Mean SSI")
    ax.set_title("Mean SSI vs Contamination Level")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "contamination_level.png"), dpi=150)
    plt.close()


def plot_confidence_variance_histogram(all_confidences: list[list[float]], figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)
    variances = [np.var(conf) for conf in all_confidences]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(variances, bins=50, edgecolor="black", alpha=0.7)
    ax.set_xlabel("Confidence Variance")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Confidence Variance Across Items")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "variance_hist.png"), dpi=150)
    plt.close()


def run_evaluation(results_file: str, figures_dir: str) -> dict:
    with open(results_file, "r") as f:
        data = json.load(f)

    ssi_clean = data["ssi_scores"]["clean"]
    ssi_low = data["ssi_scores"]["low"]
    ssi_high = data["ssi_scores"]["high"]

    ssi_contaminated = ssi_low + ssi_high

    metrics = evaluate_ssi_discrimination(ssi_clean, ssi_contaminated)

    plot_gate_metrics(metrics["auc"], 0.7, figures_dir)
    plot_ssi_distribution(ssi_clean, ssi_low, ssi_high, figures_dir)
    plot_roc_curve(ssi_clean, ssi_contaminated, metrics["auc"], figures_dir)

    levels = [0.0, 0.10, 0.50]
    mean_ssi = [np.mean(ssi_clean), np.mean(ssi_low), np.mean(ssi_high)]
    plot_contamination_level_analysis(levels, mean_ssi, figures_dir)

    all_confidences = data.get("all_confidences", {})
    if all_confidences:
        combined = all_confidences.get("clean", []) + all_confidences.get("low", []) + all_confidences.get("high", [])
        if combined:
            plot_confidence_variance_histogram(combined, figures_dir)

    metrics["per_level_mean_ssi"] = {
        "clean": float(np.mean(ssi_clean)),
        "low": float(np.mean(ssi_low)),
        "high": float(np.mean(ssi_high)),
    }

    gate_pass = metrics["auc"] >= 0.7 and metrics["cohens_d"] >= 0.5

    return {
        "metrics": metrics,
        "gate_pass": gate_pass,
    }
