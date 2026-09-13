"""H-M4: Figure generation — 5 required figures."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path
from typing import Optional

from config import (
    TAU_THRESHOLD, DELTA_R2_THRESHOLD, GAP_THRESHOLD, FIGURES_DIR,
    FigureConfig, PlotConfig,
)
from analysis import H_M4_Results

_fig_cfg = FigureConfig()
_plot_cfg = PlotConfig()


def _model_label(model_id: str) -> str:
    labels = {
        "gpt-4o-mini": "GPT-4o-mini",
        "deepseek-coder-v2-lite": "DeepSeek-V2-Lite",
        "claude-3-haiku": "Claude-3-Haiku",
        "codellama-34b": "CodeLlama-34B",
        "codellama-13b": "CodeLlama-13B",
    }
    return labels.get(model_id, model_id)


def plot_gate_metrics_bar(results: H_M4_Results, save_path: Optional[Path] = None) -> None:
    """Figure 1: bar chart of τ, |ΔR²|, gap with threshold lines."""
    fig, ax = plt.subplots(figsize=_fig_cfg.bar_figsize)

    metrics = ["Kendall τ", "Partial ΔR²", "Cross-Model Gap"]
    values = [abs(results.tau), results.delta_R2, results.cross_model_gap]
    thresholds = [TAU_THRESHOLD, DELTA_R2_THRESHOLD, GAP_THRESHOLD]
    colors = ["#4C72B0", "#DD8452", "#55A868"]

    bars = ax.bar(metrics, values, color=colors, alpha=0.85, edgecolor="black", linewidth=0.5)

    for thresh, x, label in zip(thresholds, range(len(metrics)), metrics):
        ax.hlines(thresh, x - 0.4, x + 0.4, colors=_fig_cfg.threshold_color,
                  linestyles=_fig_cfg.threshold_linestyle, linewidth=_fig_cfg.threshold_linewidth)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("H-M4 Gate Metrics vs Thresholds", fontsize=13, fontweight="bold")
    ax.set_ylabel("Value", fontsize=11)
    ax.set_ylim(0, max(max(values) * 1.3, max(thresholds) * 1.3))

    gate_str = "PASS" if results.gate_pass else ("PARTIAL" if results.gate_partial else "FAIL")
    ax.text(0.98, 0.95, f"Gate: {gate_str}", transform=ax.transAxes,
            ha="right", va="top", fontsize=12, fontweight="bold",
            color="green" if results.gate_pass else ("orange" if results.gate_partial else "red"))

    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([0], [0], color=_fig_cfg.threshold_color,
                              linestyle=_fig_cfg.threshold_linestyle,
                              linewidth=_fig_cfg.threshold_linewidth)],
              labels=["Threshold"], loc="upper left")

    plt.tight_layout()
    path = save_path or (FIGURES_DIR / "gate_metrics_bar.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=_fig_cfg.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def plot_ranking_scatter(
    model_rates: pd.Series,
    pass_at_1: dict,
    results: H_M4_Results,
    save_path: Optional[Path] = None,
) -> None:
    """Figure 2: contract rate (y) vs pass@1* (x), model labels, τ annotated."""
    fig, ax = plt.subplots(figsize=_fig_cfg.scatter_figsize)

    for model_id in model_rates.index:
        if model_id not in pass_at_1:
            continue
        x = pass_at_1[model_id]
        y = float(model_rates[model_id])
        color = _fig_cfg.model_colors.get(model_id, "gray")
        ax.scatter(x, y, color=color, s=_plot_cfg.scatter_point_size,
                   alpha=_plot_cfg.scatter_alpha, zorder=5)
        ax.annotate(_model_label(model_id), (x, y),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

    # OLS regression line
    models = [m for m in model_rates.index if m in pass_at_1]
    xs = np.array([pass_at_1[m] for m in models])
    ys = np.array([float(model_rates[m]) for m in models])
    if len(xs) >= 2:
        m, b = np.polyfit(xs, ys, 1)
        x_line = np.linspace(xs.min(), xs.max(), 100)
        ax.plot(x_line, m * x_line + b, "k--", linewidth=1, alpha=0.5, label="OLS baseline")

    ax.set_xlabel("EvalPlus pass@1* (weighted avg)", fontsize=11)
    ax.set_ylabel("Mean Contract-Satisfaction Rate", fontsize=11)
    ax.set_title("Contract-Satisfaction vs pass@1* by Model", fontsize=13, fontweight="bold")
    ax.text(0.05, 0.95, f"Kendall τ = {results.tau:.3f}\np = {results.tau_pvalue:.4f}",
            transform=ax.transAxes, fontsize=10, va="top",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.legend()
    plt.tight_layout()

    path = save_path or (FIGURES_DIR / "ranking_scatter.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=_fig_cfg.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def plot_cross_model_bar(
    exp_b_df: pd.DataFrame,
    pass_at_1: dict,
    results: H_M4_Results,
    save_path: Optional[Path] = None,
) -> None:
    """Figure 3: per-model contract rate sorted; pass@1* rank on secondary axis."""
    model_rates = exp_b_df.groupby("model_id")["contract_satisfaction_rate"].mean()
    sorted_models = model_rates.sort_values(ascending=False).index.tolist()

    fig, ax1 = plt.subplots(figsize=_fig_cfg.bar_figsize)
    x = np.arange(len(sorted_models))
    colors = [_fig_cfg.model_colors.get(m, "gray") for m in sorted_models]

    bars = ax1.bar(x, [float(model_rates[m]) for m in sorted_models],
                   color=colors, alpha=0.85, edgecolor="black", linewidth=0.5)
    ax1.set_xlabel("Model", fontsize=11)
    ax1.set_ylabel("Mean Contract-Satisfaction Rate", fontsize=11)
    ax1.set_xticks(x)
    ax1.set_xticklabels([_model_label(m) for m in sorted_models], rotation=15, ha="right")
    ax1.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

    # Secondary axis: pass@1* rank
    ax2 = ax1.twinx()
    pass_ranks = {m: sorted(pass_at_1, key=pass_at_1.get, reverse=True).index(m) + 1
                  for m in sorted_models if m in pass_at_1}
    ax2.plot(x, [pass_ranks.get(m, float("nan")) for m in sorted_models],
             "ro--", linewidth=1.5, markersize=6, label="pass@1* rank")
    ax2.set_ylabel("pass@1* Rank (1=best)", fontsize=11)
    ax2.set_yticks(range(1, len(sorted_models) + 1))
    ax2.invert_yaxis()

    ax1.set_title("Per-Model Contract-Satisfaction Rate (sorted)", fontsize=13, fontweight="bold")
    ax1.text(0.98, 0.98, f"Gap = {results.cross_model_gap:.3f}", transform=ax1.transAxes,
             ha="right", va="top", fontsize=10,
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    ax2.legend(loc="upper right")
    plt.tight_layout()

    path = save_path or (FIGURES_DIR / "cross_model_bar.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=_fig_cfg.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def plot_r2_decomposition(results: H_M4_Results, save_path: Optional[Path] = None) -> None:
    """Figure 4: variance decomposition — reduced R², model-family ΔR², residual."""
    fig, ax = plt.subplots(figsize=_fig_cfg.bar_figsize)

    components = ["pass@1* + log(size)", "Model Family (ΔR²)", "Residual"]
    delta = max(0.0, results.delta_R2)
    reduced = max(0.0, results.R2_reduced)
    residual = max(0.0, 1.0 - reduced - delta)

    values = [reduced, delta, residual]
    colors = ["#4C72B0", "#DD8452", "#CCCCCC"]

    bottom = 0
    for val, color, label in zip(values, colors, components):
        ax.bar(0, val, bottom=bottom, color=color, alpha=0.85, edgecolor="black",
               linewidth=0.5, label=f"{label}: {val:.3f}")
        bottom += val

    ax.set_xlim(-0.5, 0.5)
    ax.set_xticks([])
    ax.set_ylabel("Marginal R²", fontsize=11)
    ax.set_title("Variance Decomposition of Contract-Satisfaction Rate", fontsize=13, fontweight="bold")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper right", fontsize=9)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

    fallback_note = " (OLS fallback)" if results.fallback_ols else ""
    conv_note = " (converged)" if results.converged else " (not converged)"
    ax.text(0.02, 0.02, f"MixedLM{fallback_note}{conv_note}", transform=ax.transAxes,
            fontsize=8, alpha=0.7)

    plt.tight_layout()
    path = save_path or (FIGURES_DIR / "r2_decomposition.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=_fig_cfg.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def plot_permutation_null(results: H_M4_Results, save_path: Optional[Path] = None) -> None:
    """Figure 5: histogram of permutation null distribution with observed τ marked."""
    fig, ax = plt.subplots(figsize=_fig_cfg.histogram_figsize)

    null = np.array(results.permutation_null)
    ax.hist(null, bins=_plot_cfg.perm_hist_bins,
            color=_plot_cfg.perm_null_color, alpha=_plot_cfg.perm_null_alpha,
            edgecolor="white", linewidth=0.3, label="Null distribution")
    ax.axvline(results.tau, color=_plot_cfg.perm_observed_color,
               linewidth=2, linestyle="-", label=f"Observed τ = {results.tau:.3f}")
    ax.axvline(TAU_THRESHOLD, color="orange", linewidth=1.5,
               linestyle="--", label=f"Threshold τ = {TAU_THRESHOLD}")

    ax.set_xlabel("Kendall τ", fontsize=11)
    ax.set_ylabel("Count", fontsize=11)
    ax.set_title(f"Permutation Null Distribution (n=5! = {len(null)} perms)", fontsize=13, fontweight="bold")
    ax.text(0.98, 0.95, f"p = {results.tau_pvalue:.4f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    ax.legend()
    plt.tight_layout()

    path = save_path or (FIGURES_DIR / "permutation_null.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=_fig_cfg.dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def save_all_figures(
    results: H_M4_Results,
    exp_b_df: pd.DataFrame,
    df_long: pd.DataFrame,
    pass_at_1: dict,
    figures_dir: Optional[Path] = None,
) -> None:
    """Generate and save all 5 figures."""
    fdir = figures_dir or FIGURES_DIR
    fdir.mkdir(parents=True, exist_ok=True)

    model_rates = exp_b_df.groupby("model_id")["contract_satisfaction_rate"].mean()
    model_rates_filtered = model_rates[[m for m in model_rates.index if m in pass_at_1]]

    plot_gate_metrics_bar(results, fdir / "gate_metrics_bar.png")
    plot_ranking_scatter(model_rates_filtered, pass_at_1, results, fdir / "ranking_scatter.png")
    plot_cross_model_bar(exp_b_df, pass_at_1, results, fdir / "cross_model_bar.png")
    plot_r2_decomposition(results, fdir / "r2_decomposition.png")
    plot_permutation_null(results, fdir / "permutation_null.png")

    print(f"\nAll figures saved to: {fdir}")
