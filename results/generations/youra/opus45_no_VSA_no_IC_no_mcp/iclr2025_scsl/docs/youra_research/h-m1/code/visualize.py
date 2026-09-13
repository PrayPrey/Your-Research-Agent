import json
import os
import numpy as np
import matplotlib.pyplot as plt
from config import Config


def plot_gate_bar_chart(gate_result: dict, all_records: dict, save_path: str):
    fig, ax = plt.subplots(figsize=(10, 6))

    seeds = list(all_records.keys())
    early_ratios = [gate_result["per_seed"][s]["early_ratio"] for s in seeds]
    threshold = gate_result["threshold"]

    colors = ["#2ecc71" if er >= threshold else "#e74c3c" for er in early_ratios]
    bars = ax.bar([f"Seed {s}" for s in seeds], early_ratios, color=colors)

    ax.axhline(y=threshold, color="#3498db", linestyle="--", linewidth=2, label=f"Threshold ({threshold})")
    ax.axhline(y=1.0, color="#95a5a6", linestyle=":", linewidth=1, label="Ratio = 1.0")

    ax.set_ylabel("Spurious/Core Gradient Norm Ratio")
    ax.set_title("Gate Check: Early Epoch (1-10) Gradient Norm Ratio")
    ax.legend()
    ax.set_ylim(0, max(early_ratios) * 1.2)

    for bar, er in zip(bars, early_ratios):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{er:.2f}", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_ratio_trajectory(all_records: dict, save_path: str):
    fig, ax = plt.subplots(figsize=(12, 6))

    colors = ["#3498db", "#e74c3c", "#2ecc71"]
    for i, (seed, records) in enumerate(all_records.items()):
        epochs = [r["epoch"] for r in records]
        ratios = [r["ratio"] for r in records]
        ax.plot(epochs, ratios, marker="o", markersize=3, label=f"Seed {seed}",
                color=colors[i % len(colors)], alpha=0.8)

    ax.axhline(y=1.5, color="#9b59b6", linestyle="--", linewidth=2, label="Target (1.5)")
    ax.axhline(y=1.0, color="#95a5a6", linestyle=":", linewidth=1, label="Ratio = 1.0")

    ax.set_xlabel("Epoch")
    ax.set_ylabel("Spurious/Core Gradient Norm Ratio")
    ax.set_title("Gradient Norm Ratio Trajectory Over Training")
    ax.legend()
    ax.set_xlim(1, max(epochs))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_norm_comparison(all_records: dict, save_path: str):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for seed, records in all_records.items():
        epochs = [r["epoch"] for r in records]
        minority_norms = [r["minority_norm"] for r in records]
        spurious_norms = [r["spurious_norm"] for r in records]

        axes[0].plot(epochs, minority_norms, label=f"Seed {seed}", alpha=0.7)
        axes[1].plot(epochs, spurious_norms, label=f"Seed {seed}", alpha=0.7)

    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Minority Group Gradient Norm")
    axes[0].set_title("Minority Group (label != place) Gradient Norms")
    axes[0].legend()

    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Spurious-Aligned Group Gradient Norm")
    axes[1].set_title("Spurious-Aligned Group (label == place) Gradient Norms")
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def main():
    config = Config()
    os.makedirs(config.figures_dir, exist_ok=True)

    records_path = os.path.join(config.output_dir, "gradient_norm_records.json")
    gate_path = os.path.join(config.output_dir, "gate_result.json")

    with open(records_path, "r") as f:
        all_records = json.load(f)
    with open(gate_path, "r") as f:
        gate_result = json.load(f)

    all_records = {int(k): v for k, v in all_records.items()}
    gate_result["per_seed"] = {int(k): v for k, v in gate_result["per_seed"].items()}

    plot_gate_bar_chart(
        gate_result, all_records,
        os.path.join(config.figures_dir, "gate_bar_chart.png")
    )
    print("Generated: gate_bar_chart.png")

    plot_ratio_trajectory(
        all_records,
        os.path.join(config.figures_dir, "ratio_trajectory.png")
    )
    print("Generated: ratio_trajectory.png")

    plot_norm_comparison(
        all_records,
        os.path.join(config.figures_dir, "norm_comparison.png")
    )
    print("Generated: norm_comparison.png")

    print(f"\nAll figures saved to {config.figures_dir}")


if __name__ == "__main__":
    main()
