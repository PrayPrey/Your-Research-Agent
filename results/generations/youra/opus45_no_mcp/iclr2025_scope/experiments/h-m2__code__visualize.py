"""Visualization for H-M2: Sharpness comparison figures"""

import os
import matplotlib.pyplot as plt
import numpy as np

from config import GATE_THRESHOLD


def plot_gate_comparison(seq_sharpness: float, ret_sharpness: float, threshold: float, out_path: str):
    """Bar chart: GSM8K vs NQ sharpness with threshold line."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))

    tasks = ["GSM8K\n(Sequential)", "NQ\n(Retrieval)"]
    values = [seq_sharpness, ret_sharpness]
    colors = ["#4CAF50", "#F44336"]

    bars = ax.bar(tasks, values, color=colors, width=0.6, edgecolor="black", linewidth=1.5)

    threshold_line = ret_sharpness * threshold
    ax.axhline(y=threshold_line, color="orange", linestyle="--", linewidth=2, label=f"Threshold ({threshold}x retrieval)")

    ratio = seq_sharpness / (ret_sharpness + 1e-12)
    gate_status = "PASS" if ratio < threshold else "FAIL"
    gate_color = "green" if ratio < threshold else "red"

    ax.set_ylabel("SAM Sharpness", fontsize=12)
    ax.set_title(f"H-M2: Task-Specific Sharpness Comparison\n"
                 f"Ratio: {ratio:.3f} (threshold: <{threshold}) - {gate_status}", fontsize=14)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.legend(loc="upper right")
    ax.set_ylim(0, max(values) * 1.2)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")


def plot_sharpness_distribution(seq_per_batch: list, ret_per_batch: list, out_path: str):
    """Histogram of per-batch sharpness for both tasks."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    all_vals = seq_per_batch + ret_per_batch
    min_val, max_val = min(all_vals), max(all_vals)
    bins = np.linspace(min_val - 0.01, max_val + 0.01, 30)

    ax.hist(seq_per_batch, bins=bins, alpha=0.6, label=f"GSM8K (mean={np.mean(seq_per_batch):.4f})",
            color="#4CAF50", edgecolor="black")
    ax.hist(ret_per_batch, bins=bins, alpha=0.6, label=f"NQ (mean={np.mean(ret_per_batch):.4f})",
            color="#F44336", edgecolor="black")

    ax.axvline(np.mean(seq_per_batch), color="#2E7D32", linestyle="--", linewidth=2)
    ax.axvline(np.mean(ret_per_batch), color="#C62828", linestyle="--", linewidth=2)

    ax.set_xlabel("SAM Sharpness", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("H-M2: Per-Batch Sharpness Distribution", fontsize=14)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_path}")
