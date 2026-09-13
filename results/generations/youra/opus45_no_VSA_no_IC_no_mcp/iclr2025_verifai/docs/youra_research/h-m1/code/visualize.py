"""Visualization functions for reconstruction test results."""
import os
from typing import Dict, Any

import matplotlib.pyplot as plt


def plot_gate_comparison(metrics: Dict[str, Any], acc_thresh: float, pass_thresh: float, out_path: str = None) -> None:
    """Bar chart comparing actual metrics vs thresholds."""
    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["Mean Accuracy", "Pass Rate"]
    actual = [metrics["mean_accuracy"], metrics["pass_rate"]]
    thresholds = [acc_thresh, pass_thresh]

    x = range(len(labels))
    width = 0.35

    bars1 = ax.bar([i - width/2 for i in x], actual, width, label="Actual", color="steelblue")
    bars2 = ax.bar([i + width/2 for i in x], thresholds, width, label="Threshold", color="coral")

    ax.set_ylabel("Rate")
    ax.set_title("Reconstruction Test: Gate Check")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)
    ax.legend()
    ax.axhline(y=0.95, color="gray", linestyle="--", alpha=0.5)

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    plt.tight_layout()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=150)
    plt.close()


def plot_per_field_accuracy(metrics: Dict[str, Any], out_path: str = None) -> None:
    """Bar chart of per-field accuracy."""
    per_field = metrics["per_field"]

    fig, ax = plt.subplots(figsize=(10, 5))

    fields = list(per_field.keys())
    accuracies = [per_field[f] for f in fields]

    bars = ax.bar(fields, accuracies, color="steelblue")

    ax.set_ylabel("Accuracy")
    ax.set_xlabel("Field")
    ax.set_title("Per-Field Reconstruction Accuracy")
    ax.set_ylim(0, 1.1)
    ax.axhline(y=0.95, color="coral", linestyle="--", label="95% threshold")
    ax.legend()

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    plt.tight_layout()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=150)
    plt.close()


def plot_accuracy_by_error_type(breakdown: Dict[str, Dict[str, float]], out_path: str = None) -> None:
    """Bar chart of mean accuracy per error type."""
    fig, ax = plt.subplots(figsize=(12, 5))

    error_types = list(breakdown.keys())
    mean_accs = [breakdown[et]["mean_accuracy"] for et in error_types]

    bars = ax.bar(error_types, mean_accs, color="steelblue")

    ax.set_ylabel("Mean Accuracy")
    ax.set_xlabel("Error Type")
    ax.set_title("Reconstruction Accuracy by Error Type")
    ax.set_ylim(0, 1.1)
    ax.axhline(y=0.95, color="coral", linestyle="--", label="95% threshold")
    ax.legend()

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        plt.savefig(out_path, dpi=150)
    plt.close()
