"""Visualization module for h-e1 experiment."""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import FIGURES_DIR
from analysis import residualize


def plot_scatter(df: pd.DataFrame, result: dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    for family in df["family"].unique():
        subset = df[df["family"] == family]
        ax.scatter(subset["truthfulqa_mc1"], subset["advglue_avg"], label=family, s=80, alpha=0.7)

    ax.set_xlabel("TruthfulQA MC1 Accuracy")
    ax.set_ylabel("GLUE Average Accuracy")
    ax.set_title(f"Partial Correlation: r={result['r']:.3f}, p={result['p']:.4f}")
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_residuals(df: pd.DataFrame, result: dict, out_path: str) -> None:
    x = df["truthfulqa_mc1"].values
    y = df["advglue_avg"].values
    z = df["log_params"].values

    rx = residualize(x, z)
    ry = residualize(y, z)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(rx, ry, s=80, alpha=0.7)

    coef = np.polyfit(rx, ry, 1)
    x_line = np.linspace(rx.min(), rx.max(), 100)
    ax.plot(x_line, np.polyval(coef, x_line), "r--", alpha=0.8, label="Linear fit")

    ax.set_xlabel("Residualized TruthfulQA MC1")
    ax.set_ylabel("Residualized GLUE Avg")
    ax.set_title(f"Residuals (controlling for log(params))\nr={result['r']:.3f}")
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_bootstrap_hist(result: dict, out_path: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.hist(result["bootstrap_rs"], bins=50, edgecolor="black", alpha=0.7)
    ax.axvline(result["r"], color="red", linestyle="--", linewidth=2, label=f"Observed r={result['r']:.3f}")
    ax.axvline(result["ci_lower"], color="green", linestyle=":", linewidth=2, label=f"95% CI: [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
    ax.axvline(result["ci_upper"], color="green", linestyle=":", linewidth=2)
    ax.axvline(0.3, color="orange", linestyle="-", linewidth=2, alpha=0.5, label="Threshold (r=0.3)")

    ax.set_xlabel("Bootstrap Partial Correlation (r)")
    ax.set_ylabel("Frequency")
    ax.set_title("Bootstrap Distribution of Partial Correlation")
    ax.legend()

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_family_comparison(df: pd.DataFrame, out_path: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    family_order = df.groupby("family")["truthfulqa_mc1"].mean().sort_values(ascending=False).index.tolist()

    sns.barplot(data=df, x="family", y="truthfulqa_mc1", ax=axes[0], order=family_order)
    axes[0].set_title("TruthfulQA MC1 by Family")
    axes[0].set_ylabel("Accuracy")

    sns.barplot(data=df, x="family", y="advglue_avg", ax=axes[1], order=family_order)
    axes[1].set_title("GLUE Avg by Family")
    axes[1].set_ylabel("Accuracy")

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def generate_all_figures(df: pd.DataFrame, result: dict, figures_dir: str = None) -> None:
    figures_dir = figures_dir or FIGURES_DIR
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    plot_scatter(df, result, os.path.join(figures_dir, "scatter.png"))
    plot_residuals(df, result, os.path.join(figures_dir, "residuals.png"))
    plot_bootstrap_hist(result, os.path.join(figures_dir, "bootstrap_hist.png"))
    plot_family_comparison(df, os.path.join(figures_dir, "family_comparison.png"))


if __name__ == "__main__":
    from aggregate import collect_scores
    from analysis import run_analysis

    df = collect_scores()
    result = run_analysis(df)
    generate_all_figures(df, result)
