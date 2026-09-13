"""Visualization suite for H-M1."""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from config import CONFIG


def plot_gate_comparison(stats_result: dict, out_path: str) -> None:
    """Bar chart: high_use_avg vs low_use_avg with threshold line."""
    fig, ax = plt.subplots(figsize=(8, 6))

    groups = ["High-Use", "Low-Use"]
    values = [stats_result["high_use_avg"], stats_result["low_use_avg"]]
    colors = ["#2ecc71", "#e74c3c"]

    bars = ax.bar(groups, values, color=colors)

    threshold_y = stats_result["low_use_avg"] * CONFIG.ratio_threshold
    ax.axhline(y=threshold_y, color="black", linestyle="--", label=f"3:1 Threshold")

    ax.set_ylabel("Average Optimization Papers")
    ax.set_title(f"H-M1: Optimization Paper Counts\nRatio: {stats_result['ratio']:.2f}")
    ax.legend()

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_per_dataset_bars(df: pd.DataFrame, out_path: str) -> None:
    """Grouped bar chart: paper_count per dataset."""
    fig, ax = plt.subplots(figsize=(14, 6))

    palette = {"high": "#2ecc71", "low": "#e74c3c"}
    sns.barplot(data=df, x="name", y="paper_count", hue="group", palette=palette, ax=ax)

    ax.set_xlabel("Dataset")
    ax.set_ylabel("Optimization Paper Count")
    ax.set_title("Optimization Papers by Dataset")
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_boxplot(df: pd.DataFrame, out_path: str) -> None:
    """Box plot: paper_count distribution by group."""
    fig, ax = plt.subplots(figsize=(8, 6))

    palette = {"high": "#2ecc71", "low": "#e74c3c"}
    sns.boxplot(data=df, x="group", y="paper_count", palette=palette, ax=ax)

    ax.set_xlabel("Dataset Group")
    ax.set_ylabel("Optimization Paper Count")
    ax.set_title("Paper Count Distribution: High-Use vs Low-Use")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_correlation_scatter(df: pd.DataFrame, corr: dict, out_path: str) -> None:
    """Scatter: run_count vs paper_count with correlation annotation."""
    fig, ax = plt.subplots(figsize=(8, 6))

    palette = {"high": "#2ecc71", "low": "#e74c3c"}
    sns.scatterplot(data=df, x="run_count", y="paper_count", hue="group", palette=palette, s=100, ax=ax)

    ax.set_xlabel("Run Count (OpenML)")
    ax.set_ylabel("Optimization Paper Count (S2)")
    ax.set_title(f"Correlation: ρ={corr['rho']:.3f}, p={corr['p_value']:.4f}")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
