"""Visualization for H-E1 experiment results."""
import os
import numpy as np
import matplotlib.pyplot as plt
from config import CONFIG


def plot_extraction_rates(extraction_rates: dict, out_dir: str):
    """Bar chart of extraction rates per condition with threshold line."""
    os.makedirs(out_dir, exist_ok=True)
    conditions = list(extraction_rates.keys())
    rates = [extraction_rates[c] for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(conditions, rates, color="steelblue", edgecolor="black")
    ax.axhline(y=CONFIG.experiment.extraction_rate_threshold, color="red",
               linestyle="--", label=f"Threshold ({CONFIG.experiment.extraction_rate_threshold:.0%})")
    ax.set_ylabel("Extraction Rate")
    ax.set_xlabel("Condition")
    ax.set_title("Confidence Extraction Rate by Condition")
    ax.set_ylim(0, 1.05)
    ax.legend()

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{rate:.1%}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "extraction_rate.png"), dpi=150)
    plt.close()


def plot_reliability_diagram(results: list, condition: str, out_dir: str, n_bins: int = 15):
    """Calibration plot (accuracy vs confidence) for a condition."""
    os.makedirs(out_dir, exist_ok=True)

    if not results:
        return

    confidences = np.array([r["confidence"] for r in results])
    accuracies = np.array([r["correct"] for r in results], dtype=float)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bin_boundaries[:-1] + bin_boundaries[1:]) / 2
    bin_accs = []
    bin_confs = []
    bin_counts = []

    for i in range(n_bins):
        if i == 0:
            in_bin = (confidences >= bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        else:
            in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])

        if in_bin.sum() > 0:
            bin_accs.append(accuracies[in_bin].mean())
            bin_confs.append(confidences[in_bin].mean())
            bin_counts.append(in_bin.sum())
        else:
            bin_accs.append(np.nan)
            bin_confs.append(np.nan)
            bin_counts.append(0)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.bar(bin_centers, bin_accs, width=1/n_bins, alpha=0.7, edgecolor="black", label="Accuracy")
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Reliability Diagram: {condition}")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, f"reliability_{condition}.png"), dpi=150)
    plt.close()


def plot_ece_comparison(ece_by_condition: dict, out_dir: str):
    """Bar chart comparing ECE across conditions."""
    os.makedirs(out_dir, exist_ok=True)
    conditions = list(ece_by_condition.keys())
    ece_values = [ece_by_condition[c] if ece_by_condition[c] is not None else 0 for c in conditions]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(conditions, ece_values, color="coral", edgecolor="black")
    ax.set_ylabel("ECE")
    ax.set_xlabel("Condition")
    ax.set_title("Expected Calibration Error by Condition")
    ax.set_ylim(0, max(ece_values) * 1.2 if max(ece_values) > 0 else 0.5)

    for bar, ece in zip(bars, ece_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{ece:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "ece_comparison.png"), dpi=150)
    plt.close()


def plot_failure_breakdown(failures: dict, out_dir: str):
    """Pie chart of extraction failure types."""
    os.makedirs(out_dir, exist_ok=True)

    labels = list(failures.keys())
    sizes = list(failures.values())

    if sum(sizes) == 0:
        return

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("Extraction Failure Breakdown")

    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "failure_breakdown.png"), dpi=150)
    plt.close()
