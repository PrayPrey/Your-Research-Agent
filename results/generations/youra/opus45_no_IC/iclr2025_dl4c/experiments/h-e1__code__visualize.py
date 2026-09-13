"""Visualization: 2x3 factorial bar chart and training curves."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional


def plot_gate_metrics(
    results: Dict[str, Dict],
    output_path: str = "figures/gate_metrics.png",
    title: str = "H-E1: FGO vs Standard PPO (2x3 Factorial)",
) -> None:
    """
    Generate 2x3 factorial bar chart comparing FGO vs Standard across feedback types.

    Args:
        results: Dict mapping condition_name to evaluation results
        output_path: Path to save figure
        title: Figure title
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    feedback_types = ["compile", "test", "combined"]
    conditions = ["standard", "fgo"]

    humaneval_data = {ft: {"standard": 0.0, "fgo": 0.0} for ft in feedback_types}
    mbpp_data = {ft: {"standard": 0.0, "fgo": 0.0} for ft in feedback_types}

    for cond_name, res in results.items():
        feedback_type = res["feedback_type"]
        use_fgo = res["use_fgo"]
        cond = "fgo" if use_fgo else "standard"

        if "humaneval" in res:
            humaneval_data[feedback_type][cond] = res["humaneval"]["pass@1"]
        if "mbpp" in res:
            mbpp_data[feedback_type][cond] = res["mbpp"]["pass@1"]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(len(feedback_types))
    width = 0.35

    for ax, data, dataset_name in [
        (axes[0], humaneval_data, "HumanEval"),
        (axes[1], mbpp_data, "MBPP"),
    ]:
        standard_vals = [data[ft]["standard"] for ft in feedback_types]
        fgo_vals = [data[ft]["fgo"] for ft in feedback_types]

        bars1 = ax.bar(x - width/2, standard_vals, width, label="Standard PPO", color="steelblue")
        bars2 = ax.bar(x + width/2, fgo_vals, width, label="FGO PPO", color="coral")

        ax.set_xlabel("Feedback Type")
        ax.set_ylabel("pass@1")
        ax.set_title(f"{dataset_name}")
        ax.set_xticks(x)
        ax.set_xticklabels([ft.capitalize() for ft in feedback_types])
        ax.legend()
        ax.set_ylim(0, 1.0)

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.2f}",
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha="center", va="bottom", fontsize=8)

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Gate metrics figure saved: {output_path}")


def plot_training_curves(
    results: Dict[str, Dict],
    output_path: str = "figures/training_curves.png",
) -> None:
    """
    Plot training reward curves for all 6 conditions.

    Args:
        results: Dict with training results including metrics_history
        output_path: Path to save figure
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, 6))

    for idx, (cond_name, res) in enumerate(results.items()):
        if cond_name == "experiment_info":
            continue

        history = res.get("metrics_history", [])
        if not history:
            continue

        episodes = [h["episode"] for h in history]
        rewards = [h["avg_reward"] for h in history]

        label = f"{'FGO' if res['use_fgo'] else 'Std'}+{res['feedback_type'].capitalize()}"
        ax.plot(episodes, rewards, label=label, color=colors[idx], linewidth=1.5)

    ax.set_xlabel("Episode")
    ax.set_ylabel("Average Reward")
    ax.set_title("Training Curves: 6 Conditions")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Training curves saved: {output_path}")


def plot_masking_stats(
    results: Dict[str, Dict],
    output_path: str = "figures/masking_stats.png",
) -> None:
    """
    Plot FGO masking statistics (% tokens masked per condition).

    Args:
        results: Dict with FGO mask stats
        output_path: Path to save figure
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fgo_conditions = []
    mask_percentages = []

    for cond_name, res in results.items():
        if cond_name == "experiment_info":
            continue
        if res.get("use_fgo") and res.get("fgo_mask_stats"):
            fgo_conditions.append(cond_name.replace("fgo_", "").capitalize())
            mask_percentages.append(np.mean(res["fgo_mask_stats"]))

    if not fgo_conditions:
        print("No FGO masking stats available")
        return

    fig, ax = plt.subplots(figsize=(8, 5))

    bars = ax.bar(fgo_conditions, mask_percentages, color="coral")

    ax.set_xlabel("Feedback Type")
    ax.set_ylabel("% Tokens Masked (Unexecuted)")
    ax.set_title("FGO Masking Statistics")
    ax.set_ylim(0, 100)

    for bar, pct in zip(bars, mask_percentages):
        ax.annotate(f"{pct:.1f}%",
                   xy=(bar.get_x() + bar.get_width() / 2, pct),
                   xytext=(0, 3),
                   textcoords="offset points",
                   ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"Masking stats saved: {output_path}")


def generate_all_figures(
    results_path: str,
    figures_dir: str = "figures",
) -> None:
    """
    Generate all figures from experiment results.

    Args:
        results_path: Path to factorial_results.json or evaluation_results.json
        figures_dir: Directory to save figures
    """
    with open(results_path) as f:
        results = json.load(f)

    eval_path = results_path.replace("factorial_results", "evaluation_results")
    if os.path.exists(eval_path):
        with open(eval_path) as f:
            eval_results = json.load(f)
        for cond, data in eval_results.items():
            if cond in results:
                results[cond].update(data)

    plot_gate_metrics(results, os.path.join(figures_dir, "gate_metrics.png"))
    plot_training_curves(results, os.path.join(figures_dir, "training_curves.png"))
    plot_masking_stats(results, os.path.join(figures_dir, "masking_stats.png"))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results_path = sys.argv[1]
    else:
        results_path = "outputs/factorial_results.json"

    generate_all_figures(results_path)
