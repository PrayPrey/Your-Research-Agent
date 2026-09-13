"""Generate figures for H-E1 experiment results."""

import json
import os
import sys
import csv

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CONFIG, CONDITIONS

CONDITION_COLORS = {
    "curriculum": "#2196F3",  # Blue
    "uniform": "#FF9800",     # Orange
    "easy_only": "#4CAF50",   # Green
    "hard_only": "#F44336",   # Red
}

CONDITION_LABELS = {
    "curriculum": "Curriculum (Easy→Hard)",
    "uniform": "Uniform Random",
    "easy_only": "Easy Only",
    "hard_only": "Hard Only",
}


def plot_gate_metric_comparison(results: dict, output_path: str) -> None:
    """Bar chart: Curriculum vs Uniform final pass@1 on HumanEval+."""
    fig, ax = plt.subplots(figsize=(8, 6))

    conditions = ["curriculum", "uniform"]
    values = [results.get(c, {}).get("final_pass@1", 0.0) for c in conditions]
    colors = [CONDITION_COLORS[c] for c in conditions]
    labels = [CONDITION_LABELS[c] for c in conditions]

    bars = ax.bar(labels, values, color=colors, alpha=0.85, edgecolor="black", linewidth=0.5)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.002,
            f"{val:.3f}",
            ha="center", va="bottom", fontsize=12, fontweight="bold",
        )

    # Add 2pp threshold line
    if values[1] > 0:
        threshold = values[1] + 0.02
        ax.axhline(y=threshold, color="black", linestyle="--", linewidth=1.5,
                   label=f"Uniform + 2pp = {threshold:.3f}")
        ax.legend(fontsize=10)

    ax.set_ylabel("pass@1 (HumanEval+)", fontsize=12)
    ax.set_title("Gate Metric: Curriculum vs Uniform (Final Checkpoint)", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(values) * 1.2 + 0.05)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_learning_curves(all_results: dict, output_path: str) -> None:
    """pass@1 vs training step for all 4 conditions."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for condition in CONDITIONS:
        if condition not in all_results:
            continue
        checkpoints = all_results[condition].get("checkpoints", [])
        steps = [c["step"] for c in checkpoints if c.get("pass@1") is not None]
        scores = [c["pass@1"] for c in checkpoints if c.get("pass@1") is not None]
        if steps:
            ax.plot(steps, scores, marker="o", color=CONDITION_COLORS[condition],
                    label=CONDITION_LABELS[condition], linewidth=2, markersize=5)

    ax.axvline(x=CONFIG["curriculum_step"], color="gray", linestyle="--", linewidth=1.5,
               alpha=0.7, label=f"Curriculum switch (step {CONFIG['curriculum_step']})")

    ax.set_xlabel("Training Step", fontsize=12)
    ax.set_ylabel("pass@1 (HumanEval+)", fontsize=12)
    ax.set_title("Learning Curves: All 4 Conditions", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_reward_density(log_dir: str, output_path: str) -> None:
    """Reward density over time for all 4 conditions."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for condition in CONDITIONS:
        csv_path = os.path.join(log_dir, f"reward_density_{condition}.csv")
        if not os.path.exists(csv_path):
            continue
        try:
            df = pd.read_csv(csv_path)
            if "step" in df.columns and "reward_density" in df.columns:
                # Smooth with rolling average
                window = min(50, len(df) // 10 + 1)
                smoothed = df["reward_density"].rolling(window=window, min_periods=1).mean()
                ax.plot(df["step"], smoothed, color=CONDITION_COLORS[condition],
                        label=CONDITION_LABELS[condition], linewidth=2, alpha=0.85)
        except Exception as e:
            print(f"Warning: Could not read {csv_path}: {e}")

    ax.axvline(x=CONFIG["curriculum_step"], color="gray", linestyle="--", linewidth=1.5,
               alpha=0.7, label=f"Curriculum switch (step {CONFIG['curriculum_step']})")

    ax.set_xlabel("Training Step", fontsize=12)
    ax.set_ylabel("Reward Density (fraction non-degenerate steps)", fontsize=12)
    ax.set_title("Reward Density Over Training", fontsize=13, fontweight="bold")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def plot_condition_table(final_results: dict, output_path: str) -> None:
    """Final pass@1 HumanEval+ and MBPP+ for all 4 conditions."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")

    columns = ["Condition", "HumanEval+ pass@1", "MBPP+ pass@1", "Gate"]
    rows = []
    for condition in CONDITIONS:
        res = final_results.get(condition, {})
        he_score = res.get("final_pass@1", "N/A")
        mbpp_score = res.get("final_mbpp_pass@1", "N/A")
        gate = res.get("gate", "N/A")
        if isinstance(he_score, float):
            he_score = f"{he_score:.4f}"
        if isinstance(mbpp_score, float):
            mbpp_score = f"{mbpp_score:.4f}"
        rows.append([CONDITION_LABELS[condition], he_score, mbpp_score, gate])

    table = ax.table(
        cellText=rows,
        colLabels=columns,
        cellLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)

    # Style header
    for j in range(len(columns)):
        table[(0, j)].set_facecolor("#2196F3")
        table[(0, j)].set_text_props(color="white", fontweight="bold")

    # Alternating row colors
    for i in range(1, len(rows) + 1):
        color = "#F5F5F5" if i % 2 == 0 else "white"
        for j in range(len(columns)):
            table[(i, j)].set_facecolor(color)

    ax.set_title("Final Results: All Conditions", fontsize=13, fontweight="bold", pad=20)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def generate_all_figures(results_dir: str, log_dir: str, figures_dir: str) -> None:
    """Generate all 4 required figures from experiment results."""
    os.makedirs(figures_dir, exist_ok=True)

    # Load all results
    all_results = {}
    for condition in CONDITIONS:
        path = os.path.join(results_dir, f"eval_results_{condition}.json")
        if os.path.exists(path):
            with open(path) as f:
                all_results[condition] = json.load(f)

    if not all_results:
        print("Warning: No result files found. Generating placeholder figures.")

    # Figure 1: Gate metric bar chart
    plot_gate_metric_comparison(
        all_results,
        os.path.join(figures_dir, "gate_metric_comparison.png"),
    )

    # Figure 2: Learning curves
    plot_learning_curves(
        all_results,
        os.path.join(figures_dir, "learning_curves.png"),
    )

    # Figure 3: Reward density over time
    plot_reward_density(
        log_dir,
        os.path.join(figures_dir, "reward_density.png"),
    )

    # Figure 4: Condition comparison table
    plot_condition_table(
        all_results,
        os.path.join(figures_dir, "condition_comparison_table.png"),
    )

    print(f"\nAll figures saved to: {figures_dir}")
