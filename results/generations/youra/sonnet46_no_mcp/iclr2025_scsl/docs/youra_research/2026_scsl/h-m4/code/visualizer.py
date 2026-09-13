import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, List
from config import ExperimentConfig

FIGURE_SIZE = (8, 5)
FIGURE_DPI = 150
BAR_COLOR = "#4C72B0"
SCATTER_COLOR = "#DD8452"
ERM_COLOR = "#4C72B0"
DFR_COLOR = "#DD8452"
CI_ALPHA = 0.2
ERROR_CAPSIZE = 4
FONT_SIZE_TITLE = 13
FONT_SIZE_LABEL = 11
FONT_SIZE_ANNOT = 10
GATE_PASS_COLOR = "green"
GATE_FAIL_COLOR = "red"


class Visualizer:
    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg
        os.makedirs(cfg.paths.figures_dir, exist_ok=True)

    def plot_gate_metrics(
        self,
        aggregated: Dict[int, Dict[str, float]],
        pearson_r: float,
        t_star: float,
        r_threshold: float = 0.7,
    ) -> str:
        epochs = sorted(aggregated.keys())
        improvements = [aggregated[e]["mean_wga_improvement"] for e in epochs]
        stds = [aggregated[e]["std_wga_improvement"] for e in epochs]

        fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        x = np.arange(len(epochs))
        ax.bar(x, improvements, yerr=stds, color=BAR_COLOR, capsize=ERROR_CAPSIZE, alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([f"Epoch {e}" for e in epochs], fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel("Mean WGA Improvement (DFR - ERM)", fontsize=FONT_SIZE_LABEL)
        ax.set_title(f"DFR WGA Improvement vs Checkpoint Epoch (r={pearson_r:.3f}, t*={t_star})",
                     fontsize=FONT_SIZE_TITLE)
        color = GATE_PASS_COLOR if pearson_r > r_threshold else GATE_FAIL_COLOR
        ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
        ax.annotate(f"Pearson r={pearson_r:.3f}", xy=(0.98, 0.95), xycoords="axes fraction",
                    ha="right", fontsize=FONT_SIZE_ANNOT, color=color)
        plt.tight_layout()
        path = os.path.join(self.cfg.paths.figures_dir, "gate_metrics.png")
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_scatter_correlation(
        self,
        epochs_past_tstar: List[float],
        improvements: List[float],
        pearson_r: float,
        pearson_p: float,
    ) -> str:
        x = np.array(epochs_past_tstar)
        y = np.array(improvements)

        fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        ax.scatter(x, y, color=SCATTER_COLOR, zorder=5, s=60)

        # Regression line
        if len(x) > 1:
            coeffs = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = np.polyval(coeffs, x_line)
            ax.plot(x_line, y_line, color="black", linewidth=1.5)

            # 95% CI via residuals
            y_pred = np.polyval(coeffs, x)
            residuals = y - y_pred
            std_res = np.std(residuals)
            ax.fill_between(x_line, y_line - 1.96 * std_res, y_line + 1.96 * std_res,
                            alpha=CI_ALPHA, color="gray")

        ax.set_xlabel("Epochs Past t*", fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel("Mean WGA Improvement", fontsize=FONT_SIZE_LABEL)
        ax.set_title(f"Correlation: WGA Improvement vs (Epoch - t*)\n"
                     f"Pearson r={pearson_r:.3f}, p={pearson_p:.4f}",
                     fontsize=FONT_SIZE_TITLE)
        plt.tight_layout()
        path = os.path.join(self.cfg.paths.figures_dir, "scatter_correlation.png")
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_wga_curves(
        self,
        results_per_seed: Dict[int, Dict[int, Dict[str, float]]],
        conditions: List[int],
    ) -> str:
        seeds = list(results_per_seed.keys())
        epochs = sorted(conditions)

        erm_per_epoch = {e: [] for e in epochs}
        dfr_per_epoch = {e: [] for e in epochs}
        for seed in seeds:
            for e in epochs:
                metrics = results_per_seed[seed].get(e, {})
                if metrics:
                    erm_per_epoch[e].append(metrics["erm_wga"])
                    dfr_per_epoch[e].append(metrics["dfr_wga"])

        erm_means = [np.mean(erm_per_epoch[e]) for e in epochs]
        erm_stds = [np.std(erm_per_epoch[e]) for e in epochs]
        dfr_means = [np.mean(dfr_per_epoch[e]) for e in epochs]
        dfr_stds = [np.std(dfr_per_epoch[e]) for e in epochs]

        fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        x = np.arange(len(epochs))
        ax.errorbar(x, erm_means, yerr=erm_stds, label="ERM WGA",
                    color=ERM_COLOR, marker="o", capsize=ERROR_CAPSIZE)
        ax.errorbar(x, dfr_means, yerr=dfr_stds, label="DFR WGA",
                    color=DFR_COLOR, marker="s", capsize=ERROR_CAPSIZE)
        ax.set_xticks(x)
        ax.set_xticklabels([f"Ep {e}" for e in epochs], fontsize=FONT_SIZE_LABEL)
        ax.set_ylabel("Worst-Group Accuracy", fontsize=FONT_SIZE_LABEL)
        ax.set_title("ERM vs DFR WGA Across Checkpoint Epochs", fontsize=FONT_SIZE_TITLE)
        ax.legend()
        plt.tight_layout()
        path = os.path.join(self.cfg.paths.figures_dir, "wga_curves.png")
        plt.savefig(path)
        plt.close(fig)
        return path

    def plot_monotonicity_check(
        self,
        improvements: List[float],
        conditions: List[int],
    ) -> str:
        diffs = [improvements[i + 1] - improvements[i] for i in range(len(improvements) - 1)]
        labels = [f"Ep{conditions[i]}→Ep{conditions[i+1]}" for i in range(len(diffs))]

        fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
        colors = [GATE_PASS_COLOR if d > 0 else GATE_FAIL_COLOR for d in diffs]
        ax.bar(range(len(diffs)), diffs, color=colors)
        ax.set_xticks(range(len(diffs)))
        ax.set_xticklabels(labels, fontsize=FONT_SIZE_LABEL, rotation=15)
        ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
        ax.set_ylabel("Δ WGA Improvement", fontsize=FONT_SIZE_LABEL)
        ax.set_title("Monotonicity Check: Consecutive WGA Improvement Differences",
                     fontsize=FONT_SIZE_TITLE)
        plt.tight_layout()
        path = os.path.join(self.cfg.paths.figures_dir, "monotonicity_check.png")
        plt.savefig(path)
        plt.close(fig)
        return path

    def save_all(
        self,
        results_per_seed: Dict,
        aggregated: Dict,
        correlation_results: Dict,
        t_star: float,
    ) -> List[str]:
        import math
        paths = []
        pearson_r = correlation_results.get("pearson_r", float("nan"))
        r_display = pearson_r if not (isinstance(pearson_r, float) and math.isnan(pearson_r)) else 0.0
        paths.append(self.plot_gate_metrics(aggregated, r_display, t_star))
        conditions = sorted(aggregated.keys())
        paths.append(self.plot_wga_curves(results_per_seed, conditions))
        # Scatter and monotonicity require ≥2 conditions
        if len(conditions) >= 2:
            p_one = correlation_results.get("pearson_p_onetailed", 1.0)
            if isinstance(p_one, float) and math.isnan(p_one):
                p_one = 1.0
            paths.append(self.plot_scatter_correlation(
                correlation_results["epochs_past_tstar"],
                correlation_results["improvements"],
                r_display,
                p_one,
            ))
            paths.append(self.plot_monotonicity_check(
                correlation_results["improvements"],
                conditions,
            ))
        return paths
