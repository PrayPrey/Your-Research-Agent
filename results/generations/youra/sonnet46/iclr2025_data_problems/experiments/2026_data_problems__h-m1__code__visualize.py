"""
Visualization for H-M1: Conditional Log-Odds Demographic-Occupation Analysis.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CONFIG_TO_INTENSITY = {"C1": 10, "C2": 30, "C3": 50, "C4": 70, "C5": 90, "C6": None}
FASTTEXT_CONFIGS = ["C1", "C2", "C3", "C4", "C5"]


class Visualizer:
    """Generate all H-M1 figures."""

    def __init__(self, figures_dir: str, dpi: int = 150):
        self.figures_dir = Path(figures_dir)
        self.dpi = dpi
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Individual plots
    # ------------------------------------------------------------------

    def plot_spearman_gate(
        self,
        stats_results: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Plot Spearman ρ bar chart with 95% CI.
        Output: spearman_gate.png
        """
        if output_path is None:
            output_path = str(self.figures_dir / "spearman_gate.png")

        gate = stats_results.get("gate", {})
        spearman = stats_results.get("spearman", {})
        rho = spearman.get("rho", 0.0)
        pvalue = spearman.get("pvalue", 1.0)
        ci_low = gate.get("bootstrap_ci_low", rho - 0.1)
        ci_high = gate.get("bootstrap_ci_high", rho + 0.1)
        gate_passed = gate.get("gate_passed", False)

        fig, ax = plt.subplots(figsize=(6, 4))

        color = "#2ecc71" if gate_passed else "#e74c3c"
        ax.bar([0], [rho], color=color, alpha=0.8, width=0.4, label=f"Spearman ρ = {rho:.3f}")
        ax.errorbar(
            [0], [rho],
            yerr=[[rho - ci_low], [ci_high - rho]],
            fmt="none",
            color="black",
            capsize=6,
            linewidth=2,
        )
        ax.axhline(0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xticks([0])
        ax.set_xticklabels(["Spearman ρ\n(C1-C5)"])
        ax.set_ylabel("Correlation coefficient")
        ax.set_title(
            f"Spearman Gate: {'PASSED' if gate_passed else 'FAILED'}\n"
            f"ρ={rho:.3f}, p={pvalue:.4f}",
            fontsize=11,
        )
        ax.legend(loc="upper right", fontsize=9)
        plt.tight_layout()
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved spearman_gate plot to %s", output_path)
        return output_path

    def plot_log_odds_vs_intensity(
        self,
        mean_log_odds_per_config: Dict[str, float],
        ols_results: Dict[str, float],
        output_path: Optional[str] = None,
    ) -> str:
        """
        Scatter C1-C5 + OLS regression line, DoReMi C6 highlighted.
        Output: log_odds_vs_intensity.png
        """
        if output_path is None:
            output_path = str(self.figures_dir / "log_odds_vs_intensity.png")

        fig, ax = plt.subplots(figsize=(10, 6))

        # C1-C5 scatter
        x_fasttext = []
        y_fasttext = []
        for cid in FASTTEXT_CONFIGS:
            intensity = CONFIG_TO_INTENSITY[cid]
            if cid in mean_log_odds_per_config:
                x_fasttext.append(intensity)
                y_fasttext.append(mean_log_odds_per_config[cid])

        if x_fasttext:
            ax.scatter(x_fasttext, y_fasttext, s=80, color="#4C72B0", zorder=5, label="FastText C1-C5")

        # OLS regression line
        if ols_results and x_fasttext:
            coef = ols_results.get("coef", 0.0)
            intercept = ols_results.get("intercept", 0.0)
            x_line = np.linspace(min(x_fasttext) - 5, max(x_fasttext) + 5, 100)
            y_line = coef * x_line + intercept
            ax.plot(x_line, y_line, color="#4C72B0", linestyle="--", alpha=0.7,
                    label=f"OLS (β={coef:.4f}, R²={ols_results.get('r_squared', 0):.3f})")

        # C6 DoReMi
        if "C6" in mean_log_odds_per_config:
            c6_val = mean_log_odds_per_config["C6"]
            ax.axhline(c6_val, color="#DD8452", linestyle="-.", linewidth=2,
                       label=f"DoReMi C6 (mean log-odds={c6_val:.3f})")
            ax.annotate(
                f"C6 (DoReMi)\n{c6_val:.3f}",
                xy=(0.02, c6_val),
                xycoords=("axes fraction", "data"),
                fontsize=9,
                color="#DD8452",
            )

        ax.set_xlabel("FastText Filtering Intensity (percentile %)", fontsize=11)
        ax.set_ylabel("Mean Log-Odds (demographic-occupation)", fontsize=11)
        ax.set_title("Mean Log-Odds vs Filtering Intensity (C1-C5) + DoReMi C6", fontsize=12)
        ax.legend(fontsize=9)
        plt.tight_layout()
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved log_odds_vs_intensity plot to %s", output_path)
        return output_path

    def plot_log_odds_heatmap(
        self,
        log_odds_df: pd.DataFrame,
        config_id: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Demographic x occupation heatmap for one config using seaborn.
        Output: log_odds_heatmap_{config_id}.png
        """
        if output_path is None:
            output_path = str(self.figures_dir / f"log_odds_heatmap_{config_id}.png")

        try:
            import seaborn as sns
        except ImportError:
            logger.warning("seaborn not available; skipping heatmap")
            return output_path

        if log_odds_df.empty:
            logger.warning("Empty log_odds_df; skipping heatmap for %s", config_id)
            return output_path

        subset = log_odds_df[log_odds_df["config_id"] == config_id]
        if subset.empty:
            logger.warning("No data for config %s; skipping heatmap", config_id)
            return output_path

        # Pivot to demo x occ matrix
        pivot = subset.pivot_table(
            index="demographic",
            columns="occupation",
            values="log_odds",
            aggfunc="first",
        )

        # Replace inf values for visualization
        pivot = pivot.replace([np.inf, -np.inf], np.nan)

        fig, ax = plt.subplots(figsize=(14, 10))
        sns.heatmap(
            pivot,
            cmap="RdBu_r",
            center=0,
            ax=ax,
            cbar_kws={"label": "Log-Odds"},
            xticklabels=True,
            yticklabels=True,
        )
        ax.set_title(f"Log-Odds Heatmap: Demographic × Occupation [{config_id}]", fontsize=12)
        ax.set_xlabel("Occupation", fontsize=10)
        ax.set_ylabel("Demographic", fontsize=10)
        plt.xticks(rotation=45, ha="right", fontsize=7)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved heatmap for %s to %s", config_id, output_path)
        return output_path

    def plot_fasttext_vs_doremi(
        self,
        log_odds_df: pd.DataFrame,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Violin plots C5 vs C6 log-odds distributions.
        Output: fasttext_vs_doremi.png
        """
        if output_path is None:
            output_path = str(self.figures_dir / "fasttext_vs_doremi.png")

        if log_odds_df.empty:
            logger.warning("Empty log_odds_df; skipping fasttext_vs_doremi plot")
            return output_path

        subset = log_odds_df[log_odds_df["config_id"].isin(["C5", "C6"])].copy()
        subset = subset[np.isfinite(subset["log_odds"])]

        if subset.empty:
            logger.warning("No finite log-odds for C5/C6; skipping violin plot")
            return output_path

        fig, ax = plt.subplots(figsize=(8, 6))

        groups = []
        labels = []
        for cid in ["C5", "C6"]:
            vals = subset[subset["config_id"] == cid]["log_odds"].values
            if len(vals) > 0:
                groups.append(vals)
                labels.append(cid)

        if groups:
            parts = ax.violinplot(groups, positions=range(len(groups)), showmedians=True)
            for pc in parts["bodies"]:
                pc.set_alpha(0.7)
            if "C5" in labels and "C6" in labels:
                parts["bodies"][labels.index("C5")].set_facecolor("#4C72B0")
                parts["bodies"][labels.index("C6")].set_facecolor("#DD8452")

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels([f"{l}\n({'FastText @90%' if l == 'C5' else 'DoReMi'})" for l in labels])
        ax.set_ylabel("Log-Odds (demographic-occupation)", fontsize=11)
        ax.set_title("Log-Odds Distribution: FastText C5 vs DoReMi C6", fontsize=12)
        plt.tight_layout()
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved fasttext_vs_doremi plot to %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def generate_all(
        self,
        log_odds_df: pd.DataFrame,
        mean_log_odds_per_config: Dict[str, float],
        stats_results: Dict[str, Any],
    ) -> List[str]:
        """
        Generate all H-M1 figures.

        Returns list of saved file paths.
        """
        saved = []

        ols_results = stats_results.get("ols", {})

        try:
            saved.append(self.plot_spearman_gate(stats_results))
        except Exception as e:
            logger.error("Failed to plot spearman gate: %s", e)

        try:
            saved.append(self.plot_log_odds_vs_intensity(mean_log_odds_per_config, ols_results))
        except Exception as e:
            logger.error("Failed to plot log_odds_vs_intensity: %s", e)

        try:
            saved.append(self.plot_fasttext_vs_doremi(log_odds_df))
        except Exception as e:
            logger.error("Failed to plot fasttext_vs_doremi: %s", e)

        # Heatmaps for C1 and C5
        for cid in ["C1", "C5"]:
            try:
                saved.append(self.plot_log_odds_heatmap(log_odds_df, cid))
            except Exception as e:
                logger.error("Failed to plot heatmap for %s: %s", cid, e)

        logger.info("Generated %d figures", len(saved))
        return saved
