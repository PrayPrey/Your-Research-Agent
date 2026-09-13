"""Visualization for H-M2."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd


def plot_correlation_heatmap(
    df: pd.DataFrame,
    cols: list[str],
    out_path: str,
) -> None:
    """Plot pairwise Spearman correlation heatmap."""
    corr_matrix = df[cols].corr(method="spearman")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".3f",
        cmap="RdYlBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        ax=ax,
    )
    ax.set_title("HaluEval vs TruthfulQA Correlation Matrix")

    # Clean up labels
    labels = [c.replace("halueval_", "HaluEval-").replace("truthfulqa_mc2", "TruthfulQA") for c in cols]
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels, rotation=0)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_scatter(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    r: float,
    out_path: str,
) -> None:
    """Scatter plot with regression line and correlation annotation."""
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.scatter(df[x_col], df[y_col], alpha=0.7, s=60)

    # Regression line
    z = np.polyfit(df[x_col], df[y_col], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[x_col].min(), df[x_col].max(), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)

    ax.set_xlabel("HaluEval Aggregate Score")
    ax.set_ylabel("TruthfulQA MC2 Score")
    ax.set_title(f"HaluEval vs TruthfulQA (r = {r:.3f})")

    # Annotate correlation
    ax.annotate(
        f"Spearman r = {r:.3f}",
        xy=(0.05, 0.95),
        xycoords="axes fraction",
        fontsize=12,
        fontweight="bold",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_gate_metrics(
    r_cross: float,
    r_intra_mean: float,
    threshold: float,
    out_path: str,
) -> None:
    """Bar chart comparing cross vs intra correlations with threshold."""
    fig, ax = plt.subplots(figsize=(8, 5))

    metrics = ["r(HaluEval, TruthfulQA)", "r(HaluEval intra-subtask)"]
    values = [r_cross, r_intra_mean]
    colors = ["#3498db", "#27ae60"]

    bars = ax.bar(metrics, values, color=colors, alpha=0.8, edgecolor="black")

    # Threshold line
    ax.axhline(y=threshold, color="red", linestyle="--", linewidth=2, label=f"Threshold = {threshold}")

    ax.set_ylabel("Spearman Correlation")
    ax.set_title("H-M2 Gate Metrics: Cross vs Intra Benchmark Correlation")
    ax.set_ylim(0, 1)
    ax.legend()

    # Value labels
    for bar, val in zip(bars, values):
        ax.annotate(
            f"{val:.3f}",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
