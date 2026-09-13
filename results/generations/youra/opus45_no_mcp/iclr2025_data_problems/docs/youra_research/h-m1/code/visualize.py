import os
import numpy as np
import matplotlib.pyplot as plt


def plot_accuracy_by_level(results: dict, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)

    levels = sorted(results.keys())
    cont_accs = [results[l]["mean_contaminated_acc"] for l in levels]
    clean_accs = [results[l]["mean_clean_acc"] for l in levels]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = [l * 100 for l in levels]
    ax.plot(x, cont_accs, 'o-', label="Contaminated Items", linewidth=2, markersize=8, color='red')
    ax.plot(x, clean_accs, 's-', label="Clean Items", linewidth=2, markersize=8, color='blue')
    ax.set_xlabel("Contamination Level (%)", fontsize=12)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("H-M1: Contaminated vs Clean Item Accuracy by Level", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "accuracy_by_level.png"), dpi=150)
    plt.close()


def plot_effect_size_bars(results: dict, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)

    levels = sorted([l for l in results.keys() if l > 0])
    effect_sizes = [results[l]["mean_effect_size"] for l in levels]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = [f"{int(l*100)}%" for l in levels]
    colors = ['green' if e > 0.05 else 'orange' if e > 0 else 'red' for e in effect_sizes]
    bars = ax.bar(x, effect_sizes, color=colors, edgecolor='black')
    ax.axhline(y=0.05, color='black', linestyle='--', label='Target (5%)')
    ax.set_xlabel("Contamination Level", fontsize=12)
    ax.set_ylabel("Effect Size (Contaminated - Clean Acc)", fontsize=12)
    ax.set_title("H-M1: Effect Size by Contamination Level", fontsize=14)
    ax.legend()
    for bar, val in zip(bars, effect_sizes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, f"{val:.3f}",
                ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "effect_size.png"), dpi=150)
    plt.close()


def plot_item_accuracy_distribution(clean_correct: list, contaminated_correct: list, figures_dir: str):
    os.makedirs(figures_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    data = [[1 if c else 0 for c in clean_correct], [1 if c else 0 for c in contaminated_correct]]
    labels = ["Clean Items", "Contaminated Items"]
    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    colors = ["lightblue", "lightcoral"]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
    ax.set_ylabel("Correctness (0/1)")
    ax.set_title("H-M1: Item Correctness Distribution")
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "item_distribution.png"), dpi=150)
    plt.close()
