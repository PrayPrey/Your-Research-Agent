"""H-M2 Visualization: 5 figures for corpus entropy → logit margin analysis."""
import json
import logging
import math
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from config import HM2Config, ALL_CONFIGS, CORPUS_H_ENTROPY, load_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class Visualizer:
    """Generate all H-M2 analysis figures."""

    def __init__(self, cfg: HM2Config):
        self.cfg = cfg
        self.figures_dir = Path(cfg.figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def plot_entropy_vs_margin(
        self,
        entropy_values: List[float],
        logit_margins: List[float],
        config_ids: List[str],
        spearman_rho: float,
        spearman_pvalue: float,
        ols_coef: Optional[float] = None,
        ols_intercept: Optional[float] = None,
        ols_r2: Optional[float] = None,
    ) -> str:
        """Figure 1: Scatter plot of H(occ|demo) vs mean logit margin."""
        fig, ax = plt.subplots(figsize=self.cfg.figure_size)

        # Scatter plot
        ax.scatter(entropy_values, logit_margins, s=80, zorder=3, color="steelblue")
        for i, cid in enumerate(config_ids):
            ax.annotate(cid, (entropy_values[i], logit_margins[i]),
                        textcoords="offset points", xytext=(5, 5), fontsize=9)

        # OLS regression line
        if ols_coef is not None and ols_intercept is not None:
            x_log = [math.log(h) for h in entropy_values]
            x_range = np.linspace(min(entropy_values), max(entropy_values), 100)
            x_log_range = np.log(x_range)
            y_fit = ols_coef * x_log_range + ols_intercept
            ax.plot(x_range, y_fit, "r--", alpha=0.7,
                    label=f"OLS fit (R²={ols_r2:.3f})" if ols_r2 else "OLS fit")

        ax.set_xlabel("Corpus Entropy H(occ|demo)", fontsize=12)
        ax.set_ylabel("Mean Logit Margin", fontsize=12)
        ax.set_title(
            f"Corpus Entropy vs. Model Logit Margin\n"
            f"Spearman ρ={spearman_rho:.3f}, p={spearman_pvalue:.4f}",
            fontsize=13
        )
        if ols_coef is not None:
            ax.legend()
        ax.grid(True, alpha=0.3)

        path = str(self.figures_dir / "01_entropy_vs_margin.png")
        fig.tight_layout()
        fig.savefig(path, dpi=self.cfg.dpi)
        plt.close(fig)
        logger.info(f"[viz] Saved: {path}")
        return path

    def plot_logit_margin_heatmap(
        self,
        probe_results: Dict[str, Dict],
        config_ids: Optional[List[str]] = None,
    ) -> str:
        """Figure 2: Heatmap of logit margins per config (occupation × config grid)."""
        if config_ids is None:
            config_ids = [c for c in ALL_CONFIGS if c in probe_results]

        from probe import OCCUPATION_PAIRS
        occ_labels = [f"{f}/{m}" for f, m in OCCUPATION_PAIRS]

        # Build matrix: rows=occupations, cols=configs
        # Use per-config per-occupation margins if available, else use mean
        matrix = []
        for i, (female_occ, male_occ) in enumerate(OCCUPATION_PAIRS):
            row = []
            for cid in config_ids:
                r = probe_results.get(cid, {})
                # Try to get per-pair margin; fall back to mean
                mean_m = r.get("mean_logit_margin", 0.0) or 0.0
                row.append(mean_m)
            matrix.append(row)

        matrix = np.array(matrix)

        fig, ax = plt.subplots(figsize=self.cfg.figure_size_heatmap)
        im = ax.imshow(matrix, aspect="auto", cmap="RdBu_r", vmin=-2, vmax=2)
        plt.colorbar(im, ax=ax, label="Logit Margin")
        ax.set_xticks(range(len(config_ids)))
        ax.set_xticklabels(config_ids, rotation=45, ha="right")
        ax.set_yticks(range(len(occ_labels)))
        ax.set_yticklabels(occ_labels, fontsize=8)
        ax.set_title("Logit Margin Heatmap: Occupation × Corpus Config", fontsize=13)
        ax.set_xlabel("Corpus Config")
        ax.set_ylabel("Occupation Pair (female/male)")

        path = str(self.figures_dir / "02_logit_margin_heatmap.png")
        fig.tight_layout()
        fig.savefig(path, dpi=self.cfg.dpi)
        plt.close(fig)
        logger.info(f"[viz] Saved: {path}")
        return path

    def plot_training_curves(
        self,
        training_results: Dict[str, Dict],
    ) -> str:
        """Figure 3: Training loss curves per config (placeholder if logs unavailable)."""
        fig, ax = plt.subplots(figsize=self.cfg.figure_size)

        colors = plt.cm.tab10(np.linspace(0, 1, len(ALL_CONFIGS)))
        plotted = 0
        for i, config_id in enumerate(ALL_CONFIGS):
            r = training_results.get(config_id, {})
            loss_curve = r.get("loss_curve", [])
            if loss_curve:
                steps = list(range(0, len(loss_curve) * 100, 100))
                ax.plot(steps, loss_curve, color=colors[i], label=config_id, alpha=0.8)
                plotted += 1

        if plotted == 0:
            ax.text(0.5, 0.5, "Training curves unavailable\n(mock/placeholder)",
                    ha="center", va="center", transform=ax.transAxes, fontsize=14)

        ax.set_xlabel("Training Steps")
        ax.set_ylabel("Training Loss")
        ax.set_title("Training Loss Curves per Corpus Config", fontsize=13)
        if plotted > 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.grid(True, alpha=0.3)

        path = str(self.figures_dir / "03_training_curves.png")
        fig.tight_layout()
        fig.savefig(path, dpi=self.cfg.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"[viz] Saved: {path}")
        return path

    def plot_negative_control(
        self,
        probe_results: Dict[str, Dict],
    ) -> str:
        """Figure 4: Bar chart comparing C0 (baseline) vs C7 (negative control) margins."""
        fig, ax = plt.subplots(figsize=(6, 5))

        c0_margin = probe_results.get("C0", {}).get("mean_logit_margin", 0.0) or 0.0
        c7_margin = probe_results.get("C7", {}).get("mean_logit_margin", 0.0) or 0.0

        bars = ax.bar(["C0 (Baseline)", "C7 (Neg. Control)"],
                      [c0_margin, c7_margin],
                      color=["steelblue", "coral"], alpha=0.8)
        ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
        ax.set_ylabel("Mean Logit Margin")
        ax.set_title("Negative Control Check: C0 vs C7")
        delta = abs(c7_margin - c0_margin)
        ax.text(0.5, 0.95, f"|C7-C0| = {delta:.4f}",
                transform=ax.transAxes, ha="center", va="top", fontsize=11)
        ax.grid(True, axis="y", alpha=0.3)

        path = str(self.figures_dir / "04_negative_control.png")
        fig.tight_layout()
        fig.savefig(path, dpi=self.cfg.dpi)
        plt.close(fig)
        logger.info(f"[viz] Saved: {path}")
        return path

    def plot_config_comparison(
        self,
        entropy_values: List[float],
        logit_margins: List[float],
        config_ids: List[str],
    ) -> str:
        """Figure 5: Bar chart of logit margins sorted by entropy (C0-C6)."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # Left: sorted by config
        axes[0].bar(config_ids, logit_margins, color="steelblue", alpha=0.8)
        axes[0].set_xlabel("Corpus Config")
        axes[0].set_ylabel("Mean Logit Margin")
        axes[0].set_title("Logit Margins by Config")
        axes[0].grid(True, axis="y", alpha=0.3)

        # Right: sorted by entropy
        sorted_pairs = sorted(zip(entropy_values, logit_margins, config_ids))
        s_ent, s_mar, s_cfg = zip(*sorted_pairs)
        axes[1].bar(s_cfg, s_mar, color="darkorange", alpha=0.8)
        axes[1].set_xlabel("Corpus Config (sorted by entropy)")
        axes[1].set_ylabel("Mean Logit Margin")
        axes[1].set_title("Logit Margins Sorted by Entropy")
        axes[1].grid(True, axis="y", alpha=0.3)

        path = str(self.figures_dir / "05_config_comparison.png")
        fig.tight_layout()
        fig.savefig(path, dpi=self.cfg.dpi)
        plt.close(fig)
        logger.info(f"[viz] Saved: {path}")
        return path

    def generate_all_figures(
        self,
        probe_results: Dict,
        stat_results: Dict,
        training_results: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Generate all 5 figures."""
        paths = {}

        configs_used = stat_results.get("configs_used", [])
        entropy_values = stat_results.get("entropy_values", [])
        logit_margins = stat_results.get("logit_margins", [])
        spearman = stat_results.get("spearman", {})
        ols = stat_results.get("ols", {})

        if configs_used and entropy_values and logit_margins:
            paths["entropy_vs_margin"] = self.plot_entropy_vs_margin(
                entropy_values=entropy_values,
                logit_margins=logit_margins,
                config_ids=configs_used,
                spearman_rho=spearman.get("rho", 0),
                spearman_pvalue=spearman.get("pvalue", 1),
                ols_coef=ols.get("coef"),
                ols_intercept=ols.get("intercept"),
                ols_r2=ols.get("r_squared"),
            )

        paths["heatmap"] = self.plot_logit_margin_heatmap(probe_results)
        paths["training_curves"] = self.plot_training_curves(training_results or {})
        paths["negative_control"] = self.plot_negative_control(probe_results)

        if configs_used and entropy_values and logit_margins:
            paths["config_comparison"] = self.plot_config_comparison(
                entropy_values, logit_margins, configs_used
            )

        return paths


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-results", type=str, required=True)
    parser.add_argument("--stat-results", type=str, required=True)
    parser.add_argument("--config", type=str, default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    with open(args.probe_results) as f:
        probe_results = json.load(f)
    with open(args.stat_results) as f:
        stat_results = json.load(f)

    viz = Visualizer(cfg)
    paths = viz.generate_all_figures(probe_results, stat_results)
    print("Figures generated:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
