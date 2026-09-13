from __future__ import annotations
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

if TYPE_CHECKING:
    from config import Config

logger = logging.getLogger(__name__)

FIGURE_SIZES = {
    "corpus_comparison_bar": (10, 6),
    "contamination_heatmap": (14, 16),
    "corpus_pair_differences": (10, 5),
    "wimbd_consistency_scatter": (8, 8),
    "per_corpus_rankings": (12, 10),
    "dunn_posthoc_heatmap": (6, 5),
}
FIGURE_DPI = 150
CORPUS_COLORS = {"pile": "#1f77b4", "c4": "#ff7f0e", "redpajama": "#2ca02c"}
HEATMAP_CMAP = "YlOrRd"
FONT_SIZES = {"title": 14, "axis_label": 12, "tick": 10, "annotation": 10}
REFERENCE_LINE_STYLE = {
    "color": "red", "linestyle": "--", "linewidth": 1.5, "alpha": 0.7, "label": "2pp threshold"
}
LEGEND_LOC = "upper right"


class Visualizer:
    def __init__(self, config: "Config"):
        self.config = config
        Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    def _save(self, name: str) -> None:
        path = Path(self.config.figures_dir) / name
        plt.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
        plt.close()
        logger.info(f"Saved figure: {path}")

    def plot_corpus_comparison_bar(
        self, matrix_wide: pd.DataFrame, kruskal_H: float, kruskal_p: float
    ) -> None:
        """Bar chart: mean rate per corpus ±1 SE; 2pp reference line; H/p annotation."""
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["corpus_comparison_bar"], dpi=FIGURE_DPI)
        corpora = ["pile", "c4", "redpajama"]
        means = [matrix_wide[c].mean() * 100 for c in corpora]
        sems = [matrix_wide[c].sem() * 100 for c in corpora]
        colors = [CORPUS_COLORS[c] for c in corpora]
        bars = ax.bar(corpora, means, yerr=sems, color=colors, capsize=5, alpha=0.85)
        ax.axhline(y=2.0, **REFERENCE_LINE_STYLE)
        ax.set_xlabel("Corpus", fontsize=FONT_SIZES["axis_label"])
        ax.set_ylabel("Mean Contamination Rate (%)", fontsize=FONT_SIZES["axis_label"])
        ax.set_title("Cross-Corpus Contamination Comparison (59 sub-tasks)", fontsize=FONT_SIZES["title"])
        ax.tick_params(labelsize=FONT_SIZES["tick"])
        ax.text(0.98, 0.95, f"Kruskal-Wallis H={kruskal_H:.2f}, p={kruskal_p:.2e}",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=FONT_SIZES["annotation"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        ax.legend(loc=LEGEND_LOC, fontsize=FONT_SIZES["tick"])
        self._save("corpus_comparison_barplot.png")

    def plot_contamination_heatmap(self, matrix_wide: pd.DataFrame) -> None:
        """59×3 heatmap; rows sorted by mean rate desc."""
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["contamination_heatmap"], dpi=FIGURE_DPI)
        data = matrix_wide.copy() * 100  # to percent
        data["mean"] = data.mean(axis=1)
        data = data.sort_values("mean", ascending=False).drop(columns="mean")
        sns.heatmap(data, ax=ax, cmap=HEATMAP_CMAP, fmt=".1f", annot=False,
                    linewidths=0.3, cbar_kws={"label": "Contamination Rate (%)"})
        ax.set_title("Contamination Matrix: 59 Sub-tasks × 3 Corpora", fontsize=FONT_SIZES["title"])
        ax.set_xlabel("Corpus", fontsize=FONT_SIZES["axis_label"])
        ax.set_ylabel("Benchmark Sub-task", fontsize=FONT_SIZES["axis_label"])
        ax.tick_params(labelsize=7)
        self._save("contamination_matrix_heatmap.png")

    def plot_corpus_pair_differences(self, matrix_wide: pd.DataFrame) -> None:
        """Pairwise mean difference bars with 2pp threshold line."""
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["corpus_pair_differences"], dpi=FIGURE_DPI)
        means = {c: matrix_wide[c].mean() * 100 for c in ["pile", "c4", "redpajama"]}
        pairs = [("pile", "c4"), ("pile", "redpajama"), ("c4", "redpajama")]
        labels = [f"{a}−{b}" for a, b in pairs]
        diffs = [abs(means[a] - means[b]) for a, b in pairs]
        colors = ["steelblue" if d > 2.0 else "salmon" for d in diffs]
        ax.bar(labels, diffs, color=colors, alpha=0.85)
        ax.axhline(y=2.0, **REFERENCE_LINE_STYLE)
        ax.set_xlabel("Corpus Pair", fontsize=FONT_SIZES["axis_label"])
        ax.set_ylabel("|Mean Difference| (pp)", fontsize=FONT_SIZES["axis_label"])
        ax.set_title("Pairwise Corpus Mean Contamination Differences", fontsize=FONT_SIZES["title"])
        ax.tick_params(labelsize=FONT_SIZES["tick"])
        ax.legend(loc=LEGEND_LOC, fontsize=FONT_SIZES["tick"])
        self._save("corpus_pair_differences.png")

    def plot_wimbd_consistency_scatter(
        self, pile_rates: pd.Series, wimbd_rates: dict, rho: float
    ) -> None:
        """H-M1 Pile column vs WIMBD published rates; Spearman rho annotated."""
        common = pile_rates.index.intersection(list(wimbd_rates.keys()))
        if len(common) < 3:
            logger.warning("Not enough common subtasks for WIMBD scatter plot")
            return
        x = np.array([wimbd_rates[k] * 100 for k in common])
        y = pile_rates.loc[common].values * 100
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["wimbd_consistency_scatter"], dpi=FIGURE_DPI)
        ax.scatter(x, y, alpha=0.7, color=CORPUS_COLORS["pile"])
        for i, subtask in enumerate(common):
            ax.annotate(subtask, (x[i], y[i]), fontsize=6, alpha=0.7)
        lim = max(x.max(), y.max()) * 1.05
        ax.plot([0, lim], [0, lim], "k--", alpha=0.5, label="y=x")
        ax.set_xlabel("WIMBD Published Rate (%)", fontsize=FONT_SIZES["axis_label"])
        ax.set_ylabel("H-M1 Pile Rate (%)", fontsize=FONT_SIZES["axis_label"])
        ax.set_title("WIMBD Consistency: H-M1 Pile vs Published Rates", fontsize=FONT_SIZES["title"])
        ax.text(0.05, 0.95, f"Spearman ρ={rho:.3f}",
                transform=ax.transAxes, va="top", fontsize=FONT_SIZES["annotation"],
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        ax.legend(loc=LEGEND_LOC, fontsize=FONT_SIZES["tick"])
        self._save("wimbd_consistency_scatter.png")

    def plot_per_corpus_rankings(self, matrix_wide: pd.DataFrame) -> None:
        """Top-10 and bottom-10 sub-tasks per corpus (horizontal bar)."""
        fig, axes = plt.subplots(3, 2, figsize=FIGURE_SIZES["per_corpus_rankings"], dpi=FIGURE_DPI)
        for row, corpus in enumerate(["pile", "c4", "redpajama"]):
            rates = (matrix_wide[corpus] * 100).sort_values(ascending=False)
            top10 = rates.head(10)
            bot10 = rates.tail(10).sort_values()
            axes[row, 0].barh(top10.index, top10.values, color=CORPUS_COLORS[corpus], alpha=0.85)
            axes[row, 0].set_title(f"{corpus} — Top-10", fontsize=FONT_SIZES["tick"])
            axes[row, 0].tick_params(labelsize=7)
            axes[row, 1].barh(bot10.index, bot10.values, color=CORPUS_COLORS[corpus], alpha=0.5)
            axes[row, 1].set_title(f"{corpus} — Bottom-10", fontsize=FONT_SIZES["tick"])
            axes[row, 1].tick_params(labelsize=7)
        plt.suptitle("Per-Corpus Contamination Rankings", fontsize=FONT_SIZES["title"])
        plt.tight_layout()
        self._save("per_corpus_rankings.png")

    def plot_dunn_posthoc_heatmap(self, posthoc_df: pd.DataFrame) -> None:
        """Dunn's test p-value heatmap for 3 corpus pairs."""
        fig, ax = plt.subplots(figsize=FIGURE_SIZES["dunn_posthoc_heatmap"], dpi=FIGURE_DPI)
        sns.heatmap(posthoc_df, ax=ax, annot=True, fmt=".3f", cmap="RdYlGn_r",
                    vmin=0, vmax=1, linewidths=0.5,
                    cbar_kws={"label": "Bonferroni-adjusted p-value"})
        ax.set_title("Dunn Post-hoc Test (Bonferroni)", fontsize=FONT_SIZES["title"])
        self._save("dunn_posthoc_heatmap.png")
