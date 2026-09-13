"""
H-M4: Visualization — 5 figures for matching method comparison.
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]
COLORS = {"token_matched": "#2196F3", "step_matched": "#FF5722"}


def plot_correlation_comparison_bar(r_token, r_step, ci_token, ci_step, out_path):
    fig, ax = plt.subplots(figsize=(7, 5))
    conditions = ["Token-count\nmatched", "Step\nmatched"]
    values = [r_token, r_step]
    colors = [COLORS["token_matched"], COLORS["step_matched"]]
    yerr_lo = [r_token - ci_token[0], r_step - ci_step[0]]
    yerr_hi = [ci_token[1] - r_token, ci_step[1] - r_step]

    bars = ax.bar(conditions, values, color=colors, width=0.4, alpha=0.85,
                  yerr=[yerr_lo, yerr_hi], capsize=8, ecolor="black", error_kw={"linewidth": 1.5})

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_ylabel("Pearson r (contamination vs accuracy differential)", fontsize=11)
    ax.set_title("H-M4: Correlation Strength by Checkpoint Matching Method\n"
                 "(with 95% Bootstrap CI)", fontsize=12)
    ax.set_ylim(-0.3, 1.0)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.03,
                f"r={val:.3f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    delta_r = r_token - r_step
    ax.text(0.97, 0.05, f"Δr = {delta_r:+.3f}", transform=ax.transAxes,
            ha="right", fontsize=10, color="darkgreen" if delta_r > 0 else "darkred",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_scatter_two_panel(cont_est, token_diffs, step_diffs, r_token, r_step, out_path):
    cont_vec = [cont_est[b] for sz in MODEL_SIZES for b in BENCHMARKS]
    diff_token = [token_diffs[sz][b] for sz in MODEL_SIZES for b in BENCHMARKS]
    diff_step  = [step_diffs[sz][b]  for sz in MODEL_SIZES for b in BENCHMARKS]
    bench_labels = [b[:4] for sz in MODEL_SIZES for b in BENCHMARKS]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
    for ax, diffs, r, cond, color in [
        (axes[0], diff_token, r_token, "Token-count matched", COLORS["token_matched"]),
        (axes[1], diff_step, r_step, "Step matched", COLORS["step_matched"]),
    ]:
        ax.scatter(cont_vec, diffs, color=color, alpha=0.7, s=50, zorder=3)
        # regression line
        m, b = np.polyfit(cont_vec, diffs, 1)
        x_line = np.linspace(min(cont_vec) - 0.01, max(cont_vec) + 0.01, 100)
        ax.plot(x_line, m * x_line + b, color=color, linewidth=2)
        ax.axhline(0, color="gray", linewidth=0.7, linestyle="--")
        ax.set_xlabel("Contamination Estimate", fontsize=10)
        ax.set_ylabel("Accuracy Differential (dedup - Pile)", fontsize=10)
        ax.set_title(f"{cond}\nr={r:.3f}", fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle("H-M4: Contamination vs Accuracy Differential by Matching Method", fontsize=12)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_differential_bar_chart(aggregated, out_path):
    n_bench = len(BENCHMARKS)
    n_sizes = len(MODEL_SIZES)
    x = np.arange(n_bench)
    width = 0.1
    offsets = np.linspace(-(n_sizes - 1) * width, (n_sizes - 1) * width, n_sizes * 2)

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, size in enumerate(MODEL_SIZES):
        token_vals = [aggregated["token_matched"][size][b] for b in BENCHMARKS]
        step_vals  = [aggregated["step_matched"][size][b] for b in BENCHMARKS]
        off_t = offsets[i * 2]
        off_s = offsets[i * 2 + 1]
        ax.bar(x + off_t, token_vals, width=width * 0.9, alpha=0.8, color=COLORS["token_matched"],
               label=f"{size} token-matched" if i == 0 else "_")
        ax.bar(x + off_s, step_vals, width=width * 0.9, alpha=0.8, color=COLORS["step_matched"],
               label=f"{size} step-matched" if i == 0 else "_")

    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([b.replace("_", "\n") for b in BENCHMARKS], fontsize=10)
    ax.set_ylabel("Accuracy Differential (dedup-Pile − Pile)", fontsize=10)
    ax.set_title("H-M4: Per-benchmark Differentials — Token-matched vs Step-matched\n"
                 "(4 model sizes)", fontsize=11)

    patch_t = mpatches.Patch(color=COLORS["token_matched"], label="Token-count matched")
    patch_s = mpatches.Patch(color=COLORS["step_matched"], label="Step matched")
    ax.legend(handles=[patch_t, patch_s], fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_bias_decomposition(aggregated, out_path):
    """Per model size: volume bias vs contamination component."""
    token_diffs = aggregated["token_matched"]
    step_diffs = aggregated["step_matched"]

    sizes = MODEL_SIZES
    token_means = [np.mean([token_diffs[sz][b] for b in BENCHMARKS]) for sz in sizes]
    step_means  = [np.mean([step_diffs[sz][b] for b in BENCHMARKS]) for sz in sizes]
    volume_bias = [s - t for s, t in zip(step_means, token_means)]

    x = np.arange(len(sizes))
    width = 0.3
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, token_means, width=width, alpha=0.85, color=COLORS["token_matched"],
           label="Token-matched mean differential")
    ax.bar(x + width/2, volume_bias, width=width, alpha=0.85, color="#9C27B0",
           label="Volume bias (step − token, uniform shift)")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Pythia\n{sz}" for sz in sizes], fontsize=10)
    ax.set_ylabel("Mean Accuracy Differential", fontsize=10)
    ax.set_title("H-M4: Volume Bias Decomposition by Model Size", fontsize=11)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_correlation_summary_table(comparison_results, out_path):
    """Summary table figure with r, p, CI for both conditions + delta_r."""
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis("off")

    col_labels = ["Condition", "Pearson r", "p-value", "Spearman ρ", "95% CI", "n"]
    row_data = [
        ["Token-count matched",
         f"{comparison_results['r_token_matched']:.4f}",
         f"{comparison_results['p_token_matched']:.4f}",
         f"{comparison_results['rho_token_matched']:.4f}",
         f"[{comparison_results['ci_token_matched'][0]:.3f}, {comparison_results['ci_token_matched'][1]:.3f}]",
         "16"],
        ["Step matched",
         f"{comparison_results['r_step_matched']:.4f}",
         f"{comparison_results['p_step_matched']:.4f}",
         f"{comparison_results['rho_step_matched']:.4f}",
         f"[{comparison_results['ci_step_matched'][0]:.3f}, {comparison_results['ci_step_matched'][1]:.3f}]",
         "16"],
        ["Δ (token − step)",
         f"{comparison_results['delta_r']:+.4f}",
         "—", "—", "—", "—"],
    ]

    tbl = ax.table(cellText=row_data, colLabels=col_labels, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1, 1.6)

    # Color header
    for j in range(len(col_labels)):
        tbl[0, j].set_facecolor("#37474F")
        tbl[0, j].set_text_props(color="white", fontweight="bold")

    tbl[1, 0].set_facecolor("#E3F2FD")
    tbl[2, 0].set_facecolor("#FBE9E7")
    tbl[3, 0].set_facecolor("#F3E5F5")

    gate = comparison_results.get("gate_verdict", "")
    ax.set_title(f"H-M4: Correlation Comparison Summary  |  Gate: {gate}", fontsize=11,
                 fontweight="bold", pad=10)
    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    results_dir = base / "results"
    figures_dir = base / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    with open(results_dir / "aggregated_differentials.json") as f:
        aggregated = json.load(f)
    with open(results_dir / "correlation_comparison.json") as f:
        comp = json.load(f)

    cont_est = comp["contamination_estimates"]

    plot_correlation_comparison_bar(
        comp["r_token_matched"], comp["r_step_matched"],
        comp["ci_token_matched"], comp["ci_step_matched"],
        str(figures_dir / "fig_01_correlation_comparison_bar.png"))

    plot_scatter_two_panel(
        cont_est, aggregated["token_matched"], aggregated["step_matched"],
        comp["r_token_matched"], comp["r_step_matched"],
        str(figures_dir / "fig_02_scatter_two_panel.png"))

    plot_differential_bar_chart(aggregated, str(figures_dir / "fig_03_differential_bar_chart.png"))
    plot_bias_decomposition(aggregated, str(figures_dir / "fig_04_bias_decomposition.png"))
    plot_correlation_summary_table(comp, str(figures_dir / "fig_05_correlation_summary_table.png"))

    print("All 5 figures generated.")
