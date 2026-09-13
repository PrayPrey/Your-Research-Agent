"""Results persistence and visualization for H-M1."""

import json
import yaml
from pathlib import Path
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from config import RepairConfig, GRANULARITY_LEVELS


# Visualization config
VIZ_CONFIG = {
    "figure_dpi": 150,
    "bar_color_palette": "Blues_d",
    "heatmap_cmap": "RdYlGn",
    "ci_confidence": 0.95,
    "figure_size": (8, 5),
}


def save_results(
    results: list[dict],
    metrics: dict,
    posthoc: Optional[dict],
    config: RepairConfig,
) -> None:
    """Save repair results, metrics, and post-hoc analysis to files.

    Args:
        results: List of repair result dicts
        metrics: ANOVA metrics dict
        posthoc: Tukey HSD results dict (or None if ANOVA not significant)
        config: RepairConfig with output paths
    """
    # Create directories
    Path(config.results_dir).mkdir(parents=True, exist_ok=True)

    # Save repair results JSON
    with open(config.output_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved repair results to {config.output_json}")

    # Save metrics YAML
    with open(config.output_metrics, "w") as f:
        yaml.dump(metrics, f, default_flow_style=False)
    print(f"Saved metrics to {config.output_metrics}")

    # Save post-hoc YAML (if available)
    if posthoc is not None:
        with open(config.output_posthoc, "w") as f:
            yaml.dump(posthoc, f, default_flow_style=False)
        print(f"Saved post-hoc analysis to {config.output_posthoc}")


def _wilson_ci(successes: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Calculate Wilson score confidence interval for proportion."""
    if n == 0:
        return (0.0, 0.0)

    z = stats.norm.ppf(1 - (1 - confidence) / 2)
    p = successes / n

    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    spread = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denominator

    return (max(0, center - spread), min(1, center + spread))


def plot_success_rate_bar(groups: dict[str, list[int]], figures_dir: str) -> None:
    """Bar chart: repair success rate per granularity with 95% CI error bars.

    Args:
        groups: Dict mapping granularity to list of binary success values
        figures_dir: Directory to save figure
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    success_rates = []
    ci_lower = []
    ci_upper = []

    for g in GRANULARITY_LEVELS:
        data = groups[g]
        rate = np.mean(data) if data else 0
        success_rates.append(rate)

        # Wilson CI
        successes = sum(data)
        n = len(data)
        lo, hi = _wilson_ci(successes, n)
        ci_lower.append(rate - lo)
        ci_upper.append(hi - rate)

    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figure_size"])

    x = np.arange(len(GRANULARITY_LEVELS))
    colors = sns.color_palette(VIZ_CONFIG["bar_color_palette"], len(GRANULARITY_LEVELS))

    bars = ax.bar(x, success_rates, color=colors, edgecolor="black", linewidth=1.2)
    ax.errorbar(x, success_rates, yerr=[ci_lower, ci_upper],
                fmt="none", color="black", capsize=5, capthick=2)

    ax.set_xlabel("Granularity Level", fontsize=12)
    ax.set_ylabel("Repair Success Rate", fontsize=12)
    ax.set_title("Repair Success Rate by Error Feedback Granularity", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(GRANULARITY_LEVELS)
    ax.set_ylim(0, max(success_rates) * 1.3 if max(success_rates) > 0 else 0.5)

    # Add percentage labels
    for i, (bar, rate) in enumerate(zip(bars, success_rates)):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{rate:.1%}", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(f"{figures_dir}/success_rate_bar.png", dpi=VIZ_CONFIG["figure_dpi"])
    plt.close()
    print(f"Saved success rate bar chart")


def plot_granularity_curve(groups: dict[str, list[int]], figures_dir: str) -> None:
    """Line plot: repair rate vs granularity level (G0 -> G4).

    Args:
        groups: Dict mapping granularity to list of binary success values
        figures_dir: Directory to save figure
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    success_rates = [np.mean(groups[g]) if groups[g] else 0 for g in GRANULARITY_LEVELS]

    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figure_size"])

    x = range(len(GRANULARITY_LEVELS))
    ax.plot(x, success_rates, marker="o", markersize=10, linewidth=2.5,
            color="#2196F3", markerfacecolor="#1976D2")

    # Fill area under curve
    ax.fill_between(x, success_rates, alpha=0.2, color="#2196F3")

    ax.set_xlabel("Granularity Level", fontsize=12)
    ax.set_ylabel("Repair Success Rate", fontsize=12)
    ax.set_title("Granularity Effect Curve (G0 → G4)", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(GRANULARITY_LEVELS)
    ax.set_ylim(0, max(success_rates) * 1.2 if max(success_rates) > 0 else 0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"{figures_dir}/granularity_curve.png", dpi=VIZ_CONFIG["figure_dpi"])
    plt.close()
    print(f"Saved granularity curve plot")


def plot_anova_summary(metrics: dict, figures_dir: str) -> None:
    """Visualization of ANOVA results: F-statistic, p-value, eta-squared.

    Args:
        metrics: ANOVA metrics dict from run_anova()
        figures_dir: Directory to save figure
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # F-statistic
    ax1 = axes[0]
    ax1.bar(["F-statistic"], [metrics["f_statistic"]], color="#4CAF50", edgecolor="black")
    ax1.set_ylabel("Value", fontsize=11)
    ax1.set_title(f"F-statistic = {metrics['f_statistic']:.2f}", fontsize=12)

    # P-value (log scale comparison)
    ax2 = axes[1]
    p_val = metrics["p_value"]
    color = "#4CAF50" if p_val < 0.05 else "#F44336"
    ax2.bar(["p-value"], [p_val], color=color, edgecolor="black")
    ax2.axhline(y=0.05, color="red", linestyle="--", linewidth=2, label="alpha = 0.05")
    ax2.set_ylabel("p-value", fontsize=11)
    ax2.set_title(f"p = {p_val:.4f} {'PASS' if p_val < 0.05 else 'FAIL'}", fontsize=12)
    ax2.legend()

    # Eta-squared
    ax3 = axes[2]
    eta_sq = metrics["eta_squared"]
    ax3.bar(["eta-squared"], [eta_sq], color="#2196F3", edgecolor="black")
    ax3.axhline(y=0.02, color="orange", linestyle="--", linewidth=2, label="Small effect (0.02)")
    ax3.axhline(y=0.06, color="red", linestyle="--", linewidth=2, label="Medium effect (0.06)")
    ax3.set_ylabel("Effect Size", fontsize=11)
    ax3.set_title(f"eta-squared = {eta_sq:.4f}", fontsize=12)
    ax3.legend(fontsize=8)

    plt.suptitle("ANOVA Results Summary", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(f"{figures_dir}/anova_summary.png", dpi=VIZ_CONFIG["figure_dpi"], bbox_inches="tight")
    plt.close()
    print(f"Saved ANOVA summary plot")


def plot_gate_comparison(metrics: dict, figures_dir: str, alpha: float = 0.05) -> None:
    """Bar chart: ANOVA p-value vs threshold (GATE visualization).

    Args:
        metrics: ANOVA metrics dict
        figures_dir: Directory to save figure
        alpha: Significance threshold (default 0.05)
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(6, 5))

    p_val = metrics["p_value"]
    passed = p_val < alpha

    colors = ["#4CAF50" if passed else "#F44336", "#BDBDBD"]
    ax.bar(["ANOVA p-value", "Threshold (alpha)"], [p_val, alpha],
           color=colors, edgecolor="black", linewidth=1.5)

    ax.set_ylabel("Value", fontsize=12)
    ax.set_title(f"MUST_WORK Gate: {'PASS' if passed else 'FAIL'}", fontsize=14,
                 color="#4CAF50" if passed else "#F44336")

    # Add value labels
    ax.text(0, p_val + 0.002, f"{p_val:.4f}", ha="center", fontsize=11)
    ax.text(1, alpha + 0.002, f"{alpha}", ha="center", fontsize=11)

    plt.tight_layout()
    plt.savefig(f"{figures_dir}/gate_comparison.png", dpi=VIZ_CONFIG["figure_dpi"])
    plt.close()
    print(f"Saved gate comparison plot")


def plot_posthoc_heatmap(posthoc: dict, figures_dir: str) -> None:
    """Heatmap of Tukey HSD p-values for all granularity pairs.

    Args:
        posthoc: Tukey HSD results dict from run_posthoc()
        figures_dir: Directory to save figure
    """
    if posthoc is None:
        print("Skipping post-hoc heatmap (ANOVA not significant)")
        return

    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    # Build p-value matrix
    n = len(GRANULARITY_LEVELS)
    p_matrix = np.ones((n, n))

    for i, g1 in enumerate(GRANULARITY_LEVELS):
        for j, g2 in enumerate(GRANULARITY_LEVELS):
            if i < j:
                key = f"{g1}_vs_{g2}"
                if key in posthoc:
                    p_matrix[i, j] = posthoc[key]["p_value"]
                    p_matrix[j, i] = posthoc[key]["p_value"]

    fig, ax = plt.subplots(figsize=(7, 6))

    mask = np.triu(np.ones_like(p_matrix, dtype=bool), k=1)
    mask = ~mask  # Show upper triangle

    sns.heatmap(p_matrix, mask=mask, annot=True, fmt=".3f",
                xticklabels=GRANULARITY_LEVELS, yticklabels=GRANULARITY_LEVELS,
                cmap="RdYlGn_r", center=0.05, vmin=0, vmax=0.2,
                cbar_kws={"label": "p-value"}, ax=ax)

    ax.set_title("Tukey HSD Pairwise Comparisons (p-values)", fontsize=14)

    plt.tight_layout()
    plt.savefig(f"{figures_dir}/posthoc_heatmap.png", dpi=VIZ_CONFIG["figure_dpi"])
    plt.close()
    print(f"Saved post-hoc heatmap")


def plot_error_type_breakdown(results: list[dict], groups: dict, figures_dir: str) -> None:
    """Stratified repair success by error type.

    Args:
        results: List of repair result dicts
        groups: Dict mapping granularity to success values
        figures_dir: Directory to save figure
    """
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=VIZ_CONFIG["figure_size"])

    # Count successes and failures per granularity
    success_counts = []
    failure_counts = []

    for g in GRANULARITY_LEVELS:
        data = groups[g]
        success_counts.append(sum(data))
        failure_counts.append(len(data) - sum(data))

    x = np.arange(len(GRANULARITY_LEVELS))
    width = 0.6

    ax.bar(x, success_counts, width, label="Success", color="#4CAF50", edgecolor="black")
    ax.bar(x, failure_counts, width, bottom=success_counts, label="Failure", color="#F44336", edgecolor="black")

    ax.set_xlabel("Granularity Level", fontsize=12)
    ax.set_ylabel("Number of Cases", fontsize=12)
    ax.set_title("Repair Outcomes by Granularity Level", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(GRANULARITY_LEVELS)
    ax.legend()

    plt.tight_layout()
    plt.savefig(f"{figures_dir}/error_breakdown.png", dpi=VIZ_CONFIG["figure_dpi"])
    plt.close()
    print(f"Saved error breakdown plot")


def generate_all_figures(
    results: list[dict],
    groups: dict[str, list[int]],
    metrics: dict,
    posthoc: Optional[dict],
    config: RepairConfig,
) -> None:
    """Generate all required figures for validation report.

    Args:
        results: List of repair result dicts
        groups: Aggregated success values by granularity
        metrics: ANOVA metrics dict
        posthoc: Tukey HSD results (or None)
        config: RepairConfig with figures_dir
    """
    figures_dir = config.figures_dir
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating figures in {figures_dir}/")

    # 1. Success rate bar chart with CI
    plot_success_rate_bar(groups, figures_dir)

    # 2. Granularity effect curve
    plot_granularity_curve(groups, figures_dir)

    # 3. ANOVA summary
    plot_anova_summary(metrics, figures_dir)

    # 4. Gate comparison
    plot_gate_comparison(metrics, figures_dir, alpha=config.anova_alpha)

    # 5. Post-hoc heatmap (if ANOVA significant)
    if metrics.get("gate_passed", False) and posthoc:
        plot_posthoc_heatmap(posthoc, figures_dir)

    # 6. Error breakdown
    plot_error_type_breakdown(results, groups, figures_dir)

    print(f"All figures generated successfully")
