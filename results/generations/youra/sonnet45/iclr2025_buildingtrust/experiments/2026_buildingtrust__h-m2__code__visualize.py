"""visualize.py — 5 required figures for H-M2 (A-9)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    FIG1_CONFIG, FIG2_CONFIG, FIG3_CONFIG, FIG4_CONFIG, FIG5_CONFIG,
    FIGURES_DIR, N_QUINTILES,
)


def save_figure(
    fig: plt.Figure,
    name: str,
    figures_dir: str,
    formats: tuple = ("pdf", "png"),
    dpi: int = 150,
) -> list:
    """Save figure in multiple formats.

    Args:
        fig:         matplotlib Figure
        name:        base filename (no extension)
        figures_dir: output directory
        formats:     tuple of format strings
        dpi:         dots per inch

    Returns:
        list of Path objects for saved files
    """
    os.makedirs(figures_dir, exist_ok=True)
    paths = []
    for fmt in formats:
        path = Path(figures_dir) / f"{name}.{fmt}"
        fig.savefig(str(path), dpi=dpi, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def plot_q1_variance_bar(
    results_per_dataset: dict,
    figures_dir: str = FIGURES_DIR,
) -> list:
    """Fig 1 (gate metric): bar chart DPO vs SFT Q1 variance per dataset with p-value annotation.

    Args:
        results_per_dataset: {dataset: {"dpo_q1_var": float, "sft_q1_var": float, "p_one_tailed": float}}
    Returns:
        list of Path objects for saved files (pdf + png)
    """
    cfg = FIG1_CONFIG
    datasets = list(results_per_dataset.keys())
    n_ds = len(datasets)
    x = np.arange(n_ds)
    width = 0.35

    fig, ax = plt.subplots(figsize=cfg["figsize"])
    dpo_vals = [results_per_dataset[d].get("dpo_q1_var", 0.0) for d in datasets]
    sft_vals = [results_per_dataset[d].get("sft_q1_var", 0.0) for d in datasets]
    p_vals   = [results_per_dataset[d].get("p_one_tailed", 1.0) for d in datasets]

    bars1 = ax.bar(x - width / 2, dpo_vals, width, label="DPO",
                   color=cfg["bar_colors"]["DPO"], alpha=0.85)
    bars2 = ax.bar(x + width / 2, sft_vals, width, label="SFT",
                   color=cfg["bar_colors"]["SFT"], alpha=0.85)

    # Annotate with p-values
    for i, (b1, b2, p) in enumerate(zip(bars1, bars2, p_vals)):
        sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
        y_top = max(b1.get_height(), b2.get_height())
        ax.text(i, y_top * 1.02, f"p={p:.3f}\n{sig}",
                ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels([d.upper() for d in datasets])
    ax.set_ylabel("Q1 KL-Residualized Delta Variance")
    ax.set_title("H-M2: DPO vs SFT Q1 Logit Delta Variance (KL-Residualized)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    return save_figure(fig, cfg["save_name"], figures_dir, dpi=cfg["dpi"])


def plot_quintile_trend(
    quintile_data: dict,
    figures_dir: str = FIGURES_DIR,
) -> list:
    """Fig 2: Q1-Q5 variance ratio line chart (DPO vs SFT) per dataset.

    Args:
        quintile_data: {dataset: {"dpo": np.ndarray(5,), "sft": np.ndarray(5,)}}
    """
    cfg = FIG2_CONFIG
    datasets = list(quintile_data.keys())
    quintile_labels = [f"Q{i+1}" for i in range(N_QUINTILES)]

    fig, axes = plt.subplots(1, len(datasets), figsize=cfg["figsize"], sharey=False)
    if len(datasets) == 1:
        axes = [axes]

    for ax, ds in zip(axes, datasets):
        dpo_v = quintile_data[ds]["dpo"]
        sft_v = quintile_data[ds]["sft"]
        ax.plot(quintile_labels, dpo_v, marker="o", label="DPO", color="steelblue")
        ax.plot(quintile_labels, sft_v, marker="s", label="SFT", color="darkorange")
        ax.set_title(ds.upper())
        ax.set_xlabel("Quintile (Q1=low margin)")
        ax.set_ylabel("KL-Residualized Variance")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    fig.suptitle("H-M2: Variance by Confidence Margin Quintile", fontsize=12)
    fig.tight_layout()
    return save_figure(fig, cfg["save_name"], figures_dir, dpi=cfg["dpi"])


def plot_kl_scatter(
    scatter_data: dict,
    figures_dir: str = FIGURES_DIR,
) -> list:
    """Fig 3: delta_var vs kl_div colored by quintile (validates residualization).

    Args:
        scatter_data: {pair_id: {"kl_div": (N,), "delta_var": (N,), "quintile_labels": (N,)}}
    """
    cfg = FIG3_CONFIG
    pair_ids = list(scatter_data.keys())
    n_pairs  = len(pair_ids)
    fig, axes = plt.subplots(1, n_pairs, figsize=cfg["figsize"])
    if n_pairs == 1:
        axes = [axes]

    cmap = plt.get_cmap(cfg["cmap"])

    for ax, pair_id in zip(axes, pair_ids):
        data   = scatter_data[pair_id]
        kl     = data["kl_div"]
        dv     = data["delta_var"]
        qlabel = data["quintile_labels"]

        sc = ax.scatter(kl, dv, c=qlabel, cmap=cmap, alpha=cfg["alpha"],
                        s=2, rasterized=True)
        plt.colorbar(sc, ax=ax, label="Quintile")
        ax.set_xlabel("KL Divergence KL(base||aligned)")
        ax.set_ylabel("Logit Delta Variance")
        ax.set_title(f"{pair_id}")
        ax.grid(alpha=0.3)

    fig.suptitle("H-M2: KL Divergence vs Delta Variance (colored by quintile)", fontsize=11)
    fig.tight_layout()
    return save_figure(fig, cfg["save_name"], figures_dir, dpi=cfg["dpi"])


def plot_benchmark_q1_grouped(
    benchmark_data: dict,
    figures_dir: str = FIGURES_DIR,
) -> list:
    """Fig 4: grouped bar MMLU/TQA/ARC × DPO/SFT with error bars.

    Args:
        benchmark_data: {dataset: {"dpo_q1_var": float, "sft_q1_var": float,
                                    "dpo_q1_std": float, "sft_q1_std": float}}
    """
    cfg = FIG4_CONFIG
    datasets = list(benchmark_data.keys())
    x     = np.arange(len(datasets))
    width = 0.35

    fig, ax = plt.subplots(figsize=cfg["figsize"])
    dpo_v   = [benchmark_data[d].get("dpo_q1_var", 0.0) for d in datasets]
    sft_v   = [benchmark_data[d].get("sft_q1_var", 0.0) for d in datasets]
    dpo_e   = [benchmark_data[d].get("dpo_q1_std", 0.0) for d in datasets]
    sft_e   = [benchmark_data[d].get("sft_q1_std", 0.0) for d in datasets]

    ax.bar(x - width / 2, dpo_v, width, yerr=dpo_e, label="DPO",
           color="steelblue", alpha=0.85, capsize=cfg["capsize"])
    ax.bar(x + width / 2, sft_v, width, yerr=sft_e, label="SFT",
           color="darkorange", alpha=0.85, capsize=cfg["capsize"])

    ax.set_xticks(x)
    ax.set_xticklabels([d.upper() for d in datasets])
    ax.set_ylabel("Q1 Variance (KL-Residualized)")
    ax.set_title("H-M2: Q1 Variance Comparison Across Benchmarks")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return save_figure(fig, cfg["save_name"], figures_dir, dpi=cfg["dpi"])


def plot_variance_ratio_heatmap(
    ratio_data: dict,
    figures_dir: str = FIGURES_DIR,
) -> list:
    """Fig 5: DPO/SFT variance ratio Q1-Q5 × dataset heatmap/line.

    Args:
        ratio_data: {dataset: np.ndarray(5,)} — DPO/SFT variance ratio per quintile
    """
    cfg = FIG5_CONFIG
    datasets = list(ratio_data.keys())
    matrix   = np.stack([ratio_data[d] for d in datasets], axis=0)  # (n_ds, 5)

    fig, ax = plt.subplots(figsize=cfg["figsize"])
    im = ax.imshow(
        matrix,
        aspect="auto",
        cmap=cfg["cmap"],
        vmin=0.5,
        vmax=max(2.0, float(np.nanmax(matrix))),
    )
    plt.colorbar(im, ax=ax, label="DPO/SFT Variance Ratio")

    ax.set_xticks(range(N_QUINTILES))
    ax.set_xticklabels([f"Q{i+1}" for i in range(N_QUINTILES)])
    ax.set_yticks(range(len(datasets)))
    ax.set_yticklabels([d.upper() for d in datasets])
    ax.set_xlabel("Quintile (Q1 = low margin)")
    ax.set_title("H-M2: DPO/SFT Variance Ratio per Quintile × Dataset")

    # Add value annotations
    for i in range(len(datasets)):
        for j in range(N_QUINTILES):
            ax.text(j, i, f"{matrix[i, j]:.2f}",
                    ha="center", va="center", fontsize=7, color="black")

    fig.tight_layout()
    return save_figure(fig, cfg["save_name"], figures_dir, dpi=cfg["dpi"])
