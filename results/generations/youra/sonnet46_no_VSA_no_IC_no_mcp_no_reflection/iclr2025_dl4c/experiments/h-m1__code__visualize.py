import os
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class VisualizerConfig:
    figure_dpi: int = 300
    figure_format: str = "png"
    color_binary: str = "#1f77b4"
    color_ratio: str = "#ff7f0e"
    output_dir: str = "docs/youra_research/h-m1/figures"


def plot_gate_metrics(
    results: dict,
    ci_lower: float,
    ci_upper: float,
    output_path: str,
    viz_cfg: VisualizerConfig = None,
) -> None:
    """Figure 1: side-by-side bars HumanEval pass@1 + APPS all-pass for both conditions."""
    if viz_cfg is None:
        viz_cfg = VisualizerConfig()

    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    conditions = ["binary", "ratio"]
    colors = [viz_cfg.color_binary, viz_cfg.color_ratio]

    # HumanEval pass@1
    he_vals = [results["final"][c]["humaneval_pass1"] for c in conditions]
    he_gap = he_vals[1] - he_vals[0]
    he_err = [[0, 0], [he_vals[1] - ci_lower - he_vals[0], ci_upper - he_gap + he_vals[0]]]  # simplified

    bars0 = axes[0].bar(conditions, he_vals, color=colors, alpha=0.8)
    axes[0].set_title("HumanEval pass@1")
    axes[0].set_ylabel("pass@1")
    axes[0].set_ylim(0, max(he_vals) * 1.3)
    for bar, val in zip(bars0, he_vals):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                     f"{val:.3f}", ha="center", va="bottom", fontsize=10)
    # CI annotation
    axes[0].annotate(
        f"gap={he_gap:+.3f}\n95% CI [{ci_lower:+.3f}, {ci_upper:+.3f}]",
        xy=(0.5, 0.95), xycoords="axes fraction", ha="center", va="top", fontsize=8,
    )

    # APPS all-pass
    apps_vals = [results["final"][c]["apps_allpass_rate"] for c in conditions]
    bars1 = axes[1].bar(conditions, apps_vals, color=colors, alpha=0.8)
    axes[1].set_title("APPS-val all-pass rate")
    axes[1].set_ylabel("all-pass fraction")
    axes[1].set_ylim(0, max(apps_vals) * 1.3 if max(apps_vals) > 0 else 0.3)
    for bar, val in zip(bars1, apps_vals):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                     f"{val:.3f}", ha="center", va="bottom", fontsize=10)

    fig.suptitle("H-M1: Gate Metrics — Ratio vs Binary Reward", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=viz_cfg.figure_dpi, format=viz_cfg.figure_format)
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_learning_curves(
    humaneval_curves: dict,
    output_path: str,
    viz_cfg: VisualizerConfig = None,
) -> None:
    """Figure 2: HumanEval pass@1 vs step for both conditions."""
    if viz_cfg is None:
        viz_cfg = VisualizerConfig()

    fig, ax = plt.subplots(figsize=(8, 5))

    for condition, color in [("binary", viz_cfg.color_binary), ("ratio", viz_cfg.color_ratio)]:
        if condition not in humaneval_curves:
            continue
        curve = humaneval_curves[condition]
        steps = sorted(curve.keys())
        vals = [curve[s] for s in steps]
        ax.plot(steps, vals, marker="o", color=color, label=condition, linewidth=2)

    ax.set_xlabel("Training Step")
    ax.set_ylabel("HumanEval pass@1")
    ax.set_title("H-M1: HumanEval Learning Curves")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=viz_cfg.figure_dpi, format=viz_cfg.figure_format)
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_pass_rate_distribution(
    per_problem_rates: dict,
    output_path: str,
    viz_cfg: VisualizerConfig = None,
) -> None:
    """Figure 3: histogram of per-problem k/n pass rates — binary vs ratio."""
    if viz_cfg is None:
        viz_cfg = VisualizerConfig()

    fig, ax = plt.subplots(figsize=(8, 5))
    bins = np.linspace(0, 1, 21)

    for condition, color in [("binary", viz_cfg.color_binary), ("ratio", viz_cfg.color_ratio)]:
        if condition not in per_problem_rates:
            continue
        rates = per_problem_rates[condition]
        ax.hist(rates, bins=bins, color=color, alpha=0.6, label=condition, density=True)

    ax.set_xlabel("Per-problem pass rate (k/n)")
    ax.set_ylabel("Density")
    ax.set_title("H-M1: APPS-val Per-Problem Pass Rate Distribution")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=viz_cfg.figure_dpi, format=viz_cfg.figure_format)
    plt.close(fig)
    print(f"Saved: {output_path}")


def plot_policy_scatter(
    binary_rates: list,
    ratio_rates: list,
    output_path: str,
    viz_cfg: VisualizerConfig = None,
) -> None:
    """Figure 4: scatter (binary_rate, ratio_rate) per APPS-val problem."""
    if viz_cfg is None:
        viz_cfg = VisualizerConfig()

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(binary_rates, ratio_rates, alpha=0.4, s=10, color="steelblue")
    lim_max = max(max(binary_rates, default=1), max(ratio_rates, default=1)) + 0.05
    ax.plot([0, lim_max], [0, lim_max], "k--", linewidth=1, label="y=x")
    ax.set_xlabel("Binary pass rate per problem")
    ax.set_ylabel("Ratio pass rate per problem")
    ax.set_title("H-M1: Policy Target Scatter (APPS-val problems)")
    ax.legend()
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=viz_cfg.figure_dpi, format=viz_cfg.figure_format)
    plt.close(fig)
    print(f"Saved: {output_path}")


def save_all_figures(results: dict, figures_dir: str, viz_cfg: VisualizerConfig = None) -> None:
    """Generate all 4 required figures."""
    if viz_cfg is None:
        viz_cfg = VisualizerConfig()
    os.makedirs(figures_dir, exist_ok=True)

    ci = results.get("analysis", {})
    ci_lower = ci.get("bootstrap_ci_lower", 0.0)
    ci_upper = ci.get("bootstrap_ci_upper", 0.0)

    plot_gate_metrics(results, ci_lower, ci_upper,
                      os.path.join(figures_dir, "fig1_gate_metrics.png"), viz_cfg)

    humaneval_curves = {}
    for condition, curve_data in results.get("checkpoint_results", {}).items():
        humaneval_curves[condition] = {int(k): v for k, v in curve_data.items()}
    plot_learning_curves(humaneval_curves,
                         os.path.join(figures_dir, "fig2_learning_curves.png"), viz_cfg)

    per_problem_rates = results.get("per_problem_rates", {})
    plot_pass_rate_distribution(per_problem_rates,
                                os.path.join(figures_dir, "fig3_distribution.png"), viz_cfg)

    binary_rates = per_problem_rates.get("binary", [])
    ratio_rates = per_problem_rates.get("ratio", [])
    if binary_rates and ratio_rates:
        plot_policy_scatter(binary_rates, ratio_rates,
                            os.path.join(figures_dir, "fig4_policy_scatter.png"), viz_cfg)

    print(f"All figures saved to: {figures_dir}")
