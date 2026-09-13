"""Visualization: 6 required figures for H-E1."""
import logging
import os

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import numpy as np
import pandas as pd
import seaborn as sns

from config import CONFIG

logger = logging.getLogger(__name__)


def plot_bar_factorial(df: pd.DataFrame, output_dir: str) -> None:
    """MMLU + HellaSwag by Scale × PPL-threshold, error bars over seeds."""
    os.makedirs(output_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, metric, title in zip(
        axes,
        ["mmlu_4shot", "hellaswag_0shot"],
        ["MMLU 4-shot", "HellaSwag 0-shot"],
    ):
        summary = (
            df.groupby(["scale", "ppl_threshold"])[metric]
            .agg(["mean", "std"])
            .reset_index()
        )
        x = np.arange(len(summary["ppl_threshold"].unique()))
        width = 0.35
        scales = sorted(summary["scale"].unique())
        for i, scale in enumerate(scales):
            sub = summary[summary["scale"] == scale].sort_values("ppl_threshold")
            ax.bar(
                x + i * width - width / 2,
                sub["mean"],
                width,
                yerr=sub["std"],
                label=f"{scale}M",
                capsize=4,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(sorted(summary["ppl_threshold"].unique()))
        ax.set_xlabel("PPL Threshold (τ)")
        ax.set_ylabel("Accuracy")
        ax.set_title(title)
        ax.legend()
    plt.suptitle("H-E1: Scale × Curation Interaction")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "bar_factorial.png"), dpi=150)
    plt.close()


def plot_interaction(df: pd.DataFrame, output_dir: str) -> None:
    """Line plot: score vs τ, separate lines per scale."""
    os.makedirs(output_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, metric, title in zip(
        axes, ["mmlu_4shot", "hellaswag_0shot"], ["MMLU 4-shot", "HellaSwag 0-shot"]
    ):
        summary = df.groupby(["scale", "ppl_threshold"])[metric].mean().reset_index()
        for scale in sorted(df["scale"].unique()):
            sub = summary[summary["scale"] == scale].sort_values("ppl_threshold")
            ax.plot(sub["ppl_threshold"], sub[metric], marker="o", label=f"{scale}M")
        ax.set_xlabel("PPL Threshold (τ)")
        ax.set_ylabel("Mean Accuracy")
        ax.set_title(f"Scale × PPL Interaction: {title}")
        ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "interaction_plot.png"), dpi=150)
    plt.close()


def plot_dedup_interaction(df: pd.DataFrame, output_dir: str) -> None:
    """Dedup effect (J=0.7 vs J=0.9) by scale."""
    os.makedirs(output_dir, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, metric, title in zip(
        axes, ["mmlu_4shot", "hellaswag_0shot"], ["MMLU 4-shot", "HellaSwag 0-shot"]
    ):
        summary = df.groupby(["scale", "dedup_j"])[metric].mean().reset_index()
        for scale in sorted(df["scale"].unique()):
            sub = summary[summary["scale"] == scale].sort_values("dedup_j")
            ax.plot(sub["dedup_j"], sub[metric], marker="s", label=f"{scale}M")
        ax.set_xlabel("Dedup Jaccard Threshold")
        ax.set_ylabel("Mean Accuracy")
        ax.set_title(f"Scale × Dedup Interaction: {title}")
        ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "dedup_interaction.png"), dpi=150)
    plt.close()


def plot_fineweb_replication(df: pd.DataFrame, output_dir: str) -> None:
    """Side-by-side Dolma vs FineWeb interaction plots."""
    os.makedirs(output_dir, exist_ok=True)
    corpora = sorted(df["corpus"].unique())
    fig, axes = plt.subplots(1, max(len(corpora), 1), figsize=(8 * len(corpora), 5))
    if len(corpora) == 1:
        axes = [axes]
    for ax, corpus in zip(axes, corpora):
        sub_df = df[df["corpus"] == corpus]
        summary = sub_df.groupby(["scale", "ppl_threshold"])["mmlu_4shot"].mean().reset_index()
        for scale in sorted(sub_df["scale"].unique()):
            s = summary[summary["scale"] == scale].sort_values("ppl_threshold")
            ax.plot(s["ppl_threshold"], s["mmlu_4shot"], marker="o", label=f"{scale}M")
        ax.set_title(f"{corpus.capitalize()}: Scale × PPL")
        ax.set_xlabel("PPL Threshold")
        ax.set_ylabel("MMLU 4-shot")
        ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fineweb_replication.png"), dpi=150)
    plt.close()


def plot_corpus_size_heatmap(variant_metadata: list, output_dir: str) -> None:
    """Token count per filter condition."""
    os.makedirs(output_dir, exist_ok=True)
    if not variant_metadata:
        return
    df = pd.DataFrame(variant_metadata)
    if "token_count" not in df.columns:
        return
    pivot = df.pivot_table(
        values="token_count",
        index="ppl_threshold",
        columns="dedup_j",
        aggfunc="mean",
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(pivot, annot=True, fmt=".2e", cmap="YlOrRd", ax=ax)
    ax.set_title("Token Count by PPL Threshold × Dedup J")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "corpus_size_heatmap.png"), dpi=150)
    plt.close()


def plot_contamination_table(variant_metadata: list, output_dir: str) -> None:
    """CR per corpus variant."""
    os.makedirs(output_dir, exist_ok=True)
    if not variant_metadata:
        return
    df = pd.DataFrame(variant_metadata)
    if "contamination_rate" not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis("off")
    table_data = df[["condition", "corpus", "ppl_threshold", "dedup_j", "contamination_rate"]].values.tolist()
    col_labels = ["Condition", "Corpus", "PPL τ", "Dedup J", "CR"]
    tbl = ax.table(cellText=table_data, colLabels=col_labels, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    ax.set_title("Contamination Rate per Corpus Variant", pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "contamination_table.png"), dpi=150, bbox_inches="tight")
    plt.close()


def generate_all_figures(
    df: pd.DataFrame,
    variant_metadata: list,
    output_dir: str,
) -> None:
    """Generate all 6 figures."""
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Generating figures in {output_dir}")
    plot_bar_factorial(df, output_dir)
    plot_interaction(df, output_dir)
    plot_dedup_interaction(df, output_dir)
    plot_fineweb_replication(df, output_dir)
    plot_corpus_size_heatmap(variant_metadata, output_dir)
    plot_contamination_table(variant_metadata, output_dir)
    logger.info("All figures generated.")
