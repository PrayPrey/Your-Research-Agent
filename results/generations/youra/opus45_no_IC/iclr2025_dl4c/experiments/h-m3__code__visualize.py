"""Visualization for H-M3 convergence comparison."""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict, Any


def plot_learning_curve_comparison(
    fgo_curves: List[List[Tuple[int, float]]],
    standard_curves: List[List[Tuple[int, float]]],
    save_path: str
) -> None:
    """Plot learning curves: FGO vs Standard PPO (required figure)."""
    plt.figure(figsize=(10, 6))

    def plot_with_band(curves, label, color):
        if not curves:
            return
        all_steps = sorted(set(s for c in curves for s, _ in c))
        if not all_steps:
            return

        values = np.zeros((len(curves), len(all_steps)))
        for i, curve in enumerate(curves):
            curve_dict = dict(curve)
            for j, step in enumerate(all_steps):
                values[i, j] = curve_dict.get(step, np.nan)

        mean = np.nanmean(values, axis=0)
        std = np.nanstd(values, axis=0)

        plt.plot(all_steps, mean, label=label, color=color, linewidth=2)
        plt.fill_between(all_steps, mean - std, mean + std, color=color, alpha=0.2)

    plot_with_band(fgo_curves, "FGO PPO", "blue")
    plot_with_band(standard_curves, "Standard PPO", "orange")

    plt.xlabel("Training Steps")
    plt.ylabel("Pass@1")
    plt.title("Learning Curve Comparison: FGO vs Standard PPO")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_steps_to_target_bar(
    fgo_steps: float,
    standard_steps: float,
    save_path: str
) -> None:
    """Bar chart: steps to reach target pass@1."""
    plt.figure(figsize=(8, 5))

    conditions = ["Standard PPO", "FGO PPO"]
    steps = [standard_steps, fgo_steps]
    colors = ["orange", "blue"]

    plt.bar(conditions, steps, color=colors)
    plt.ylabel("Steps to Target Pass@1")
    plt.title("Convergence Speed: Steps to Target")

    for i, v in enumerate(steps):
        plt.text(i, v + max(steps) * 0.02, f"{v:.0f}", ha="center", fontsize=12)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_sample_efficiency(
    fgo_efficiency: float,
    standard_efficiency: float,
    save_path: str
) -> None:
    """Bar chart: pass@1 improvement per 1000 samples."""
    plt.figure(figsize=(8, 5))

    conditions = ["Standard PPO", "FGO PPO"]
    efficiency = [standard_efficiency, fgo_efficiency]
    colors = ["orange", "blue"]

    plt.bar(conditions, efficiency, color=colors)
    plt.ylabel("Pass@1 Gain per 1000 Samples")
    plt.title("Sample Efficiency Comparison")

    for i, v in enumerate(efficiency):
        plt.text(i, v + max(abs(e) for e in efficiency) * 0.02, f"{v:.4f}", ha="center", fontsize=12)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def plot_training_loss(
    fgo_loss: List[Tuple[int, float]],
    standard_loss: List[Tuple[int, float]],
    save_path: str
) -> None:
    """Plot training loss curves."""
    plt.figure(figsize=(10, 6))

    if fgo_loss:
        steps, losses = zip(*fgo_loss)
        plt.plot(steps, losses, label="FGO PPO", color="blue", alpha=0.7)

    if standard_loss:
        steps, losses = zip(*standard_loss)
        plt.plot(steps, losses, label="Standard PPO", color="orange", alpha=0.7)

    plt.xlabel("Training Steps")
    plt.ylabel("Loss")
    plt.title("Training Loss Curves")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Saved: {save_path}")


def generate_all_figures(
    results: Dict[str, Any],
    output_dir: str
) -> List[str]:
    """Generate all required and optional figures."""
    os.makedirs(output_dir, exist_ok=True)
    generated = []

    fgo_results = results.get("fgo", [])
    standard_results = results.get("standard", [])

    fgo_curves = [r["learning_curve"] for r in fgo_results if "learning_curve" in r]
    std_curves = [r["learning_curve"] for r in standard_results if "learning_curve" in r]

    path = os.path.join(output_dir, "learning_curve_comparison.png")
    plot_learning_curve_comparison(fgo_curves, std_curves, path)
    generated.append(path)

    if fgo_results and standard_results:
        fgo_steps = np.mean([r["steps_to_target"] for r in fgo_results])
        std_steps = np.mean([r["steps_to_target"] for r in standard_results])
        path = os.path.join(output_dir, "steps_to_target.png")
        plot_steps_to_target_bar(fgo_steps, std_steps, path)
        generated.append(path)

    return generated


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        results_path = sys.argv[1]
        with open(results_path, "r") as f:
            results = json.load(f)
        output_dir = os.path.dirname(results_path) or "."
        generate_all_figures(results, os.path.join(output_dir, "figures"))
