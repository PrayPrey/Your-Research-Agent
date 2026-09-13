"""Cross-task comparison: compare h-e1 (SQuAD) and h-c1 (HotpotQA) scaling laws."""
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from config import Paths, ComparisonConfig


def load_scaling_fit(path: str) -> dict:
    """Load scaling fit JSON from h-e1 or h-c1."""
    with open(path, "r") as f:
        return json.load(f)


def compare_alphas(fit_squad: dict, fit_hotpot: dict, output_json: str | None = None) -> dict:
    """Compute |alpha_squad - alpha_hotpot|, CI overlap, pass/fail."""
    paths = Paths()
    cfg = ComparisonConfig()
    output_json = output_json or paths.comparison_json

    alpha_squad = fit_squad["alpha"]
    alpha_hotpot = fit_hotpot["alpha"]
    alpha_diff = abs(alpha_squad - alpha_hotpot)

    ci_squad = (fit_squad["alpha_ci_low"], fit_squad["alpha_ci_high"])
    ci_hotpot = (fit_hotpot["alpha_ci_low"], fit_hotpot["alpha_ci_high"])
    ci_overlap = ci_squad[1] >= ci_hotpot[0] and ci_hotpot[1] >= ci_squad[0]

    pass_diff = alpha_diff <= cfg.alpha_diff_threshold
    pass_ci = ci_overlap if cfg.require_ci_overlap else True
    overall_pass = pass_diff and pass_ci

    result = {
        "alpha_squad": float(alpha_squad),
        "alpha_hotpot": float(alpha_hotpot),
        "alpha_diff": float(alpha_diff),
        "alpha_diff_threshold": cfg.alpha_diff_threshold,
        "ci_squad": list(ci_squad),
        "ci_hotpot": list(ci_hotpot),
        "ci_overlap": ci_overlap,
        "pass_diff": pass_diff,
        "pass_ci": pass_ci,
        "overall_pass": overall_pass,
    }

    os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Comparison saved: {output_json}")

    return result


def plot_dual_scaling(
    optimal_squad: pd.DataFrame,
    optimal_hotpot: pd.DataFrame,
    fit_squad: dict,
    fit_hotpot: dict,
    comparison: dict,
    output_png: str | None = None,
) -> None:
    """Generate dual log-log scaling plot with fit lines and CI bands."""
    paths = Paths()
    output_png = output_png or paths.dual_plot_png
    os.makedirs(os.path.dirname(output_png) or ".", exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Dual scaling curves
    log_n_squad = np.log10(optimal_squad["N"].values)
    log_r_squad = np.log10(optimal_squad["r_opt"].values)
    log_n_hotpot = np.log10(optimal_hotpot["N"].values)
    log_r_hotpot = np.log10(optimal_hotpot["r_opt"].values)

    ax1.scatter(log_n_squad, log_r_squad, alpha=0.7, s=100, c="steelblue",
                edgecolors="black", linewidth=0.5, label="SQuAD-v2")
    ax1.scatter(log_n_hotpot, log_r_hotpot, alpha=0.7, s=100, c="darkorange",
                edgecolors="black", linewidth=0.5, label="HotpotQA")

    x_line = np.linspace(min(log_n_squad.min(), log_n_hotpot.min()) - 0.1,
                          max(log_n_squad.max(), log_n_hotpot.max()) + 0.1, 100)

    for fit, color, name in [(fit_squad, "steelblue", "SQuAD"),
                               (fit_hotpot, "darkorange", "HotpotQA")]:
        alpha, c = fit["alpha"], fit["c"]
        y_line = np.log10(c * (10 ** x_line) ** alpha)
        ax1.plot(x_line, y_line, color=color, linewidth=2,
                 label=f"{name}: α={alpha:.3f}")

        ci_low, ci_high = fit["alpha_ci_low"], fit["alpha_ci_high"]
        y_low = np.log10(c * (10 ** x_line) ** ci_low)
        y_high = np.log10(c * (10 ** x_line) ** ci_high)
        ax1.fill_between(x_line, y_low, y_high, alpha=0.15, color=color)

    ax1.set_xlabel("log₁₀(N) - Model Parameters", fontsize=12)
    ax1.set_ylabel("log₁₀(r_opt) - Optimal Rank", fontsize=12)
    ax1.set_title("LoRA Scaling Law: Cross-Task Comparison", fontsize=14)
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Plot 2: |Δα| bar with threshold
    categories = ["SQuAD-v2", "HotpotQA", "|Δα|"]
    values = [comparison["alpha_squad"], comparison["alpha_hotpot"], comparison["alpha_diff"]]
    colors = ["steelblue", "darkorange", "green" if comparison["pass_diff"] else "red"]

    bars = ax2.bar(categories, values, color=colors, edgecolor="black", linewidth=0.5)
    ax2.axhline(y=comparison["alpha_diff_threshold"], color="red", linestyle="--",
                linewidth=2, label=f"Threshold: {comparison['alpha_diff_threshold']}")

    ax2.set_ylabel("α (Scaling Exponent)", fontsize=12)
    ax2.set_title("Scaling Exponent Comparison", fontsize=14)
    ax2.legend(loc="upper right")

    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                 f"{val:.3f}", ha="center", va="bottom", fontsize=11)

    status = "PASS" if comparison["overall_pass"] else "FAIL"
    ax2.text(0.95, 0.05, f"CI Overlap: {comparison['ci_overlap']}\nStatus: {status}",
             transform=ax2.transAxes, fontsize=10, verticalalignment="bottom",
             horizontalalignment="right", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_png, dpi=150)
    plt.close()
    print(f"Dual plot saved: {output_png}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cross-task scaling comparison")
    parser.add_argument("--h-e1-fit", default=None, help="h-e1 scaling fit JSON")
    parser.add_argument("--h-c1-fit", default=None, help="h-c1 scaling fit JSON")
    parser.add_argument("--h-e1-optimal", default=None, help="h-e1 optimal ranks CSV")
    parser.add_argument("--h-c1-optimal", default=None, help="h-c1 optimal ranks CSV")
    parser.add_argument("--output-dir", default="results")
    parser.add_argument("--figures-dir", default="figures")

    args = parser.parse_args()
    paths = Paths()

    fit_squad = load_scaling_fit(args.h_e1_fit or paths.h_e1_scaling_fit_json)
    fit_hotpot = load_scaling_fit(args.h_c1_fit or paths.scaling_fit_json)

    comparison = compare_alphas(
        fit_squad, fit_hotpot,
        os.path.join(args.output_dir, "h-c1_cross_task_comparison.json"),
    )

    optimal_squad = pd.read_csv(args.h_e1_optimal or paths.h_e1_optimal_ranks_csv)
    optimal_hotpot = pd.read_csv(args.h_c1_optimal or paths.optimal_ranks_csv)

    plot_dual_scaling(
        optimal_squad, optimal_hotpot, fit_squad, fit_hotpot, comparison,
        os.path.join(args.figures_dir, "h-c1_dual_scaling_plot.png"),
    )

    print("\n=== Cross-Task Comparison ===")
    print(f" α_SQuAD: {comparison['alpha_squad']:.4f}")
    print(f" α_HotpotQA: {comparison['alpha_hotpot']:.4f}")
    print(f" |Δα|: {comparison['alpha_diff']:.4f} (threshold: {comparison['alpha_diff_threshold']})")
    print(f" CI Overlap: {comparison['ci_overlap']}")
    print(f" VERDICT: {'PASS' if comparison['overall_pass'] else 'FAIL'}")
