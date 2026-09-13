"""Visualization functions for H-M2: G3 vs G0 comparison plots."""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_comparison(rates: dict, output_dir: str, colors: dict = None) -> str:
    """Bar chart comparing G0 vs G3 success rates with threshold line.

    Args:
        rates: Output from calculate_rates_and_difference()
        output_dir: Directory to save figure
        colors: Color dictionary with G0, G3, threshold keys

    Returns:
        Path to saved figure
    """
    if colors is None:
        colors = {"G0": "#2ecc71", "G3": "#e74c3c", "threshold": "#f39c12"}

    fig, ax = plt.subplots(figsize=(8, 6))

    # Bar positions and values
    x = [0, 1]
    labels = ["G0 (pass/fail)", "G3 (error+line)"]
    values = [rates["g0_rate"] * 100, rates["g3_rate"] * 100]
    bar_colors = [colors["G0"], colors["G3"]]

    # Create bars
    bars = ax.bar(x, values, color=bar_colors, width=0.6, edgecolor="black", linewidth=1.5)

    # Add threshold line (G0 + 10pp)
    threshold = rates["g0_rate"] * 100 + 10
    ax.axhline(y=threshold, color=colors["threshold"], linestyle="--", linewidth=2,
               label=f"Required: G0 + 10pp = {threshold:.1f}%")

    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=14, fontweight="bold")

    # Formatting
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylabel("Success Rate (%)", fontsize=12)
    ax.set_title("H-M2: G3 vs G0 Repair Success Rate Comparison", fontsize=14, fontweight="bold")
    ax.set_ylim(0, max(values) + 15)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)

    # Add annotation for difference
    diff_pp = rates["difference_pp"]
    diff_text = f"Difference (G3-G0): {diff_pp:+.1f}pp"
    ax.text(0.5, 0.02, diff_text, transform=ax.transAxes, fontsize=11,
            ha="center", va="bottom", style="italic",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()

    # Save
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "g0_vs_g3_comparison.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    return filepath


def plot_contingency_heatmap(table: np.ndarray, output_dir: str) -> str:
    """Heatmap of 2x2 contingency table showing paired outcomes.

    Args:
        table: 2x2 contingency table from build_contingency_table()
        output_dir: Directory to save figure

    Returns:
        Path to saved figure
    """
    fig, ax = plt.subplots(figsize=(7, 6))

    # Create heatmap
    sns.heatmap(table, annot=True, fmt="d", cmap="YlOrRd", ax=ax,
                xticklabels=["G3 Fail", "G3 Success"],
                yticklabels=["G0 Fail", "G0 Success"],
                annot_kws={"size": 16, "weight": "bold"},
                cbar_kws={"label": "Count"})

    ax.set_xlabel("G3 Outcome", fontsize=12)
    ax.set_ylabel("G0 Outcome", fontsize=12)
    ax.set_title("Contingency Table: G0 vs G3 Paired Outcomes", fontsize=14, fontweight="bold")

    # Add interpretation
    b = table[0, 1]  # G0 fail, G3 success
    c = table[1, 0]  # G0 success, G3 fail
    interp = f"Discordant: G0→G3 success={b}, G3→G0 success={c}"
    ax.text(0.5, -0.15, interp, transform=ax.transAxes, fontsize=10,
            ha="center", va="top", style="italic")

    plt.tight_layout()

    # Save
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "contingency_heatmap.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    return filepath


def plot_difference_ci(rates: dict, output_dir: str, colors: dict = None) -> str:
    """Error bar plot showing difference with 95% CI.

    Args:
        rates: Output from calculate_rates_and_difference()
        output_dir: Directory to save figure
        colors: Color dictionary

    Returns:
        Path to saved figure
    """
    if colors is None:
        colors = {"G3": "#e74c3c", "threshold": "#f39c12"}

    fig, ax = plt.subplots(figsize=(8, 5))

    # Point estimate and CI
    diff_pp = rates["difference_pp"]
    ci_lower = rates["ci_lower_pp"]
    ci_upper = rates["ci_upper_pp"]

    # Error bar
    ax.errorbar(x=[diff_pp], y=[0.5], xerr=[[diff_pp - ci_lower], [ci_upper - diff_pp]],
                fmt="o", color=colors["G3"], markersize=12, capsize=8, capthick=2,
                elinewidth=2, label=f"G3-G0 = {diff_pp:.1f}pp")

    # Threshold line at +10pp
    ax.axvline(x=10, color=colors["threshold"], linestyle="--", linewidth=2,
               label="Required: +10pp")

    # Zero line
    ax.axvline(x=0, color="gray", linestyle="-", linewidth=1, alpha=0.5)

    # Shading
    ax.axvspan(10, 50, alpha=0.1, color="green", label="Gate PASS region")
    ax.axvspan(-50, 10, alpha=0.1, color="red", label="Gate FAIL region")

    # Formatting
    ax.set_xlim(-35, 25)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Difference (G3 - G0) in Percentage Points", fontsize=12)
    ax.set_yticks([])
    ax.set_title("H-M2: Difference Estimate with 95% Confidence Interval", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left")

    # Add annotation
    ax.text(diff_pp, 0.3, f"{diff_pp:.1f}pp\n[{ci_lower:.1f}, {ci_upper:.1f}]",
            ha="center", va="top", fontsize=10, fontweight="bold")

    plt.tight_layout()

    # Save
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "difference_ci.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    return filepath


def plot_gate_summary(rates: dict, gate: dict, mcnemar: dict, output_dir: str, colors: dict = None) -> str:
    """Summary figure with gate result and key metrics.

    Args:
        rates: Output from calculate_rates_and_difference()
        gate: Output from evaluate_gate()
        mcnemar: Output from run_mcnemar_test()
        output_dir: Directory to save figure
        colors: Color dictionary

    Returns:
        Path to saved figure
    """
    if colors is None:
        colors = {"success": "#27ae60", "fail": "#c0392b"}

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")

    # Gate result color
    result_color = colors["success"] if gate["gate_passed"] else colors["fail"]

    # Title with gate result
    ax.text(0.5, 0.95, "H-M2: Gate Evaluation Summary", fontsize=18, fontweight="bold",
            ha="center", va="top", transform=ax.transAxes)

    # Gate verdict
    verdict_box = dict(boxstyle="round,pad=0.5", facecolor=result_color, alpha=0.8)
    ax.text(0.5, 0.82, gate["verdict"], fontsize=24, fontweight="bold", color="white",
            ha="center", va="center", transform=ax.transAxes, bbox=verdict_box)

    # Metrics table
    metrics_text = f"""
    Success Rates:
        G0 (pass/fail only): {rates['g0_rate']*100:.1f}% ({rates['g0_successes']}/{rates['n_pairs']})
        G3 (error+line):     {rates['g3_rate']*100:.1f}% ({rates['g3_successes']}/{rates['n_pairs']})

    Difference (G3 - G0): {rates['difference_pp']:+.1f} percentage points
    95% CI: [{rates['ci_lower_pp']:.1f}, {rates['ci_upper_pp']:.1f}] pp

    McNemar's Test:
        p-value: {mcnemar['pvalue']:.2e}
        Favors: {mcnemar['favors']}
        Significant: {'Yes' if mcnemar['significant'] else 'No'}

    Gate Conditions:
        Difference >= 10pp: {'PASS' if gate['difference_met'] else 'FAIL'} ({rates['difference_pp']:+.1f}pp)
        McNemar p < 0.05:   {'PASS' if gate['significant'] else 'FAIL'} (p={mcnemar['pvalue']:.2e})
        Favors G3:          {'PASS' if gate['favors_g3'] else 'FAIL'} (favors {mcnemar['favors']})

    Verdict: {gate['reason']}
    """

    ax.text(0.05, 0.7, metrics_text, fontsize=11, fontfamily="monospace",
            ha="left", va="top", transform=ax.transAxes)

    plt.tight_layout()

    # Save
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "gate_summary.png")
    plt.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close()

    return filepath
