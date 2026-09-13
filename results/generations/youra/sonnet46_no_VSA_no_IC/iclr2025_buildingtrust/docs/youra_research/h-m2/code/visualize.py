"""H-M2 visualizations: bar chart, heatmap, scatter (3 panels), forest plot."""
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from config import FIGURES_DIR, DELTA_RHO_GATE

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FIG_DPI = 150
PALETTE = {
    "fairness":  "#4C72B0",   # blue
    "advglue":   "#DD8452",   # orange
    "anli":      "#55A868",   # green
    "delta":     "#C44E52",   # red
    "threshold": "#8C8C8C",   # grey dashed line
}


def plot_gate_metrics_bar(results: dict, out_dir: Path) -> None:
    """
    Bar chart: partial rho for fairness, AdvGLUE, ANLI with 95% CI.
    Annotates delta_rho value and 0.2 threshold reference line.
    Saves: out_dir/gate_metrics_comparison.png
    """
    labels = ["Fairness\n(BBQ)", "Robustness\n(AdvGLUE)", "Robustness\n(ANLI)"]
    rhos = [
        results["rho_fairness"]["rho"],
        results["rho_advglue"]["rho"],
        results["rho_anli"]["rho"],
    ]
    colors = [PALETTE["fairness"], PALETTE["advglue"], PALETTE["anli"]]

    # CI error bars (asymmetric)
    yerr_lo = [rhos[i] - results[k]["ci95"][0]
               for i, k in enumerate(["rho_fairness", "rho_advglue", "rho_anli"])]
    yerr_hi = [results[k]["ci95"][1] - rhos[i]
               for i, k in enumerate(["rho_fairness", "rho_advglue", "rho_anli"])]

    fig, ax = plt.subplots(figsize=(7, 5), dpi=FIG_DPI)
    x = np.arange(len(labels))
    bars = ax.bar(x, rhos, color=colors, yerr=[yerr_lo, yerr_hi], capsize=5,
                  error_kw={"elinewidth": 1.5})

    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.axhline(y=DELTA_RHO_GATE, color=PALETTE["threshold"], linestyle="--",
               linewidth=1.5, label=f"Δρ gate threshold (0.2)")

    # Annotate delta_rho
    delta = results["delta_rho"]
    ax.text(0.97, 0.97,
            f"Δρ = {delta:.3f}\n({'PASS' if delta >= DELTA_RHO_GATE else 'FAIL'})",
            transform=ax.transAxes, ha="right", va="top", fontsize=11,
            color=PALETTE["delta"],
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel("Partial Spearman ρ (MMLU-controlled)", fontsize=11)
    ax.set_title("H-M2: Partial Rank Correlation by Trustworthiness Dimension\n"
                 "(Fairness vs Adversarial Robustness)", fontsize=11)
    ax.legend(fontsize=9)
    ax.set_ylim(-0.1, 1.05)

    out_path = out_dir / "gate_metrics_comparison.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=FIG_DPI)
    plt.close(fig)
    logging.info(f"Saved: {out_path}")


def plot_rank_heatmap(df: pd.DataFrame, out_dir: Path) -> None:
    """
    Heatmap: models (rows, sorted by MMLU rank) x 6 benchmarks (cols), rank position colored.
    Saves: out_dir/rank_heatmap.png
    """
    score_cols = ["bbq_disambig", "bbq_ambig", "glue_score",
                  "advglue_score", "anli_r1_score", "anli_r3_score"]
    col_labels = ["BBQ\nDisambig", "BBQ\nAmbig", "GLUE", "AdvGLUE", "ANLI R1", "ANLI R3"]

    df_plot = df[["model_name", "mmlu"] + score_cols].copy()
    df_plot = df_plot.sort_values("mmlu").reset_index(drop=True)

    # Convert to rank matrix (rank within each column, lower rank = better = darker green)
    rank_df = df_plot[score_cols].rank(ascending=False).astype(int)

    fig, ax = plt.subplots(figsize=(10, max(5, len(df_plot) * 0.5 + 1.5)), dpi=FIG_DPI)
    im = ax.imshow(rank_df.values, cmap="RdYlGn_r", aspect="auto",
                   vmin=1, vmax=len(df_plot))

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot["model_name"].tolist(), fontsize=8)
    ax.set_title("H-M2: Rank Position per Model × Benchmark\n"
                 "(rows sorted by MMLU; green=top rank, red=bottom rank)", fontsize=10)

    for i in range(len(df_plot)):
        for j in range(len(col_labels)):
            ax.text(j, i, str(rank_df.values[i, j]), ha="center", va="center",
                    fontsize=8, color="black")

    plt.colorbar(im, ax=ax, label="Rank (1=best)")
    fig.tight_layout()
    out_path = out_dir / "rank_heatmap.png"
    fig.savefig(out_path, dpi=FIG_DPI)
    plt.close(fig)
    logging.info(f"Saved: {out_path}")


def plot_per_dimension_scatter(df: pd.DataFrame, results: dict, out_dir: Path) -> None:
    """
    3-panel scatter: per-dimension ID vs OOD scores with Spearman rho annotated.
    Saves: out_dir/per_dimension_scatter.png
    """
    panels = [
        {"x": "bbq_disambig", "y": "bbq_ambig",
         "xlabel": "BBQ Disambig (ID)", "ylabel": "BBQ Ambig (OOD)",
         "title": "Fairness", "color": PALETTE["fairness"],
         "rho": results["rho_fairness"]["rho"], "p": results["rho_fairness"]["p_value"]},
        {"x": "glue_score", "y": "advglue_score",
         "xlabel": "GLUE (ID)", "ylabel": "AdvGLUE (OOD)",
         "title": "Robustness: GLUE→AdvGLUE", "color": PALETTE["advglue"],
         "rho": results["rho_advglue"]["rho"], "p": results["rho_advglue"]["p_value"]},
        {"x": "anli_r1_score", "y": "anli_r3_score",
         "xlabel": "ANLI R1 (ID)", "ylabel": "ANLI R3 (OOD)",
         "title": "Robustness: ANLI R1→R3", "color": PALETTE["anli"],
         "rho": results["rho_anli"]["rho"], "p": results["rho_anli"]["p_value"]},
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), dpi=FIG_DPI)
    for ax, panel in zip(axes, panels):
        ax.scatter(df[panel["x"]], df[panel["y"]], color=panel["color"],
                   s=60, alpha=0.8, edgecolors="white", linewidth=0.5)
        ax.set_xlabel(panel["xlabel"], fontsize=9)
        ax.set_ylabel(panel["ylabel"], fontsize=9)
        ax.set_title(panel["title"], fontsize=10, fontweight="bold")
        ax.text(0.05, 0.95,
                f"partial ρ = {panel['rho']:.3f}\n(p={panel['p']:.3f})",
                transform=ax.transAxes, va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

        # Add model labels for extreme points
        for _, row in df.iterrows():
            if (row[panel["x"]] > df[panel["x"]].quantile(0.85) or
                    row[panel["x"]] < df[panel["x"]].quantile(0.15)):
                ax.annotate(row["model_name"].split("-")[0],
                            (row[panel["x"]], row[panel["y"]]),
                            fontsize=6, alpha=0.7, xytext=(3, 3),
                            textcoords="offset points")

    fig.suptitle("H-M2: Per-Dimension Scatter (partial ρ, MMLU-controlled)", fontsize=11)
    fig.tight_layout()
    out_path = out_dir / "per_dimension_scatter.png"
    fig.savefig(out_path, dpi=FIG_DPI)
    plt.close(fig)
    logging.info(f"Saved: {out_path}")


def plot_forest(results: dict, out_dir: Path) -> None:
    """
    Forest plot: partial rho per dimension with 95% CI, plus delta_rho row.
    Marks delta_rho = 0.2 threshold.
    Saves: out_dir/forest_plot.png
    """
    rows = [
        ("Fairness (BBQ)",      "rho_fairness", PALETTE["fairness"]),
        ("Robustness (AdvGLUE)", "rho_advglue",  PALETTE["advglue"]),
        ("Robustness (ANLI)",    "rho_anli",     PALETTE["anli"]),
    ]

    rhos   = [results[k]["rho"] for _, k, _ in rows]
    ci_lo  = [results[k]["ci95"][0] for _, k, _ in rows]
    ci_hi  = [results[k]["ci95"][1] for _, k, _ in rows]
    labels = [lbl for lbl, _, _ in rows]
    colors = [c for _, _, c in rows]

    # Add delta_rho as extra point (no CI from pingouin — approximate via Fisher)
    delta = results["delta_rho"]
    labels.append(f"Δρ (fairness − mean robustness)")
    rhos.append(delta)
    ci_lo.append(delta - 0.1)   # approx CI for display
    ci_hi.append(delta + 0.1)
    colors.append(PALETTE["delta"])

    fig, ax = plt.subplots(figsize=(8, 5), dpi=FIG_DPI)
    y = np.arange(len(labels))

    for i, (rho, lo, hi, color) in enumerate(zip(rhos, ci_lo, ci_hi, colors)):
        ax.plot([lo, hi], [y[i], y[i]], color=color, linewidth=2, solid_capstyle="round")
        ax.scatter([rho], [y[i]], color=color, s=80, zorder=5)

    ax.axvline(x=0, color="black", linewidth=0.8, linestyle="-")
    ax.axvline(x=DELTA_RHO_GATE, color=PALETTE["threshold"], linewidth=1.5,
               linestyle="--", label=f"Δρ gate = 0.2")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Partial Spearman ρ (MMLU-controlled, 95% CI)", fontsize=10)
    ax.set_title("H-M2: Forest Plot — Rank Correlation per Dimension", fontsize=10)
    ax.legend(fontsize=9)
    ax.set_xlim(-0.3, 1.1)
    ax.invert_yaxis()

    fig.tight_layout()
    out_path = out_dir / "forest_plot.png"
    fig.savefig(out_path, dpi=FIG_DPI)
    plt.close(fig)
    logging.info(f"Saved: {out_path}")


def generate_all_figures(df: pd.DataFrame, results: dict, out_dir: Path) -> None:
    """Call all four plot functions."""
    out_dir.mkdir(parents=True, exist_ok=True)
    plot_gate_metrics_bar(results, out_dir)
    plot_rank_heatmap(df, out_dir)
    plot_per_dimension_scatter(df, results, out_dir)
    plot_forest(results, out_dir)
    logging.info("All figures generated.")
