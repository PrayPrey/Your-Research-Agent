"""Visualization utilities for H-M1 experiment.

5-figure visualization suite:
fig1: 6-encoder Delta_rho bar chart with gate threshold line
fig2: Delta_rho vs severity multi-line (6 encoders)
fig3: Delta_R2 mediation analysis bar chart
fig4: Spearman rho heatmap 6x4 (encoder x severity)
fig5: Bootstrap distribution comparison NFT vs flat-MLP
"""
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import ENCODER_NAMES, VizConfig

logger = logging.getLogger(__name__)


def _setup_style(viz_cfg: VizConfig) -> None:
    """Apply matplotlib style."""
    try:
        plt.style.use(viz_cfg.style)
    except Exception:
        plt.style.use("default")


def generate_all_figures(
    eval_df: pd.DataFrame,
    delta_r2: float,
    encoder_stats: dict,
    bootstrap_data: dict,
    viz_cfg: VizConfig = None,
) -> list:
    """Generate all 5 required figures and return list of saved paths.

    Parameters
    ----------
    eval_df : pd.DataFrame
        Output from evaluate_all_encoders().
    delta_r2 : float
        Mediation Delta_R2 value.
    encoder_stats : dict
        Output from summarize_encoder_stats().
    bootstrap_data : dict
        {"nft_bootstrap": np.ndarray, "flat_bootstrap": np.ndarray}
    viz_cfg : VizConfig (optional)

    Returns
    -------
    list[str]
        Paths to all generated figure files.
    """
    if viz_cfg is None:
        viz_cfg = VizConfig()

    os.makedirs(viz_cfg.figures_dir, exist_ok=True)
    _setup_style(viz_cfg)

    saved_paths = []

    # fig1
    p = _plot_delta_rho_bar(eval_df, viz_cfg)
    saved_paths.append(p)

    # fig2
    p = _plot_delta_rho_curves(eval_df, viz_cfg)
    saved_paths.append(p)

    # fig3
    p = _plot_mediation_bar(eval_df, delta_r2, viz_cfg)
    saved_paths.append(p)

    # fig4
    p = _plot_rho_heatmap(eval_df, viz_cfg)
    saved_paths.append(p)

    # fig5
    p = _plot_bootstrap_dist(bootstrap_data, viz_cfg)
    saved_paths.append(p)

    logger.info(f"Generated {len(saved_paths)} figures in {viz_cfg.figures_dir}")
    return saved_paths


def _plot_delta_rho_bar(eval_df: pd.DataFrame, viz_cfg: VizConfig) -> str:
    """fig1: 6-encoder Delta_rho bar chart at severity=1.0."""
    s1_df = eval_df[eval_df["severity"] == 1.0]
    mean_dr = s1_df.groupby("encoder")["delta_rho"].mean()

    # Preserve ENCODER_NAMES order
    encoders = [e for e in ENCODER_NAMES if e in mean_dr.index]
    values = [mean_dr[e] for e in encoders]

    fig, ax = plt.subplots(figsize=viz_cfg.bar_figsize)
    colors = plt.cm.get_cmap(viz_cfg.palette)(np.linspace(0, 1, len(encoders)))
    ax.bar(encoders, values, color=colors)
    ax.axhline(
        y=0.02,
        color=viz_cfg.gate_line_color,
        linestyle=viz_cfg.gate_line_style,
        alpha=viz_cfg.gate_line_alpha,
        label="Gate threshold (0.02)"
    )
    ax.set_xlabel("Encoder")
    ax.set_ylabel("Delta_rho (s=0 to s=1.0)")
    ax.set_title("H-M1: 6-Encoder Permutation Robustness (Delta_rho at severity=1.0)")
    ax.legend()
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    save_path = os.path.join(viz_cfg.figures_dir, viz_cfg.fig1_name)
    fig.savefig(save_path, dpi=viz_cfg.dpi, format=viz_cfg.fig_format)
    plt.close(fig)
    logger.info(f"fig1 saved: {save_path}")
    return save_path


def _plot_delta_rho_curves(eval_df: pd.DataFrame, viz_cfg: VizConfig) -> str:
    """fig2: Delta_rho vs severity for all 6 encoders."""
    mean_df = eval_df.groupby(["encoder", "severity"])["delta_rho"].mean().reset_index()

    fig, ax = plt.subplots(figsize=viz_cfg.curve_figsize)
    colors = plt.cm.get_cmap(viz_cfg.palette)(np.linspace(0, 1, len(ENCODER_NAMES)))

    for i, enc_name in enumerate(ENCODER_NAMES):
        enc_df = mean_df[mean_df["encoder"] == enc_name].sort_values("severity")
        if len(enc_df) > 0:
            ax.plot(enc_df["severity"], enc_df["delta_rho"], marker="o",
                    label=enc_name, color=colors[i])

    ax.axhline(
        y=0.02,
        color=viz_cfg.gate_line_color,
        linestyle=viz_cfg.gate_line_style,
        alpha=viz_cfg.gate_line_alpha,
        label="Gate threshold (0.02)"
    )
    ax.set_xlabel("Permutation Severity")
    ax.set_ylabel("Delta_rho")
    ax.set_title("H-M1: Delta_rho vs Permutation Severity (6 Encoders)")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()

    save_path = os.path.join(viz_cfg.figures_dir, viz_cfg.fig2_name)
    fig.savefig(save_path, dpi=viz_cfg.dpi, format=viz_cfg.fig_format)
    plt.close(fig)
    logger.info(f"fig2 saved: {save_path}")
    return save_path


def _plot_mediation_bar(eval_df: pd.DataFrame, delta_r2: float, viz_cfg: VizConfig) -> str:
    """fig3: Mediation Delta_R2 bar chart."""
    s0_df = eval_df[eval_df["severity"] == 0.0]
    mean_rho = s0_df.groupby("encoder")["rho"].mean()

    encoders = [e for e in ENCODER_NAMES if e in mean_rho.index]
    r2_values = [float(mean_rho[e] ** 2) for e in encoders]

    fig, ax = plt.subplots(figsize=viz_cfg.mediation_figsize)
    colors = plt.cm.get_cmap(viz_cfg.palette)(np.linspace(0, 1, len(encoders)))
    ax.bar(encoders, r2_values, color=colors)
    ax.set_xlabel("Encoder")
    ax.set_ylabel("R2 (rho^2 at severity=0)")
    ax.set_title(f"H-M1: Mediation Analysis — Delta_R2 = {delta_r2:.4f}")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()

    save_path = os.path.join(viz_cfg.figures_dir, viz_cfg.fig3_name)
    fig.savefig(save_path, dpi=viz_cfg.dpi, format=viz_cfg.fig_format)
    plt.close(fig)
    logger.info(f"fig3 saved: {save_path}")
    return save_path


def _plot_rho_heatmap(eval_df: pd.DataFrame, viz_cfg: VizConfig) -> str:
    """fig4: Spearman rho heatmap 6 encoders x 4 severity levels."""
    pivot = eval_df.groupby(["encoder", "severity"])["rho"].mean().unstack()

    # Reorder rows to ENCODER_NAMES order
    ordered_rows = [e for e in ENCODER_NAMES if e in pivot.index]
    pivot = pivot.reindex(ordered_rows)

    fig, ax = plt.subplots(figsize=viz_cfg.heatmap_figsize)
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="coolwarm",
        annot=True,
        fmt=".3f",
        vmin=0,
        vmax=1,
        cbar_kws={"label": "Spearman rho"},
    )
    ax.set_title("H-M1: Spearman rho Heatmap (Encoder x Severity)")
    ax.set_xlabel("Permutation Severity")
    ax.set_ylabel("Encoder")
    plt.tight_layout()

    save_path = os.path.join(viz_cfg.figures_dir, viz_cfg.fig4_name)
    fig.savefig(save_path, dpi=viz_cfg.dpi, format=viz_cfg.fig_format)
    plt.close(fig)
    logger.info(f"fig4 saved: {save_path}")
    return save_path


def _plot_bootstrap_dist(bootstrap_data: dict, viz_cfg: VizConfig) -> str:
    """fig5: Bootstrap distribution comparison NFT-base vs flat-MLP."""
    nft_bs = bootstrap_data.get("nft_bootstrap", np.array([]))
    flat_bs = bootstrap_data.get("flat_bootstrap", np.array([]))

    fig, ax = plt.subplots(figsize=viz_cfg.bootstrap_figsize)

    if len(nft_bs) > 0:
        ax.hist(nft_bs, bins=50, alpha=0.6, label="NFT-base", color="blue", density=True)
    if len(flat_bs) > 0:
        ax.hist(flat_bs, bins=50, alpha=0.6, label="flat-MLP", color="orange", density=True)

    ax.axvline(x=0, color="black", linestyle="--", alpha=0.5, label="delta_rho=0")
    ax.set_xlabel("Bootstrap Delta_rho")
    ax.set_ylabel("Density")
    ax.set_title("H-M1: Bootstrap Distribution of Delta_rho (NFT-base vs flat-MLP)")
    ax.legend()
    plt.tight_layout()

    save_path = os.path.join(viz_cfg.figures_dir, viz_cfg.fig5_name)
    fig.savefig(save_path, dpi=viz_cfg.dpi, format=viz_cfg.fig_format)
    plt.close(fig)
    logger.info(f"fig5 saved: {save_path}")
    return save_path
