import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns

from config import CFG, FIG_CFG


class OutputWriter:
    def merge_and_save(
        self,
        panel: pd.DataFrame,
        stats_df: pd.DataFrame,
        out_path: str,
    ) -> pd.DataFrame:
        diversity_cols = [
            "task_path",
            "unique_count",
            "total_rows",
            "paper_diversity_ratio_at_intro",
            "log_unique_paper_count_at_intro",
            "log_unique_paper_count_at_intro_z",
            "paper_diversity_ratio_at_intro_z",
        ]
        cols_to_merge = [c for c in diversity_cols if c in stats_df.columns]
        merged = panel.merge(stats_df[cols_to_merge], on="task_path", how="left")
        merged.to_csv(out_path, index=False)
        print(f"Output written: {out_path} ({len(merged)} rows)")
        return merged


class Visualizer:
    def __init__(self, figures_dir: str):
        self.figures_dir = figures_dir
        os.makedirs(figures_dir, exist_ok=True)

    def _save(self, fname: str) -> None:
        path = os.path.join(self.figures_dir, fname)
        plt.savefig(path, dpi=FIG_CFG.dpi, bbox_inches="tight")
        plt.close()
        print(f"Figure saved: {path}")

    def plot_gate_metrics(self, gate_results: list) -> None:
        gates = [r.gate for r in gate_results]
        values = [r.value for r in gate_results]
        thresholds = [r.threshold for r in gate_results]
        colors = [FIG_CFG.color_pass if r.passed else FIG_CFG.color_fail for r in gate_results]

        fig, ax = plt.subplots(figsize=FIG_CFG.fig_size_wide)
        x = np.arange(len(gates))
        bars = ax.bar(x, values, color=colors, alpha=0.85, zorder=3)
        for xi, (thresh, val) in enumerate(zip(thresholds, values)):
            ax.hlines(thresh, xi - 0.4, xi + 0.4, colors="black",
                      linestyles="--", linewidth=1.5, zorder=4)

        ax.set_xticks(x)
        ax.set_xticklabels(gates, fontsize=FIG_CFG.font_size_tick)
        ax.set_ylabel("Metric value", fontsize=FIG_CFG.font_size_label)
        ax.set_title("H-E1 Gate Metrics vs Thresholds", fontsize=FIG_CFG.font_size_title)
        ax.grid(axis="y", alpha=0.3, zorder=0)

        pass_patch = mpatches.Patch(color=FIG_CFG.color_pass, label="PASS")
        fail_patch = mpatches.Patch(color=FIG_CFG.color_fail, label="FAIL")
        thresh_line = plt.Line2D([0], [0], color="black", linestyle="--", label="Threshold")
        ax.legend(handles=[pass_patch, fail_patch, thresh_line],
                  fontsize=FIG_CFG.font_size_tick)

        plt.tight_layout()
        self._save(FIG_CFG.fname_gate_metrics)

    def plot_coverage_heatmap(self, joined: pd.DataFrame, panel: pd.DataFrame) -> None:
        all_tasks = panel["task_path"].unique()
        matched_tasks = set(
            joined[joined["matched_task"].notna()]["matched_task"].unique()
        )
        status = ["matched" if t in matched_tasks else "unmatched" for t in all_tasks]
        df_plot = pd.DataFrame({"task_path": all_tasks, "status": status})
        df_plot = df_plot.sort_values("status")

        colors = [FIG_CFG.color_pass if s == "matched" else FIG_CFG.color_fail
                  for s in df_plot["status"]]

        fig, ax = plt.subplots(figsize=(10, max(5, len(all_tasks) * 0.18)))
        ax.barh(range(len(df_plot)), [1] * len(df_plot), color=colors, alpha=0.85)
        ax.set_yticks(range(len(df_plot)))
        ax.set_yticklabels(df_plot["task_path"], fontsize=7)
        ax.set_xlabel("Coverage status", fontsize=FIG_CFG.font_size_label)
        ax.set_title(
            f"H-E1 Benchmark Coverage ({len(matched_tasks)}/{len(all_tasks)} matched)",
            fontsize=FIG_CFG.font_size_title,
        )
        pass_patch = mpatches.Patch(color=FIG_CFG.color_pass, label="Matched")
        fail_patch = mpatches.Patch(color=FIG_CFG.color_fail, label="Unmatched")
        ax.legend(handles=[pass_patch, fail_patch], fontsize=FIG_CFG.font_size_tick)
        plt.tight_layout()
        self._save(FIG_CFG.fname_coverage_heatmap)

    def plot_predictor_distributions(self, stats_df: pd.DataFrame) -> None:
        fig, axes = plt.subplots(1, 2, figsize=FIG_CFG.fig_size_wide)
        for ax, col, title in [
            (axes[0], "log_unique_paper_count_at_intro", "log(unique paper count)"),
            (axes[1], "paper_diversity_ratio_at_intro", "diversity ratio"),
        ]:
            if col in stats_df.columns:
                ax.hist(stats_df[col].dropna(), bins=20,
                        color=FIG_CFG.color_neutral, alpha=0.8, edgecolor="white")
            ax.set_xlabel(title, fontsize=FIG_CFG.font_size_label)
            ax.set_ylabel("Count", fontsize=FIG_CFG.font_size_label)
            ax.set_title(f"Distribution: {title}", fontsize=FIG_CFG.font_size_title)
            ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        self._save(FIG_CFG.fname_predictor_distributions)

    def plot_correlation_matrix(self, enriched_panel: pd.DataFrame) -> None:
        cox_cols = [
            "log_unique_paper_count_at_intro_z",
            "paper_diversity_ratio_at_intro_z",
            "task_age",
            "log_publication_volume",
            "benchmark_introduction_year",
        ]
        cols_avail = [c for c in cox_cols if c in enriched_panel.columns]
        if len(cols_avail) < 2:
            print("Skipping correlation matrix — insufficient columns")
            return
        corr = enriched_panel[cols_avail].corr()

        fig, ax = plt.subplots(figsize=FIG_CFG.fig_size_square)
        sns.heatmap(
            corr, annot=True, fmt=".2f",
            cmap=FIG_CFG.corr_palette,
            vmin=FIG_CFG.corr_vmin, vmax=FIG_CFG.corr_vmax,
            ax=ax, square=True,
            annot_kws={"size": FIG_CFG.font_size_tick},
        )
        ax.set_title("Cox Covariate Correlation Matrix", fontsize=FIG_CFG.font_size_title)
        plt.tight_layout()
        self._save(FIG_CFG.fname_correlation_matrix)

    def plot_partial_r2(self, gate_results: list) -> None:
        g1_results = [r for r in gate_results if r.gate == "G1"]
        g2_results = [r for r in gate_results if r.gate == "G2"]
        if not g1_results or not g2_results:
            print("Skipping partial R² plot — G1/G2 results missing")
            return

        labels = ["G1: log_count_z", "G2: diversity_ratio_z"]
        values = [g1_results[0].value, g2_results[0].value]
        colors = [
            FIG_CFG.color_pass if g1_results[0].passed else FIG_CFG.color_fail,
            FIG_CFG.color_pass if g2_results[0].passed else FIG_CFG.color_fail,
        ]

        fig, ax = plt.subplots(figsize=FIG_CFG.fig_size_single)
        ax.bar(labels, values, color=colors, alpha=0.85)
        ax.axhline(y=0.01, color="red", linestyle="--", linewidth=1.5, label="Threshold (0.01)")
        ax.set_ylabel("Partial R²", fontsize=FIG_CFG.font_size_label)
        ax.set_title("Time-Independence: Partial R² (G1, G2)", fontsize=FIG_CFG.font_size_title)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=FIG_CFG.font_size_tick)
        plt.tight_layout()
        self._save(FIG_CFG.fname_partial_r2)

    def save_all(
        self,
        joined: pd.DataFrame,
        stats_df: pd.DataFrame,
        gate_results: list,
        enriched_panel: pd.DataFrame,
        panel: pd.DataFrame,
    ) -> None:
        self.plot_gate_metrics(gate_results)
        self.plot_coverage_heatmap(joined, panel)
        self.plot_predictor_distributions(stats_df)
        self.plot_correlation_matrix(enriched_panel)
        self.plot_partial_r2(gate_results)
