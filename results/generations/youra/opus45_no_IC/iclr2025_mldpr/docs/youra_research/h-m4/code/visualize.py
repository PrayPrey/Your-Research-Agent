# visualize.py - H-M4 visualization functions

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from config import FIGSIZE_SCATTER, FIGSIZE_BAR, FIGSIZE_BOX, DPI, VENUE_COLORS, FIGURES_DIR


def plot_gate_metrics(results: dict, agg_df: pd.DataFrame, out_path: str = None) -> None:
    """
    Scatter plot: entropy vs mean_concentration, regression line + CI band.
    Color by venue, annotate rho/p in title.
    """
    if out_path is None:
        out_path = str(Path(FIGURES_DIR) / "gate_metrics.png")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=FIGSIZE_SCATTER)

    # Add entropy column from results or merge externally
    # Assuming agg_df has entropy column
    if "entropy" not in agg_df.columns:
        print("Warning: entropy column missing in agg_df")
        return

    # Scatter with venue colors
    for venue in agg_df["venue"].unique():
        subset = agg_df[agg_df["venue"] == venue]
        ax.scatter(
            subset["entropy"],
            subset["mean_concentration"],
            c=VENUE_COLORS.get(venue, "gray"),
            label=venue,
            s=subset["n_papers"] * 2,  # size by paper count
            alpha=0.7,
        )

    # Regression line with CI
    sns.regplot(
        x="entropy",
        y="mean_concentration",
        data=agg_df,
        scatter=False,
        ax=ax,
        line_kws={"color": "red", "linewidth": 2},
        ci=95,
    )

    ax.set_xlabel("Entropy (benchmark diversity)", fontsize=12)
    ax.set_ylabel("Mean Concentration (1/breadth)", fontsize=12)

    rho = results.get("spearman_rho", 0)
    p = results.get("p_value", 1)
    ax.set_title(f"H-M4: Entropy vs Benchmark Concentration\nρ = {rho:.3f}, p = {p:.4f}", fontsize=14)

    ax.legend(title="Venue", loc="best")
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def plot_entropy_variance_scatter(agg_df: pd.DataFrame, out_path: str = None) -> None:
    """Detailed scatter with venue markers and size by n_papers."""
    if out_path is None:
        out_path = str(Path(FIGURES_DIR) / "entropy_variance_scatter.png")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=FIGSIZE_SCATTER)

    markers = {"NeurIPS": "o", "ICML": "s", "ICLR": "^"}

    for venue in agg_df["venue"].unique():
        subset = agg_df[agg_df["venue"] == venue]
        ax.scatter(
            subset["entropy"],
            subset["mean_concentration"],
            c=VENUE_COLORS.get(venue, "gray"),
            marker=markers.get(venue, "o"),
            label=venue,
            s=subset["n_papers"] * 3,
            alpha=0.7,
            edgecolors="black",
        )

    ax.set_xlabel("Entropy", fontsize=12)
    ax.set_ylabel("Mean Concentration", fontsize=12)
    ax.set_title("Entropy vs Benchmark Concentration by Venue", fontsize=14)
    ax.legend(title="Venue")
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def plot_per_venue_correlation(results: dict, out_path: str = None) -> None:
    """Bar chart of Spearman ρ per venue."""
    if out_path is None:
        out_path = str(Path(FIGURES_DIR) / "per_venue_correlation.png")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    per_venue = results.get("per_venue", {})
    if not per_venue:
        print("No per-venue results to plot")
        return

    venues = list(per_venue.keys())
    rhos = [per_venue[v]["rho"] for v in venues]
    colors = [VENUE_COLORS.get(v, "gray") for v in venues]

    fig, ax = plt.subplots(figsize=FIGSIZE_BAR)

    bars = ax.bar(venues, rhos, color=colors, edgecolor="black")

    # Add horizontal line at 0
    ax.axhline(y=0, color="black", linestyle="-", linewidth=0.5)

    ax.set_xlabel("Venue", fontsize=12)
    ax.set_ylabel("Spearman ρ", fontsize=12)
    ax.set_title("Per-Venue Correlation (Entropy vs Concentration)", fontsize=14)

    # Add p-value annotations
    for i, v in enumerate(venues):
        p = per_venue[v].get("p", 1)
        sig = "*" if p < 0.05 else ""
        ax.annotate(
            f"ρ={rhos[i]:.2f}{sig}",
            xy=(i, rhos[i]),
            ha="center",
            va="bottom" if rhos[i] >= 0 else "top",
            fontsize=10,
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def plot_variance_by_entropy_quartile(agg_df: pd.DataFrame, out_path: str = None) -> None:
    """Box plots of mean_concentration by entropy quartile."""
    if out_path is None:
        out_path = str(Path(FIGURES_DIR) / "variance_by_entropy_quartile.png")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    # Create quartiles
    agg_df = agg_df.copy()
    try:
        agg_df["entropy_quartile"] = pd.qcut(
            agg_df["entropy"], q=4, labels=["Q1 (Low)", "Q2", "Q3", "Q4 (High)"]
        )
    except ValueError:
        # If not enough unique values, use fewer bins
        agg_df["entropy_quartile"] = pd.cut(
            agg_df["entropy"], bins=3, labels=["Low", "Medium", "High"]
        )

    fig, ax = plt.subplots(figsize=FIGSIZE_BOX)

    agg_df.boxplot(column="mean_concentration", by="entropy_quartile", ax=ax)

    ax.set_xlabel("Entropy Quartile", fontsize=12)
    ax.set_ylabel("Mean Concentration", fontsize=12)
    ax.set_title("Benchmark Concentration by Entropy Quartile", fontsize=14)
    plt.suptitle("")  # Remove auto-generated title
    plt.tight_layout()
    plt.savefig(out_path, dpi=DPI)
    plt.close()
    print(f"Saved: {out_path}")


def generate_all(results: dict, agg_df: pd.DataFrame, out_dir: str = FIGURES_DIR) -> None:
    """Generate all 4 required figures."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_gate_metrics(results, agg_df, str(out_dir / "gate_metrics.png"))
    plot_entropy_variance_scatter(agg_df, str(out_dir / "entropy_variance_scatter.png"))
    plot_per_venue_correlation(results, str(out_dir / "per_venue_correlation.png"))
    plot_variance_by_entropy_quartile(agg_df, str(out_dir / "variance_by_entropy_quartile.png"))
