"""Visualization module for H-M3: Generate all required figures."""

import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import pandas as pd
import numpy as np

from config import ExperimentConfig


def save_fig(fig, out_path: str, dpi: int = 150):
    """Save figure and close it."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=dpi, bbox_inches='tight')
    plt.close(fig)


def plot_gate_metrics(result: dict, out_path: str, config: ExperimentConfig = None):
    """Bar chart showing pre-2021 vs post-2021 emergent share."""
    config = config or ExperimentConfig()

    fig, ax = plt.subplots(figsize=config.viz.figsize_default)

    periods = ["Pre-2021", "Post-2021"]
    shares = [result["pre_2021_emergent_share"], result["post_2021_emergent_share"]]
    colors = [config.viz.palette_traditional, config.viz.palette_emergent]

    bars = ax.bar(periods, shares, color=colors, edgecolor='black', linewidth=1.2)

    for bar, share in zip(bars, shares):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{share:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel("Emergent Benchmark Share", fontsize=12)
    ax.set_title("Researcher Attention Shift: Emergent vs Traditional Benchmarks", fontsize=14)
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50% threshold')

    change = result["share_increase"]
    p_val = result["p_value"]
    ax.text(0.95, 0.95, f"Change: {change:+.1%}\np-value: {p_val:.2e}",
            transform=ax.transAxes, ha='right', va='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    save_fig(fig, out_path, config.viz.dpi)


def plot_share_timeline(df: pd.DataFrame, out_path: str, config: ExperimentConfig = None):
    """Line plot of emergent vs traditional share over time."""
    config = config or ExperimentConfig()

    df_filtered = df[df["category"].isin(["emergent", "traditional"])].copy()

    monthly = df_filtered.groupby(["year_month", "category"])["paper_count"].sum().unstack(fill_value=0)
    monthly["total"] = monthly["emergent"] + monthly["traditional"]
    monthly["emergent_share"] = np.where(monthly["total"] > 0, monthly["emergent"] / monthly["total"], 0)
    monthly["traditional_share"] = np.where(monthly["total"] > 0, monthly["traditional"] / monthly["total"], 0)

    fig, ax = plt.subplots(figsize=config.viz.figsize_default)

    ax.plot(range(len(monthly)), monthly["emergent_share"],
            color=config.viz.palette_emergent, label='Emergent', linewidth=2)
    ax.plot(range(len(monthly)), monthly["traditional_share"],
            color=config.viz.palette_traditional, label='Traditional', linewidth=2)

    ax.axvline(x=list(monthly.index).index("2021-01") if "2021-01" in monthly.index else len(monthly)//2,
               color='gray', linestyle='--', alpha=0.7, label='2021-01 split')

    tick_positions = range(0, len(monthly), 12)
    tick_labels = [monthly.index[i] for i in tick_positions if i < len(monthly)]
    ax.set_xticks(list(tick_positions)[:len(tick_labels)])
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')

    ax.set_ylabel("Share of Total Papers", fontsize=12)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_title("Benchmark Share Over Time", fontsize=14)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 1)

    save_fig(fig, out_path, config.viz.dpi)


def plot_absolute_counts(df: pd.DataFrame, out_path: str, config: ExperimentConfig = None):
    """Stacked area chart of paper counts by category."""
    config = config or ExperimentConfig()

    df_filtered = df[df["category"].isin(["emergent", "traditional"])].copy()

    monthly = df_filtered.groupby(["year_month", "category"])["paper_count"].sum().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=config.viz.figsize_default)

    ax.stackplot(range(len(monthly)),
                 monthly.get("traditional", pd.Series([0]*len(monthly))),
                 monthly.get("emergent", pd.Series([0]*len(monthly))),
                 labels=["Traditional", "Emergent"],
                 colors=[config.viz.palette_traditional, config.viz.palette_emergent],
                 alpha=0.8)

    tick_positions = range(0, len(monthly), 12)
    tick_labels = [monthly.index[i] for i in tick_positions if i < len(monthly)]
    ax.set_xticks(list(tick_positions)[:len(tick_labels)])
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')

    ax.set_ylabel("Paper Count", fontsize=12)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_title("Absolute Paper Counts by Benchmark Category", fontsize=14)
    ax.legend(loc='upper left')

    save_fig(fig, out_path, config.viz.dpi)


def plot_benchmark_heatmap(df: pd.DataFrame, out_path: str, config: ExperimentConfig = None):
    """Heatmap of top N benchmarks by year."""
    config = config or ExperimentConfig()

    df = df.copy()
    df["year"] = df["year_month"].str[:4]

    yearly = df.groupby(["benchmark", "year"])["paper_count"].sum().unstack(fill_value=0)

    top_benchmarks = yearly.sum(axis=1).nlargest(config.viz.heatmap_top_n).index
    yearly_top = yearly.loc[top_benchmarks]

    fig, ax = plt.subplots(figsize=config.viz.figsize_heatmap)

    sns.heatmap(yearly_top, annot=True, fmt='d', cmap='YlOrRd', ax=ax,
                cbar_kws={'label': 'Paper Count'})

    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Benchmark", fontsize=12)
    ax.set_title(f"Top {config.viz.heatmap_top_n} Benchmarks by Paper Count", fontsize=14)

    save_fig(fig, out_path, config.viz.dpi)


def plot_chi_square_residuals(result: dict, out_path: str, config: ExperimentConfig = None):
    """Residual plot from chi-square test."""
    config = config or ExperimentConfig()

    expected = np.array(result.get("expected", [[0, 0], [0, 0]]))

    if expected.sum() == 0:
        fig, ax = plt.subplots(figsize=config.viz.figsize_default)
        ax.text(0.5, 0.5, "No data for residual analysis", ha='center', va='center', fontsize=14)
        ax.axis('off')
        save_fig(fig, out_path, config.viz.dpi)
        return

    observed = np.array([
        [result.get("pre_emergent", 0), result.get("pre_traditional", 0)],
        [result.get("post_emergent", 0), result.get("post_traditional", 0)],
    ])

    if observed.sum() == 0:
        observed = expected

    residuals = (observed - expected) / np.sqrt(expected + 1e-10)

    fig, ax = plt.subplots(figsize=config.viz.figsize_default)

    sns.heatmap(residuals, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax,
                xticklabels=['Emergent', 'Traditional'],
                yticklabels=['Pre-2021', 'Post-2021'],
                cbar_kws={'label': 'Standardized Residual'})

    ax.set_title(f"Chi-Square Residuals (Chi2={result['chi2_statistic']:.2f}, p={result['p_value']:.2e})", fontsize=14)

    save_fig(fig, out_path, config.viz.dpi)
