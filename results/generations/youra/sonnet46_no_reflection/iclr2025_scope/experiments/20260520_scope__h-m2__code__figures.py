import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def plot_longbench_comparison(
    joint_results: Dict[str, float],
    b3_results: Dict[str, float],
    save_path: str = "h-m2/figures/longbench_comparison.png",
) -> None:
    _ensure_dir(save_path)
    tasks = ["narrativeqa", "qasper", "multifieldqa_en", "mean_f1"]
    labels = ["NarrativeQA", "Qasper", "MultiFieldQA", "Mean F1"]
    x = np.arange(len(tasks))
    width = 0.35

    joint_vals = [joint_results.get(t, 0.0) for t in tasks]
    b3_vals = [b3_results.get(t, 0.0) for t in tasks]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width / 2, joint_vals, width, label="JointLoRA-KV", color="#2196F3")
    bars2 = ax.bar(x + width / 2, b3_vals, width, label="B3 (Sequential)", color="#FF9800")

    ax.set_xlabel("Task")
    ax.set_ylabel("F1 Score")
    ax.set_title("LongBench-QA F1: JointLoRA-KV vs B3 at 50% KV Budget")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, 1.0)

    for bar in bars1:
        ax.annotate(f"{bar.get_height():.3f}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    for bar in bars2:
        ax.annotate(f"{bar.get_height():.3f}", xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_training_loss_curves(
    loss_histories: Dict[int, List[float]],
    save_path: str = "h-m2/figures/training_loss_curves.png",
) -> None:
    _ensure_dir(save_path)
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = {42: "#E53935", 123: "#43A047", 456: "#1E88E5"}
    for seed, losses in loss_histories.items():
        color = colors.get(seed, "#9E9E9E")
        ax.plot(losses, label=f"Seed {seed}", color=color, alpha=0.8, linewidth=1.2)

    ax.set_xlabel("Step")
    ax.set_ylabel("CE Loss")
    ax.set_title("JointLoRA-KV Training Loss Curves (3 Seeds)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_loss_distribution(
    epoch_end_losses: Dict[int, List[float]],
    save_path: str = "h-m2/figures/loss_distribution.png",
) -> None:
    _ensure_dir(save_path)
    seeds = sorted(epoch_end_losses.keys())
    data = [epoch_end_losses[s] for s in seeds]
    labels = [f"Seed {s}" for s in seeds]

    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    colors = ["#E53935", "#43A047", "#1E88E5"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel("Loss at Epoch End")
    ax.set_title("Loss Distribution per Seed at Epoch End")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_per_task_f1(
    joint_results: Dict[str, float],
    b3_results: Dict[str, float],
    save_path: str = "h-m2/figures/per_task_f1.png",
) -> None:
    _ensure_dir(save_path)
    tasks = ["narrativeqa", "qasper", "multifieldqa_en"]
    labels = ["NarrativeQA", "Qasper", "MultiFieldQA"]
    x = np.arange(len(tasks))
    width = 0.35

    joint_vals = [joint_results.get(t, 0.0) for t in tasks]
    b3_vals = [b3_results.get(t, 0.0) for t in tasks]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, joint_vals, width, label="JointLoRA-KV", color="#2196F3")
    ax.bar(x + width / 2, b3_vals, width, label="B3 (Sequential)", color="#FF9800")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("F1 Score")
    ax.set_title("Per-Task F1 Breakdown: JointLoRA-KV vs B3")
    ax.legend()
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved: {save_path}")


def plot_gradient_norms(
    lora_norms: Dict[int, List[float]],
    locret_norms: Dict[int, List[float]],
    save_path: str = "h-m2/figures/gradient_norms.png",
) -> None:
    _ensure_dir(save_path)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    colors = {42: "#E53935", 123: "#43A047", 456: "#1E88E5"}
    for seed in sorted(lora_norms.keys()):
        color = colors.get(seed, "#9E9E9E")
        axes[0].plot(lora_norms[seed], label=f"Seed {seed}", color=color, alpha=0.8)
        axes[1].plot(locret_norms[seed], label=f"Seed {seed}", color=color, alpha=0.8)

    axes[0].set_title("LoRA Gradient Norms")
    axes[0].set_xlabel("Log Step (×50)")
    axes[0].set_ylabel("Grad Norm")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].set_title("Locret Gradient Norms")
    axes[1].set_xlabel("Log Step (×50)")
    axes[1].set_ylabel("Grad Norm")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.suptitle("Gradient Norms: LoRA vs Locret Groups Over Training")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"  Saved: {save_path}")
