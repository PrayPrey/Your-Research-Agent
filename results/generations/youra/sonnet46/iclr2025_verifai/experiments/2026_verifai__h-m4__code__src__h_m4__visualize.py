"""visualize.py — figure generation for h-m4 difficulty-stratified ECE analysis."""
from __future__ import annotations

import os
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .config import FigureConfig, MODEL_SHORT_NAMES


# Canonical display names for models
_DISPLAY_NAMES = {
    "llama3_8b": "LLaMA-3 8B",
    "codellama_7b": "CodeLlama 7B",
    "deepseek_6.7b": "DeepSeek 6.7B",
}

_TIER_COLORS = {
    "hard": "#d62728",   # red
    "easy": "#2ca02c",   # green
}


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_delta_ece_gate(
    model_results: dict[str, dict[str, Any]],
    output_path: str,
    threshold: float = 0.03,
    dpi: int = 150,
) -> None:
    """Bar chart of delta ECE with 95% CI error bars, color-coded by gate pass/fail.

    Parameters
    ----------
    model_results : {model_short: {delta_ece, ci_lower, ci_upper, gate_p1}}
    output_path : path to save PNG
    threshold : gate threshold line (default 0.03)
    dpi : figure resolution
    """
    _ensure_dir(os.path.dirname(output_path) or ".")

    model_shorts = list(model_results.keys())
    display_names = [_DISPLAY_NAMES.get(m, m) for m in model_shorts]

    delta_eces = [model_results[m]["delta_ece"] for m in model_shorts]
    ci_lowers = [model_results[m]["ci_lower"] for m in model_shorts]
    ci_uppers = [model_results[m]["ci_upper"] for m in model_shorts]
    gate_passes = [model_results[m].get("gate_p1", False) for m in model_shorts]

    yerr_lower = [delta_eces[i] - ci_lowers[i] for i in range(len(model_shorts))]
    yerr_upper = [ci_uppers[i] - delta_eces[i] for i in range(len(model_shorts))]

    colors = ["#2ca02c" if gp else "#d62728" for gp in gate_passes]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(model_shorts))

    bars = ax.bar(
        x,
        delta_eces,
        color=colors,
        alpha=0.8,
        width=0.5,
        yerr=[yerr_lower, yerr_upper],
        capsize=5,
        error_kw={"elinewidth": 1.5, "capthick": 1.5},
    )

    # Reference lines
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", label="y=0")
    ax.axhline(threshold, color="navy", linewidth=1.2, linestyle="--", label=f"threshold={threshold}")

    ax.set_xticks(x)
    ax.set_xticklabels(display_names, rotation=15, ha="right")
    ax.set_ylabel("Δ ECE (hard − easy)")
    ax.set_title("Primary Gate: Δ ECE by Model")
    ax.legend(loc="upper right")

    # Add gate pass/fail annotation
    for i, (gp, de) in enumerate(zip(gate_passes, delta_eces)):
        label = "PASS" if gp else "FAIL"
        color = "#2ca02c" if gp else "#d62728"
        ax.text(i, de + max(yerr_upper) * 0.05, label, ha="center", va="bottom",
                fontsize=9, color=color, fontweight="bold")

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_reliability_diagrams(
    model_eval_data: dict[str, dict[str, np.ndarray]],
    model_results: dict[str, dict[str, Any]],
    output_path: str,
    M: int = 15,
    dpi: int = 150,
) -> None:
    """3x2 grid reliability diagrams: rows=models, cols=hard/easy.

    Each subplot shows binned accuracy bars vs. diagonal (perfect calibration) + ECE annotation.

    Parameters
    ----------
    model_eval_data : {model_short: {c_hard, y_hard, c_easy, y_easy}}
    model_results : {model_short: {ece_hard, ece_easy}}
    output_path : path to save PNG
    M : number of bins
    dpi : figure resolution
    """
    _ensure_dir(os.path.dirname(output_path) or ".")

    model_shorts = list(model_eval_data.keys())
    n_models = len(model_shorts)

    fig, axes = plt.subplots(n_models, 2, figsize=(10, 4 * n_models))
    if n_models == 1:
        axes = axes[np.newaxis, :]

    bin_edges = np.linspace(0, 1, M + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]

    for row, model_short in enumerate(model_shorts):
        data = model_eval_data[model_short]
        res = model_results.get(model_short, {})
        display = _DISPLAY_NAMES.get(model_short, model_short)

        for col, (tier, c_key, y_key, ece_key) in enumerate([
            ("Hard", "c_hard", "y_hard", "ece_hard"),
            ("Easy", "c_easy", "y_easy", "ece_easy"),
        ]):
            ax = axes[row, col]
            c = np.asarray(data[c_key], dtype=float)
            y = np.asarray(data[y_key], dtype=float)

            bin_accs = []
            bin_confs = []
            for k in range(M):
                lower = bin_edges[k]
                upper = bin_edges[k + 1]
                if k == 0:
                    mask = c <= upper
                else:
                    mask = (c > lower) & (c <= upper)
                if mask.sum() == 0:
                    bin_accs.append(np.nan)
                    bin_confs.append(bin_centers[k])
                else:
                    bin_accs.append(y[mask].mean())
                    bin_confs.append(c[mask].mean())

            valid = [i for i, a in enumerate(bin_accs) if not np.isnan(a)]
            bar_heights = [bin_accs[i] for i in valid]
            bar_x = [bin_centers[i] for i in valid]

            color = _TIER_COLORS[tier.lower()]
            ax.bar(bar_x, bar_heights, width=bin_width * 0.9, color=color, alpha=0.6,
                   align="center", label="Accuracy")

            # Perfect calibration diagonal
            ax.plot([0, 1], [0, 1], "k--", linewidth=1, label="Perfect")

            ece_val = res.get(ece_key, float("nan"))
            ax.text(0.05, 0.92, f"ECE={ece_val:.4f}", transform=ax.transAxes,
                    fontsize=9, va="top", color="black",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7))

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xlabel("Confidence")
            ax.set_ylabel("Accuracy")
            ax.set_title(f"{display} — {tier} Tier")
            ax.legend(loc="lower right", fontsize=8)

    plt.suptitle("Reliability Diagrams by Model and Difficulty Tier", fontsize=13, y=1.01)
    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def plot_temperature_scaling_effect(
    model_results: dict[str, dict[str, Any]],
    post_T_results: dict[str, dict[str, Any]],
    output_path: str,
    dpi: int = 150,
) -> None:
    """Grouped bars showing pre vs. post temperature scaling delta ECE per model.

    Parameters
    ----------
    model_results : {model_short: {delta_ece, ece_hard, ece_easy}}
    post_T_results : {model_short: {post_T_delta_ece, T_star, post_T_ece_hard, post_T_ece_easy}}
    output_path : path to save PNG
    dpi : figure resolution
    """
    _ensure_dir(os.path.dirname(output_path) or ".")

    model_shorts = list(model_results.keys())
    display_names = [_DISPLAY_NAMES.get(m, m) for m in model_shorts]

    pre_deltas = [model_results[m]["delta_ece"] for m in model_shorts]
    post_deltas = [post_T_results[m]["post_T_delta_ece"] for m in model_shorts]
    t_stars = [post_T_results[m]["T_star"] for m in model_shorts]

    x = np.arange(len(model_shorts))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    bars_pre = ax.bar(x - width / 2, pre_deltas, width, label="Pre T-scaling", color="#1f77b4", alpha=0.8)
    bars_post = ax.bar(x + width / 2, post_deltas, width, label="Post T-scaling", color="#ff7f0e", alpha=0.8)

    ax.axhline(0.03, color="navy", linewidth=1.2, linestyle="--", label="threshold=0.03")

    # Annotate T* values
    for i, (bar, T) in enumerate(zip(bars_post, t_stars)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f"T*={T:.2f}", ha="center", va="bottom", fontsize=8, color="#ff7f0e")

    ax.set_xticks(x)
    ax.set_xticklabels(display_names, rotation=15, ha="right")
    ax.set_ylabel("Δ ECE (hard − easy)")
    ax.set_title("Temperature Scaling Effect on Δ ECE")
    ax.legend(loc="upper right")

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_null_baseline_comparison(
    model_results: dict[str, dict[str, Any]],
    null_results: dict[str, dict[str, Any]],
    output_path: str,
    dpi: int = 150,
) -> None:
    """Grouped bars of observed ECE vs null ECE per model per tier.

    Parameters
    ----------
    model_results : {model_short: {ece_hard, ece_easy}}
    null_results : {model_short: {null_ece_hard, null_ece_easy}}
    output_path : path to save PNG
    dpi : figure resolution
    """
    _ensure_dir(os.path.dirname(output_path) or ".")

    model_shorts = list(model_results.keys())
    display_names = [_DISPLAY_NAMES.get(m, m) for m in model_shorts]

    n = len(model_shorts)
    x = np.arange(n)
    width = 0.2

    obs_hard = [model_results[m]["ece_hard"] for m in model_shorts]
    obs_easy = [model_results[m]["ece_easy"] for m in model_shorts]
    null_hard = [null_results[m]["null_ece_hard"] for m in model_shorts]
    null_easy = [null_results[m]["null_ece_easy"] for m in model_shorts]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - 1.5 * width, obs_hard, width, label="Obs. ECE (Hard)", color="#d62728", alpha=0.8)
    ax.bar(x - 0.5 * width, null_hard, width, label="Null ECE (Hard)", color="#d62728", alpha=0.4, hatch="//")
    ax.bar(x + 0.5 * width, obs_easy, width, label="Obs. ECE (Easy)", color="#2ca02c", alpha=0.8)
    ax.bar(x + 1.5 * width, null_easy, width, label="Null ECE (Easy)", color="#2ca02c", alpha=0.4, hatch="//")

    ax.set_xticks(x)
    ax.set_xticklabels(display_names, rotation=15, ha="right")
    ax.set_ylabel("ECE")
    ax.set_title("Observed vs. Null Baseline ECE by Model and Tier")
    ax.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_m_sensitivity(
    m_sensitivity_results: dict[str, dict[int, float]],
    output_path: str,
    dpi: int = 150,
) -> None:
    """Line plot of delta ECE vs M (number of bins) per model.

    Parameters
    ----------
    m_sensitivity_results : {model_short: {M: delta_ece}}
    output_path : path to save PNG
    dpi : figure resolution
    """
    _ensure_dir(os.path.dirname(output_path) or ".")

    fig, ax = plt.subplots(figsize=(7, 5))

    markers = ["o", "s", "^"]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for idx, (model_short, m_dict) in enumerate(m_sensitivity_results.items()):
        display = _DISPLAY_NAMES.get(model_short, model_short)
        m_vals = sorted(m_dict.keys())
        delta_vals = [m_dict[M] for M in m_vals]
        ax.plot(m_vals, delta_vals, marker=markers[idx % len(markers)],
                color=colors[idx % len(colors)], label=display, linewidth=2, markersize=8)

    ax.axhline(0.03, color="navy", linewidth=1.2, linestyle="--", label="threshold=0.03")
    ax.set_xlabel("M (number of bins)")
    ax.set_ylabel("Δ ECE (hard − easy)")
    ax.set_title("M Sensitivity: Δ ECE vs. Number of Bins")
    ax.legend(loc="best")

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def plot_bootstrap_distributions(
    bootstrap_samples: dict[str, np.ndarray],
    model_results: dict[str, dict[str, Any]],
    output_path: str,
    n_bins: int = 30,
    dpi: int = 150,
) -> None:
    """Histograms of bootstrap delta ECE distributions per model with CI shading.

    Parameters
    ----------
    bootstrap_samples : {model_short: array of shape (n_boot,)}
    model_results : {model_short: {delta_ece, ci_lower, ci_upper}}
    output_path : path to save PNG
    n_bins : number of histogram bins
    dpi : figure resolution
    """
    _ensure_dir(os.path.dirname(output_path) or ".")

    model_shorts = list(bootstrap_samples.keys())
    n_models = len(model_shorts)

    fig, axes = plt.subplots(1, n_models, figsize=(5 * n_models, 5), sharey=False)
    if n_models == 1:
        axes = [axes]

    for ax, model_short in zip(axes, model_shorts):
        samples = np.asarray(bootstrap_samples[model_short], dtype=float)
        res = model_results.get(model_short, {})
        display = _DISPLAY_NAMES.get(model_short, model_short)

        ci_lower = res.get("ci_lower", np.percentile(samples, 2.5))
        ci_upper = res.get("ci_upper", np.percentile(samples, 97.5))
        delta_obs = res.get("delta_ece", np.mean(samples))

        ax.hist(samples, bins=n_bins, color="#1f77b4", alpha=0.7, edgecolor="white")

        # Shade CI region
        x_fill = samples[(samples >= ci_lower) & (samples <= ci_upper)]
        if len(x_fill) > 0:
            counts, bin_edges = np.histogram(x_fill, bins=n_bins,
                                              range=(samples.min(), samples.max()))
        # Just shade the CI region with axvspan
        ax.axvspan(ci_lower, ci_upper, alpha=0.2, color="orange", label=f"95% CI")

        # Reference lines
        ax.axvline(0, color="black", linewidth=1, linestyle="--", label="0")
        ax.axvline(delta_obs, color="red", linewidth=1.5, linestyle="-", label=f"obs={delta_obs:.3f}")
        ax.axvline(0.03, color="navy", linewidth=1.2, linestyle=":", label="threshold=0.03")

        ax.set_xlabel("Bootstrap Δ ECE")
        ax.set_ylabel("Count")
        ax.set_title(f"{display}\nCI=[{ci_lower:.3f}, {ci_upper:.3f}]")
        ax.legend(fontsize=7, loc="upper left")

    plt.suptitle("Bootstrap Distributions of Δ ECE", fontsize=13)
    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)


def save_all_figures(
    model_results: dict[str, dict[str, Any]],
    model_eval_data: dict[str, dict[str, np.ndarray]],
    post_T_results: dict[str, dict[str, Any]],
    null_results: dict[str, dict[str, Any]],
    m_sensitivity_results: dict[str, dict[int, float]],
    bootstrap_samples: dict[str, np.ndarray],
    fig_cfg: FigureConfig,
) -> None:
    """Orchestrate all 6 figures.

    Parameters
    ----------
    model_results : per-model primary results
    model_eval_data : per-model eval split data
    post_T_results : per-model temperature scaling results
    null_results : per-model null baseline results
    m_sensitivity_results : per-model M sensitivity dict
    bootstrap_samples : per-model bootstrap sample arrays
    fig_cfg : FigureConfig with paths and settings
    """
    _ensure_dir(fig_cfg.figures_dir)

    fig1_path = os.path.join(fig_cfg.figures_dir, fig_cfg.fig1_filename)
    plot_delta_ece_gate(model_results, fig1_path, dpi=fig_cfg.dpi)

    fig2_path = os.path.join(fig_cfg.figures_dir, fig_cfg.fig2_filename)
    plot_reliability_diagrams(
        model_eval_data, model_results, fig2_path,
        M=fig_cfg.reliability_bins, dpi=fig_cfg.dpi
    )

    fig3_path = os.path.join(fig_cfg.figures_dir, fig_cfg.fig3_filename)
    plot_temperature_scaling_effect(model_results, post_T_results, fig3_path, dpi=fig_cfg.dpi)

    fig4_path = os.path.join(fig_cfg.figures_dir, fig_cfg.fig4_filename)
    plot_null_baseline_comparison(model_results, null_results, fig4_path, dpi=fig_cfg.dpi)

    fig5_path = os.path.join(fig_cfg.figures_dir, fig_cfg.fig5_filename)
    plot_m_sensitivity(m_sensitivity_results, fig5_path, dpi=fig_cfg.dpi)

    fig6_path = os.path.join(fig_cfg.figures_dir, fig_cfg.fig6_filename)
    plot_bootstrap_distributions(
        bootstrap_samples, model_results, fig6_path,
        n_bins=fig_cfg.bootstrap_hist_bins, dpi=fig_cfg.dpi
    )
