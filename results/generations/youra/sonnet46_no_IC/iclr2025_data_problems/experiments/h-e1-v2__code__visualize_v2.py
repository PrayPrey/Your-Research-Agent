"""Visualization for h-e1-v2: bar charts, heatmap, learning curves, interaction plots."""
import os
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


def generate_all_figures_v2(df: pd.DataFrame, figures_dir: str) -> list:
    """Generate all h-e1-v2 figures. Returns list of saved figure paths."""
    os.makedirs(figures_dir, exist_ok=True)
    saved = []

    # Validate required columns
    required = {"scale", "ppl_threshold", "dedup_j", "hellaswag_acc_norm"}
    missing = required - set(df.columns)
    if missing:
        logger.warning(f"Missing columns for visualization: {missing}")
        # Add placeholder if needed
        for col in missing:
            df[col] = 0.0

    # Fig 1: Bar chart — HellaSwag acc_norm by Scale x PPL-threshold x Dedup-J
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, scale in zip(axes, [14, 31]):
        df_s = df[df["scale"] == scale]
        if df_s.empty:
            ax.set_title(f"{scale}M (no data)")
            continue
        pivot = df_s.groupby(["ppl_threshold", "dedup_j"])["hellaswag_acc_norm"].mean().reset_index()
        x = np.arange(len(pivot["ppl_threshold"].unique()))
        width = 0.35
        ppl_vals = sorted(pivot["ppl_threshold"].unique())
        j_vals = sorted(pivot["dedup_j"].unique())
        for i, j in enumerate(j_vals):
            sub = pivot[pivot["dedup_j"] == j]
            means = [sub[sub["ppl_threshold"] == t]["hellaswag_acc_norm"].mean() for t in ppl_vals]
            ax.bar(x + i * width, means, width, label=f"J={j}")
        ax.set_xticks(x + width / 2)
        ax.set_xticklabels([f"τ={t}" for t in ppl_vals])
        ax.set_title(f"{scale}M: HellaSwag acc_norm by PPL threshold & Dedup-J")
        ax.set_ylabel("HellaSwag acc_norm")
        ax.legend()
        ax.set_ylim(0, 1)
    plt.suptitle("h-e1-v2: Scale × Curation Interaction")
    plt.tight_layout()
    p = os.path.join(figures_dir, "fig1_bar_scale_curation.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p)
    logger.info(f"Saved {p}")

    # Fig 2: Interaction heatmap — 2x3x2 grid
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, scale in zip(axes, [14, 31]):
        df_s = df[df["scale"] == scale]
        if df_s.empty:
            ax.set_title(f"{scale}M (no data)")
            continue
        pivot = df_s.groupby(["ppl_threshold", "dedup_j"])["hellaswag_acc_norm"].mean().unstack("dedup_j")
        sns.heatmap(
            pivot, ax=ax, annot=True, fmt=".3f", cmap="YlOrRd",
            vmin=0.25, vmax=0.5,
            xticklabels=[f"J={j}" for j in pivot.columns],
            yticklabels=[f"τ={t}" for t in pivot.index],
        )
        ax.set_title(f"{scale}M: Mean HellaSwag acc_norm")
        ax.set_xlabel("Dedup-J")
        ax.set_ylabel("PPL threshold")
    plt.suptitle("h-e1-v2: Interaction Heatmap (Scale × PPL × J)")
    plt.tight_layout()
    p = os.path.join(figures_dir, "fig2_interaction_heatmap.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p)
    logger.info(f"Saved {p}")

    # Fig 3: Learning curves — acc_norm at checkpoints
    if "checkpoint_tokens" in df.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = plt.cm.tab10(np.linspace(0, 1, 6))
        for idx, (cond_id, g) in enumerate(df.groupby(["ppl_threshold", "dedup_j"])):
            ppl, j = cond_id
            for scale in [14, 31]:
                sub = g[g["scale"] == scale].groupby("checkpoint_tokens")["hellaswag_acc_norm"].mean()
                linestyle = "-" if scale == 14 else "--"
                ax.plot(
                    sub.index / 1e6, sub.values,
                    label=f"τ={ppl},J={j},{scale}M",
                    linestyle=linestyle,
                    color=colors[idx % len(colors)],
                    alpha=0.8,
                )
        ax.set_xlabel("Tokens seen (M)")
        ax.set_ylabel("HellaSwag acc_norm")
        ax.set_title("h-e1-v2: Learning Curves by Condition")
        ax.legend(fontsize=7, ncol=3)
        plt.tight_layout()
        p = os.path.join(figures_dir, "fig3_learning_curves.png")
        plt.savefig(p, dpi=150, bbox_inches="tight")
        plt.close()
        saved.append(p)
        logger.info(f"Saved {p}")

    # Fig 4: Interaction plot — PPL threshold vs acc_norm, lines for 14M vs 31M, panels for J
    j_vals = sorted(df["dedup_j"].unique())
    fig, axes = plt.subplots(1, len(j_vals), figsize=(7 * len(j_vals), 5), sharey=True)
    if len(j_vals) == 1:
        axes = [axes]
    for ax, j in zip(axes, j_vals):
        df_j = df[df["dedup_j"] == j]
        for scale, marker in zip([14, 31], ["o-", "s--"]):
            sub = df_j[df_j["scale"] == scale].groupby("ppl_threshold")["hellaswag_acc_norm"].mean()
            ax.plot(sub.index, sub.values, marker, label=f"{scale}M", markersize=8, linewidth=2)
        ax.set_xlabel("PPL threshold (τ)")
        ax.set_ylabel("HellaSwag acc_norm")
        ax.set_title(f"Dedup J={j}")
        ax.legend()
        ax.set_xticks(sorted(df["ppl_threshold"].unique()))
    plt.suptitle("h-e1-v2: Interaction Plot (PPL threshold vs acc_norm by Scale)")
    plt.tight_layout()
    p = os.path.join(figures_dir, "fig4_interaction_plot.png")
    plt.savefig(p, dpi=150, bbox_inches="tight")
    plt.close()
    saved.append(p)
    logger.info(f"Saved {p}")

    logger.info(f"Generated {len(saved)} figures in {figures_dir}")
    return saved
