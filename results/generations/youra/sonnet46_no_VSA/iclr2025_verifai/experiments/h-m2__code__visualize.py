"""Visualization module for h-m2 contract richness analysis."""
from pathlib import Path
from typing import Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

FIGURES_DIR = Path(__file__).parent.parent / "figures"

_TIER_COLORS = {1: "#4e9af1", 2: "#f6a623", 3: "#7ed321", 4: "#d0021b"}
_TIER_LABELS = {1: "Simple", 2: "Structural", 3: "Relational", 4: "Compound"}


def plot_gate_metrics(rho: float, threshold: float, p_value: float, out_dir: Path) -> None:
    """Bar chart: achieved rho vs threshold; p-value annotated."""
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(
        ["Achieved ρ", "Threshold ρ"],
        [rho, threshold],
        color=["#2ecc71" if rho >= threshold else "#e74c3c", "#bdc3c7"],
        edgecolor="black",
        linewidth=0.8,
    )
    ax.set_ylabel("Spearman ρ", fontsize=12)
    ax.set_title("Gate Metric: Spearman ρ vs Threshold", fontsize=13)
    ax.set_ylim(0, max(rho, threshold) * 1.3)
    ax.axhline(threshold, color="gray", linestyle="--", linewidth=1, label=f"Threshold = {threshold:.2f}")
    for bar, val in zip(bars, [rho, threshold]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    ax.annotate(f"p-exact = {p_value:.4f}", xy=(0.98, 0.95), xycoords="axes fraction", ha="right", va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"))
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(out_dir / "figure_gate_metrics.png", dpi=150)
    plt.close()


def plot_scatter(richness_df: pd.DataFrame, gap_dict: dict, rho: float, out_dir: Path) -> None:
    """Scatter: richness score (x) vs gap (y), colored by tier, rho annotated."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df = richness_df.copy()
    df["gap"] = df["task_id"].map(gap_dict)
    df = df.dropna(subset=["gap"])

    fig, ax = plt.subplots(figsize=(7, 5))
    for tier in [1, 2, 3, 4]:
        sub = df[df["tier"] == tier]
        ax.scatter(sub["score"], sub["gap"], c=_TIER_COLORS[tier], label=f"Tier {tier}: {_TIER_LABELS[tier]}",
                   alpha=0.6, s=30, edgecolors="none")

    # Regression line
    m, b = np.polyfit(df["score"], df["gap"], 1)
    xs = np.linspace(df["score"].min(), df["score"].max(), 100)
    ax.plot(xs, m * xs + b, "k--", linewidth=1, alpha=0.7)

    ax.set_xlabel("Contract Richness Score", fontsize=12)
    ax.set_ylabel("Oracle Isolation Gap", fontsize=12)
    ax.set_title(f"Richness Score vs Oracle Gap (ρ = {rho:.3f})", fontsize=13)
    ax.legend(fontsize=9, loc="upper left")
    ax.annotate(f"ρ = {rho:.3f}", xy=(0.98, 0.05), xycoords="axes fraction", ha="right", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="gray"))
    plt.tight_layout()
    plt.savefig(out_dir / "figure_scatter.png", dpi=150)
    plt.close()


def plot_boxplot(richness_df: pd.DataFrame, gap_dict: dict, out_dir: Path) -> None:
    """Boxplot: gap distribution per tier 1-4."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df = richness_df.copy()
    df["gap"] = df["task_id"].map(gap_dict)
    df = df.dropna(subset=["gap"])

    fig, ax = plt.subplots(figsize=(7, 5))
    tier_data = [df[df["tier"] == t]["gap"].tolist() for t in [1, 2, 3, 4]]
    bp = ax.boxplot(tier_data, patch_artist=True, medianprops={"color": "black", "linewidth": 2})
    for patch, tier in zip(bp["boxes"], [1, 2, 3, 4]):
        patch.set_facecolor(_TIER_COLORS[tier])
        patch.set_alpha(0.7)

    ax.set_xticklabels([f"T{t}: {_TIER_LABELS[t]}" for t in [1, 2, 3, 4]], fontsize=10)
    ax.set_ylabel("Oracle Isolation Gap", fontsize=12)
    ax.set_title("Oracle Gap by Richness Tier", fontsize=13)

    # Annotate n per tier
    for i, (t, td) in enumerate(zip([1, 2, 3, 4], tier_data), 1):
        ax.text(i, ax.get_ylim()[0] - 0.02, f"n={len(td)}", ha="center", fontsize=8, color="gray")

    plt.tight_layout()
    plt.savefig(out_dir / "figure_boxplot.png", dpi=150)
    plt.close()


def plot_heatmap(richness_df: pd.DataFrame, gap_dict_by_model: dict, out_dir: Path) -> None:
    """Heatmap: task richness tier x model family mean gap."""
    out_dir.mkdir(parents=True, exist_ok=True)
    # Build matrix: rows=tiers, cols=models
    models = list(gap_dict_by_model.keys())
    if not models:
        return
    matrix = np.full((4, len(models)), np.nan)
    for j, model in enumerate(models):
        model_gaps = gap_dict_by_model[model]
        for i, tier in enumerate([1, 2, 3, 4]):
            tids = richness_df[richness_df["tier"] == tier]["task_id"].tolist()
            vals = [model_gaps[t] for t in tids if t in model_gaps]
            if vals:
                matrix[i, j] = np.mean(vals)

    # Shorten model names
    short_models = [m.split("/")[-1][:20] for m in models]

    fig, ax = plt.subplots(figsize=(max(6, len(models) * 1.2), 4))
    im = ax.imshow(matrix, aspect="auto", cmap="YlOrRd", vmin=0, vmax=1)
    ax.set_xticks(range(len(models)))
    ax.set_xticklabels(short_models, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(4))
    ax.set_yticklabels([f"T{t}: {_TIER_LABELS[t]}" for t in [1, 2, 3, 4]], fontsize=10)
    ax.set_title("Mean Oracle Gap by Richness Tier × Model", fontsize=12)
    plt.colorbar(im, ax=ax, label="Mean Oracle Gap")

    # Annotate cells
    for i in range(4):
        for j in range(len(models)):
            val = matrix[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=7,
                        color="white" if val > 0.6 else "black")
    plt.tight_layout()
    plt.savefig(out_dir / "figure_heatmap.png", dpi=150)
    plt.close()


def plot_violin(richness_df: pd.DataFrame, gap_dict: dict, cu_dict: dict, out_dir: Path) -> None:
    """Violin: contract-unique failure mass by richness tier."""
    out_dir.mkdir(parents=True, exist_ok=True)
    df = richness_df.copy()
    df["cu_mass"] = df["task_id"].map(cu_dict)
    df = df.dropna(subset=["cu_mass"])

    fig, ax = plt.subplots(figsize=(7, 5))
    tier_data = {t: df[df["tier"] == t]["cu_mass"].tolist() for t in [1, 2, 3, 4]}
    positions = [1, 2, 3, 4]
    parts = ax.violinplot([tier_data[t] for t in [1, 2, 3, 4]], positions=positions, showmedians=True)
    for i, (pc, tier) in enumerate(zip(parts["bodies"], [1, 2, 3, 4])):
        pc.set_facecolor(_TIER_COLORS[tier])
        pc.set_alpha(0.7)
    parts["cmedians"].set_color("black")
    parts["cmedians"].set_linewidth(2)

    ax.set_xticks(positions)
    ax.set_xticklabels([f"T{t}: {_TIER_LABELS[t]}" for t in [1, 2, 3, 4]], fontsize=10)
    ax.set_ylabel("Contract-Unique Failure Mass", fontsize=12)
    ax.set_title("Contract-Unique Mass by Richness Tier", fontsize=13)
    plt.tight_layout()
    plt.savefig(out_dir / "figure_violin.png", dpi=150)
    plt.close()


def save_all(
    richness_df: pd.DataFrame,
    gap_dict: dict,
    gap_dict_by_model: dict,
    cu_dict: dict,
    results: dict,
    out_dir: Path,
) -> None:
    """Generate all 5 figures."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rho = results["rho"]
    p_exact = results.get("p_exact", 1.0)
    plot_gate_metrics(rho, 0.30, p_exact, out_dir)
    plot_scatter(richness_df, gap_dict, rho, out_dir)
    plot_boxplot(richness_df, gap_dict, out_dir)
    plot_heatmap(richness_df, gap_dict_by_model, out_dir)
    plot_violin(richness_df, gap_dict, cu_dict, out_dir)
    print(f"Figures saved to {out_dir}")
