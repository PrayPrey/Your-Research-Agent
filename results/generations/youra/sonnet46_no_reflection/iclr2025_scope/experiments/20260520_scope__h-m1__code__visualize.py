"""
H-M1 Visualization: 5 required figures for JointLoRA-KV experiment results.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from config import ExperimentConfig


def _save(fig, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(str(path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def plot_gate_metrics_comparison(
    joint: Dict, b1: Dict, b2: Dict, output_dir: Path
) -> str:
    """FR-8.1 (MANDATORY): Bar chart — JointLoRA-KV vs B1 vs B2 mean GLUE accuracy ± std."""
    labels = ["JointLoRA-KV", "B1 (Frozen Locret)", "B2 (kvpress)"]
    means = [
        joint.get("mean_glue_acc", 0.0),
        b1.get("mean_glue_acc", 0.0),
        b2.get("mean_glue_acc", 0.0),
    ]
    stds = [
        joint.get("mean_glue_std", 0.0),
        b1.get("mean_glue_std", 0.0),
        b2.get("mean_glue_std", 0.0),
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#2196F3", "#F44336", "#FF9800"]
    bars = ax.bar(labels, means, yerr=stds, capsize=5, color=colors, alpha=0.8, edgecolor="black")
    ax.set_ylabel("Mean GLUE Accuracy (%) at 50% KV Budget")
    ax.set_title("H-M1: JointLoRA-KV vs Baselines (GLUE @ budget=0.5)")
    ax.set_ylim(max(0, min(means) - 5), min(100, max(means) + 8))
    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{mean:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.axhline(y=means[1] + 2.0, color="red", linestyle="--", alpha=0.5, label="Gate threshold (+2pp over B1)")
    ax.legend()
    return _save(fig, output_dir / "gate_metrics_comparison.png")


def plot_training_curves(training_history: List[Dict], output_dir: Path) -> str:
    """FR-8.2: Loss per epoch for all 3 seeds (JointLoRA-KV)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#1976D2", "#388E3C", "#7B1FA2"]
    seeds = [42, 123, 456]
    for i, (history, seed, color) in enumerate(zip(training_history, seeds, colors)):
        losses = [h["loss"] for h in history]
        epochs = list(range(1, len(losses) + 1))
        ax.plot(epochs, losses, marker="o", color=color, label=f"Seed {seed}", linewidth=2)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Training Loss")
    ax.set_title("H-M1: JointLoRA-KV Training Loss (3 Seeds, MNLI)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return _save(fig, output_dir / "training_curves.png")


def plot_per_task_glue(
    joint: Dict, b1: Dict, b2: Dict, output_dir: Path
) -> str:
    """FR-8.3: Per-task bars for MNLI/SST-2/QNLI separately."""
    tasks = ["mnli", "sst2", "qnli"]
    task_labels = ["MNLI", "SST-2", "QNLI"]
    x = np.arange(len(tasks))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    joint_means = [joint.get(f"{t}_mean", 0.0) for t in tasks]
    b1_means = [b1.get(f"{t}_mean", 0.0) for t in tasks]
    b2_means = [b2.get(f"{t}_mean", 0.0) for t in tasks]

    ax.bar(x - width, joint_means, width, label="JointLoRA-KV", color="#2196F3", alpha=0.8)
    ax.bar(x, b1_means, width, label="B1 (Frozen Locret)", color="#F44336", alpha=0.8)
    ax.bar(x + width, b2_means, width, label="B2 (kvpress)", color="#FF9800", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels)
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("H-M1: Per-Task GLUE Accuracy @ 50% KV Budget")
    ax.legend()
    return _save(fig, output_dir / "per_task_glue.png")


def plot_budget_sensitivity(
    joint_sensitivity: Dict, b1_sensitivity: Dict, output_dir: Path
) -> str:
    """FR-8.4: Accuracy vs budget_ratio (0.3/0.5/0.7) line chart."""
    ratios = sorted(joint_sensitivity.keys())
    joint_accs = [joint_sensitivity[r] for r in ratios]
    b1_accs = [b1_sensitivity.get(r, 0.0) for r in ratios]
    ratio_labels = [f"{r:.0%}" for r in ratios]

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(ratio_labels, joint_accs, marker="o", color="#2196F3", label="JointLoRA-KV", linewidth=2)
    ax.plot(ratio_labels, b1_accs, marker="s", color="#F44336", label="B1 (Frozen Locret)", linewidth=2)
    ax.set_xlabel("KV Budget Ratio")
    ax.set_ylabel("MNLI Accuracy (%)")
    ax.set_title("H-M1: Budget Sensitivity (MNLI)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    return _save(fig, output_dir / "budget_sensitivity.png")


def plot_longbench_comparison(
    joint: Dict, b1: Dict, b2: Dict, output_dir: Path
) -> str:
    """FR-8.5: NarrativeQA/Qasper/MultiFieldQA F1 bars."""
    tasks = ["narrativeqa", "qasper", "multifieldqa_en"]
    task_labels = ["NarrativeQA", "Qasper", "MultiFieldQA"]
    x = np.arange(len(tasks))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    joint_f1 = [joint.get(t, {}).get("f1", 0.0) * 100 for t in tasks]
    b1_f1 = [b1.get(t, {}).get("f1", 0.0) * 100 for t in tasks]
    b2_f1 = [b2.get(t, {}).get("f1", 0.0) * 100 for t in tasks]

    ax.bar(x - width, joint_f1, width, label="JointLoRA-KV", color="#2196F3", alpha=0.8)
    ax.bar(x, b1_f1, width, label="B1 (Frozen Locret)", color="#F44336", alpha=0.8)
    ax.bar(x + width, b2_f1, width, label="B2 (kvpress)", color="#FF9800", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels)
    ax.set_ylabel("QA F1 Score (%)")
    ax.set_title("H-M1: LongBench-QA F1 @ 50% KV Budget")
    ax.legend()
    return _save(fig, output_dir / "longbench_comparison.png")
