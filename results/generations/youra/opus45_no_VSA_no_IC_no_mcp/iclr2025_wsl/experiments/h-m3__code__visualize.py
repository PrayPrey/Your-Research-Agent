import os
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt

from config import ExperimentResult


def plot_gate_2x2_bar(stats: Dict, out_path: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    archs = ["mlp", "dws", "nft"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for idx, task in enumerate(["backdoor", "accuracy"]):
        ax = axes[idx]
        means = [stats.get(f"{task}_{arch}", {}).get("mean", 0) for arch in archs]
        stds = [stats.get(f"{task}_{arch}", {}).get("std", 0) for arch in archs]

        x = np.arange(len(archs))
        bars = ax.bar(x, means, yerr=stds, capsize=5, color=colors, alpha=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels([a.upper() for a in archs])
        ax.set_title(f"{task.capitalize()} Task")
        ax.set_ylabel("AUC" if task == "backdoor" else "RMSE")

        for bar, mean in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                   f"{mean:.3f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_interaction(stats: Dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    archs = ["mlp", "dws", "nft"]
    tasks = ["backdoor", "accuracy"]
    markers = ["o", "s"]
    colors = ["#1f77b4", "#ff7f0e"]

    for task_idx, task in enumerate(tasks):
        means = []
        stds = []
        for arch in archs:
            key = f"{task}_{arch}"
            mean = stats.get(key, {}).get("mean", 0)
            std = stats.get(key, {}).get("std", 0)
            if task == "accuracy":
                mean = -mean
                std = std
            means.append(mean)
            stds.append(std)

        x = np.arange(len(archs))
        ax.errorbar(x, means, yerr=stds, marker=markers[task_idx],
                   color=colors[task_idx], label=task.capitalize(),
                   linewidth=2, markersize=8, capsize=5)

    ax.set_xticks(np.arange(len(archs)))
    ax.set_xticklabels([a.upper() for a in archs])
    ax.set_xlabel("Architecture")
    ax.set_ylabel("Performance (AUC / -RMSE)")
    ax.set_title("Architecture x Task Interaction")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_training_curves(histories: Dict[str, Dict[int, float]], out_path: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    archs = ["mlp", "dws", "nft"]
    colors = {"mlp": "#1f77b4", "dws": "#ff7f0e", "nft": "#2ca02c"}
    linestyles = ["-", "--", ":"]

    for task_idx, task in enumerate(["backdoor", "accuracy"]):
        ax = axes[task_idx]

        for arch in archs:
            task_arch_histories = {k: v for k, v in histories.items() if k.startswith(f"{task}_{arch}_")}

            if task_arch_histories:
                all_losses = []
                for key, hist in task_arch_histories.items():
                    epochs = sorted(hist.keys())
                    losses = [hist[e] for e in epochs]
                    all_losses.append(losses)

                mean_losses = np.mean(all_losses, axis=0)
                std_losses = np.std(all_losses, axis=0)
                epochs = range(len(mean_losses))

                ax.plot(epochs, mean_losses, color=colors[arch], label=arch.upper(), linewidth=2)
                ax.fill_between(epochs, mean_losses - std_losses, mean_losses + std_losses,
                              color=colors[arch], alpha=0.2)

        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title(f"{task.capitalize()} Task - Training Curves")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_diff_heatmap(stats: Dict, baseline: str, out_path: str) -> None:
    tasks = ["backdoor", "accuracy"]
    archs = ["mlp", "dws", "nft"]

    diff_matrix = np.zeros((len(tasks), len(archs)))

    for i, task in enumerate(tasks):
        baseline_mean = stats.get(f"{task}_{baseline}", {}).get("mean", 0)
        for j, arch in enumerate(archs):
            arch_mean = stats.get(f"{task}_{arch}", {}).get("mean", 0)
            if task == "backdoor":
                diff_matrix[i, j] = arch_mean - baseline_mean
            else:
                diff_matrix[i, j] = baseline_mean - arch_mean

    fig, ax = plt.subplots(figsize=(8, 4))

    im = ax.imshow(diff_matrix, cmap="RdYlGn", aspect="auto")

    ax.set_xticks(np.arange(len(archs)))
    ax.set_yticks(np.arange(len(tasks)))
    ax.set_xticklabels([a.upper() for a in archs])
    ax.set_yticklabels([t.capitalize() for t in tasks])

    for i in range(len(tasks)):
        for j in range(len(archs)):
            text = ax.text(j, i, f"{diff_matrix[i, j]:.3f}",
                          ha="center", va="center", color="black", fontsize=11)

    ax.set_title(f"Performance Difference vs {baseline.upper()} (green=better)")
    plt.colorbar(im, ax=ax, label="Difference")

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=150)
    plt.close()
