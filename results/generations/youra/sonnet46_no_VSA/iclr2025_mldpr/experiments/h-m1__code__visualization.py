import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter

from config import CoxConfig, FigureConfig
from cox_analysis import LRTResult


def _figures_dir(cfg: CoxConfig) -> Path:
    # figures_dir may be relative; resolve from project root (two levels up from code/)
    p = Path(cfg.figures_dir)
    if not p.is_absolute():
        code_dir = Path(__file__).parent
        p = code_dir.parent.parent.parent.parent / cfg.figures_dir
    p.mkdir(parents=True, exist_ok=True)
    return p


def plot_gate_metrics(result: LRTResult, cfg: CoxConfig, fig_cfg: FigureConfig) -> str:
    """Fig 1: bar chart p_value vs 0.05, |HR-1| vs 0.10 thresholds."""
    fdir = _figures_dir(cfg)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=fig_cfg.dpi)

    metrics = ["LRT p-value", "|HR-1|"]
    values = [result.p_value, result.abs_effect]
    thresholds = [cfg.p_threshold, cfg.hr_effect_threshold]

    # Color bars based on pass condition
    colors = []
    for v, t, is_lower_better in zip(values, thresholds, [True, False]):
        if is_lower_better:
            colors.append(fig_cfg.color_pass if v < t else fig_cfg.color_fail)
        else:
            colors.append(fig_cfg.color_pass if v >= t else fig_cfg.color_fail)

    x = np.arange(len(metrics))
    bars = ax.bar(x, values, color=colors, alpha=0.8, width=0.5)
    for bar, thr, name in zip(bars, thresholds, ["p < 0.05", "|HR-1| ≥ 0.10"]):
        ax.axhline(y=thr, color="black", linestyle="--", linewidth=1.2, alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=12)
    ax.set_ylabel("Value", fontsize=11)
    ax.set_title(
        f"H-M1 Gate Metrics | Gate: {'PASS' if result.gate_passed else 'FAIL (meaningful null)'}",
        fontsize=12, fontweight="bold"
    )
    gate_str = "PASS" if result.gate_passed else "FAIL"
    ax.text(0.98, 0.95, f"Gate: {gate_str}", transform=ax.transAxes,
            ha="right", va="top", fontsize=11,
            color=fig_cfg.color_pass if result.gate_passed else fig_cfg.color_fail,
            fontweight="bold")
    plt.tight_layout()
    out = str(fdir / "gate_metrics.png")
    plt.savefig(out, dpi=fig_cfg.dpi)
    plt.close()
    print(f"Saved: {out}")
    return out


def plot_km_quartiles(panel_df: pd.DataFrame, cfg: CoxConfig, fig_cfg: FigureConfig) -> str:
    """Fig 2: KM curves Q1 vs Q4 of log_unique_paper_count_at_intro."""
    fdir = _figures_dir(cfg)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=fig_cfg.dpi)

    q1_thresh = panel_df[cfg.km_col].quantile(0.25)
    q4_thresh = panel_df[cfg.km_col].quantile(0.75)

    q1_df = panel_df[panel_df[cfg.km_col] <= q1_thresh]
    q4_df = panel_df[panel_df[cfg.km_col] >= q4_thresh]

    kmf1 = KaplanMeierFitter()
    kmf4 = KaplanMeierFitter()

    kmf1.fit(q1_df[cfg.duration_col], event_observed=q1_df[cfg.event_col], label="Q1 (low diversity)")
    kmf4.fit(q4_df[cfg.duration_col], event_observed=q4_df[cfg.event_col], label="Q4 (high diversity)")

    kmf1.plot_survival_function(ax=ax, ci_show=True, color=fig_cfg.color_fail)
    kmf4.plot_survival_function(ax=ax, ci_show=True, color=fig_cfg.color_pass)

    ax.set_xlabel("Duration (years)", fontsize=11)
    ax.set_ylabel("Survival Probability", fontsize=11)
    ax.set_title("Kaplan-Meier by Diversity Quartile (Q1 vs Q4)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    plt.tight_layout()
    out = str(fdir / "km_quartiles.png")
    plt.savefig(out, dpi=fig_cfg.dpi)
    plt.close()
    print(f"Saved: {out}")
    return out


def plot_partial_effects(
    M1: CoxPHFitter, panel_df: pd.DataFrame, cfg: CoxConfig, fig_cfg: FigureConfig
) -> str:
    """Fig 3: partial effects on outcome across diversity z-score values."""
    fdir = _figures_dir(cfg)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=fig_cfg.dpi)
    try:
        M1.plot_partial_effects_on_outcome(
            cfg.diversity_col, values=[-2, -1, 0, 1, 2],
            plot_baseline=False, ax=ax
        )
        ax.set_title("Partial Effects on Survival by Diversity Level", fontsize=12, fontweight="bold")
        ax.set_xlabel("Duration (years)", fontsize=11)
    except Exception as e:
        ax.text(0.5, 0.5, f"Partial effects unavailable:\n{e}", ha="center", va="center",
                transform=ax.transAxes, fontsize=10)
        ax.set_title("Partial Effects (error — see log)", fontsize=11)
    plt.tight_layout()
    out = str(fdir / "partial_effects.png")
    plt.savefig(out, dpi=fig_cfg.dpi)
    plt.close()
    print(f"Saved: {out}")
    return out


def plot_forest(M1: CoxPHFitter, cfg: CoxConfig, fig_cfg: FigureConfig) -> str:
    """Fig 4: Forest plot — HR with 95% CI for all M1 covariates."""
    fdir = _figures_dir(cfg)

    hrs = M1.hazard_ratios_
    ci_log = M1.confidence_intervals_
    ci_cols = list(ci_log.columns)
    lower_col = next((c for c in ci_cols if "lower" in c.lower()), ci_cols[0])
    upper_col = next((c for c in ci_cols if "upper" in c.lower()), ci_cols[1])
    ci_lower = np.exp(ci_log[lower_col])
    ci_upper = np.exp(ci_log[upper_col])
    p_vals = M1.summary["p"]

    covariates = list(hrs.index)
    y_pos = np.arange(len(covariates))

    fig, ax = plt.subplots(figsize=(9, max(4, len(covariates) * 0.8)), dpi=fig_cfg.dpi)

    for i, cov in enumerate(covariates):
        hr = float(hrs[cov])
        lo = float(ci_lower[cov])
        hi = float(ci_upper[cov])
        p = float(p_vals[cov])
        color = fig_cfg.color_pass if p < 0.05 else fig_cfg.color_neutral
        ax.errorbar(hr, i, xerr=[[hr - lo], [hi - hr]], fmt="o",
                    color=color, capsize=4, markersize=7)
        ax.text(hi + 0.01, i, f"p={p:.3f}", va="center", fontsize=8)

    ax.axvline(x=1.0, color="black", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(covariates, fontsize=10)
    ax.set_xlabel("Hazard Ratio (95% CI)", fontsize=11)
    ax.set_title("Forest Plot: M1 Covariates", fontsize=12, fontweight="bold")

    # Legend
    from matplotlib.lines import Line2D
    legend_els = [
        Line2D([0], [0], marker="o", color=fig_cfg.color_pass, label="p < 0.05", markersize=7),
        Line2D([0], [0], marker="o", color=fig_cfg.color_neutral, label="p ≥ 0.05", markersize=7),
    ]
    ax.legend(handles=legend_els, fontsize=9)
    plt.tight_layout()
    out = str(fdir / "forest_plot.png")
    plt.savefig(out, dpi=fig_cfg.dpi)
    plt.close()
    print(f"Saved: {out}")
    return out


def plot_schoenfeld(
    M1: CoxPHFitter, panel_df: pd.DataFrame, cfg: CoxConfig, fig_cfg: FigureConfig
) -> str:
    """Fig 5: Schoenfeld residuals / PH assumption check."""
    fdir = _figures_dir(cfg)
    try:
        ax = M1.check_assumptions(panel_df, p_value_threshold=0.05, show_plots=True)
        fig = plt.gcf()
        fig.suptitle("Schoenfeld Residuals — PH Assumption Check", fontsize=11, fontweight="bold")
        plt.tight_layout()
    except Exception as e:
        fig, ax_fallback = plt.subplots(figsize=(7, 4), dpi=fig_cfg.dpi)
        ax_fallback.text(0.5, 0.5, f"Schoenfeld test unavailable:\n{e}",
                         ha="center", va="center", transform=ax_fallback.transAxes, fontsize=10)
        ax_fallback.set_title("Schoenfeld Residuals (error — see log)", fontsize=11)
    out = str(fdir / "schoenfeld_residuals.png")
    plt.savefig(out, dpi=fig_cfg.dpi)
    plt.close()
    print(f"Saved: {out}")
    return out


def save_all_figures(
    M1: CoxPHFitter,
    panel_df: pd.DataFrame,
    result: LRTResult,
    cfg: CoxConfig,
    fig_cfg: FigureConfig,
) -> list:
    """Generate and save all 5 figures; return list of saved paths."""
    saved = []
    saved.append(plot_gate_metrics(result, cfg, fig_cfg))
    saved.append(plot_km_quartiles(panel_df, cfg, fig_cfg))
    saved.append(plot_partial_effects(M1, panel_df, cfg, fig_cfg))
    saved.append(plot_forest(M1, cfg, fig_cfg))
    saved.append(plot_schoenfeld(M1, panel_df, cfg, fig_cfg))
    return saved
