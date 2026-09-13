"""H-M2 visualization: 6 required figures."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

PALETTE = {"high": "#2196F3", "low": "#F44336"}
DPI = 150


def fig1_gate_metrics(results: dict, figures_dir: str):
    """p-value vs 0.05 threshold, beta vs 0.10."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    p_val = results.get("primary_mwu_matched", {}).get("p_value", 1.0)
    beta = results.get("ols_standardized", {}).get("accessible_beta", 0.0)

    axes[0].bar(["MWU p-value"], [p_val], color=PALETTE["high"])
    axes[0].axhline(0.05, color="red", linestyle="--", label="alpha=0.05")
    axes[0].set_title("Primary: MWU p-value")
    axes[0].legend()

    axes[1].bar(["Accessible beta"], [abs(beta)], color=PALETTE["high"])
    axes[1].axhline(0.10, color="red", linestyle="--", label="beta gate=0.10")
    axes[1].set_title("Secondary: Standardized Beta")
    axes[1].legend()

    plt.tight_layout()
    path = os.path.join(figures_dir, "fig1_gate_metrics.png")
    plt.savefig(path, dpi=DPI)
    plt.close()
    logger.info(f"Saved {path}")


def fig2_boxplot_12m_counts(matched_df: pd.DataFrame, figures_dir: str):
    """Boxplot high vs low Accessible run counts."""
    fig, ax = plt.subplots(figsize=(6, 5))
    matched_df["group"] = matched_df["high_accessible"].map({1: "High Accessible", 0: "Low Accessible"})
    sns.boxplot(data=matched_df, x="group", y="run_count_12m", palette=[PALETTE["high"], PALETTE["low"]], ax=ax)
    ax.set_title("12-Month Run Counts by Accessible Group")
    ax.set_xlabel("")
    ax.set_ylabel("Run Count (12 months)")
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig2_boxplot_12m_counts.png")
    plt.savefig(path, dpi=DPI)
    plt.close()
    logger.info(f"Saved {path}")


def fig3_ps_distribution(df: pd.DataFrame, figures_dir: str):
    """Propensity score distribution."""
    fig, ax = plt.subplots(figsize=(7, 4))
    if "propensity_score" in df.columns:
        high = df[df["high_accessible"] == 1]["propensity_score"]
        low = df[df["high_accessible"] == 0]["propensity_score"]
        ax.hist(high, bins=30, alpha=0.6, label="High Accessible", color=PALETTE["high"])
        ax.hist(low, bins=30, alpha=0.6, label="Low Accessible", color=PALETTE["low"])
        ax.legend()
    ax.set_title("Propensity Score Distribution")
    ax.set_xlabel("Propensity Score")
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig3_ps_distribution.png")
    plt.savefig(path, dpi=DPI)
    plt.close()
    logger.info(f"Saved {path}")


def fig4_love_plot(smd_df: pd.DataFrame, figures_dir: str):
    """SMD before/after matching."""
    fig, ax = plt.subplots(figsize=(7, 5))
    if len(smd_df) > 0:
        y_pos = range(len(smd_df))
        ax.scatter(smd_df["smd_before"], y_pos, marker="o", label="Before", color=PALETTE["low"])
        ax.scatter(smd_df["smd_after"], y_pos, marker="s", label="After", color=PALETTE["high"])
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(smd_df["covariate"])
        ax.axvline(0.1, color="gray", linestyle="--", label="SMD=0.1")
        ax.legend()
    ax.set_title("Love Plot: SMD Before/After Matching")
    ax.set_xlabel("Standardized Mean Difference")
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig4_love_plot.png")
    plt.savefig(path, dpi=DPI)
    plt.close()
    logger.info(f"Saved {path}")


def fig5_ols_coefficients(ols_results: dict, figures_dir: str):
    """Standardized beta forest plot."""
    fig, ax = plt.subplots(figsize=(8, 6))
    params = ols_results.get("params", {})
    params = {k: v for k, v in params.items() if k != "const"}
    if params:
        names = list(params.keys())
        values = [params[n] for n in names]
        y_pos = range(len(names))
        ax.barh(list(y_pos), values, color=PALETTE["high"])
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(names)
        ax.axvline(0, color="black", linewidth=0.5)
        ax.axvline(0.10, color="red", linestyle="--", label="beta gate=0.10")
        ax.axvline(-0.10, color="red", linestyle="--")
        ax.legend()
    ax.set_title("OLS Standardized Coefficients")
    ax.set_xlabel("Standardized Beta")
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig5_ols_coefficients.png")
    plt.savefig(path, dpi=DPI)
    plt.close()
    logger.info(f"Saved {path}")


def fig6_window_sensitivity(results_6m: dict, results_12m: dict, figures_dir: str):
    """6m vs 12m window p-value comparison."""
    fig, ax = plt.subplots(figsize=(6, 4))
    windows = ["6 months", "12 months"]
    p_values = [
        results_6m.get("p_value", 1.0) if results_6m else 1.0,
        results_12m.get("p_value", 1.0) if results_12m else 1.0,
    ]
    ax.bar(windows, p_values, color=[PALETTE["low"], PALETTE["high"]])
    ax.axhline(0.05, color="red", linestyle="--", label="alpha=0.05")
    ax.set_title("Window Sensitivity: MWU p-value")
    ax.set_ylabel("p-value")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(figures_dir, "fig6_window_sensitivity.png")
    plt.savefig(path, dpi=DPI)
    plt.close()
    logger.info(f"Saved {path}")


def generate_all_figures(results: dict, matched_df: pd.DataFrame, analysis_df: pd.DataFrame,
                         smd_df: pd.DataFrame, ols_results: dict, results_6m: dict, figures_dir: str):
    """Generate all 6 figures."""
    os.makedirs(figures_dir, exist_ok=True)
    fig1_gate_metrics(results, figures_dir)
    fig2_boxplot_12m_counts(matched_df, figures_dir)
    fig3_ps_distribution(analysis_df, figures_dir)
    fig4_love_plot(smd_df, figures_dir)
    fig5_ols_coefficients(ols_results, figures_dir)
    fig6_window_sensitivity(results_6m, results.get("primary_mwu_matched", {}), figures_dir)
    logger.info(f"All 6 figures saved to {figures_dir}")
