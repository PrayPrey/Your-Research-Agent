"""Visualization for h-m2 Pareto-Optimal ECE analysis."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot_pareto_frontier(df: pd.DataFrame, pareto_models: list, out_path: Path) -> None:
    """Scatter truthfulqa_mc1 (x) vs advglue_avg (y), pareto points highlighted."""
    fig, ax = plt.subplots(figsize=(8, 6))

    non_pareto = df[~df["model"].isin(pareto_models)]
    pareto = df[df["model"].isin(pareto_models)]

    ax.scatter(non_pareto["truthfulqa_mc1"], non_pareto["advglue_avg"],
               c="gray", alpha=0.6, label="Non-Pareto", s=60)
    ax.scatter(pareto["truthfulqa_mc1"], pareto["advglue_avg"],
               c="red", marker="^", s=100, label="Pareto-optimal")

    pareto_sorted = pareto.sort_values("truthfulqa_mc1")
    ax.step(pareto_sorted["truthfulqa_mc1"], pareto_sorted["advglue_avg"],
            where="post", color="red", linestyle="--", alpha=0.5)

    ax.set_xlabel("TruthfulQA MC1 Accuracy")
    ax.set_ylabel("AdvGLUE Average Accuracy")
    ax.set_title("Pareto Frontier: Truthfulness vs Adversarial Robustness")
    ax.legend()
    ax.grid(True, alpha=0.3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_ece_comparison(df: pd.DataFrame, out_path: Path) -> None:
    """Boxplot of 'ece' column grouped by 'is_pareto'."""
    fig, ax = plt.subplots(figsize=(6, 5))

    pareto_ece = df[df["is_pareto"]]["ece"]
    non_pareto_ece = df[~df["is_pareto"]]["ece"]

    ax.boxplot([pareto_ece, non_pareto_ece], labels=["Pareto-optimal", "Non-Pareto"])
    ax.set_ylabel("ECE (Expected Calibration Error)")
    ax.set_title("ECE Comparison: Pareto vs Non-Pareto Models")
    ax.grid(True, alpha=0.3, axis="y")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
