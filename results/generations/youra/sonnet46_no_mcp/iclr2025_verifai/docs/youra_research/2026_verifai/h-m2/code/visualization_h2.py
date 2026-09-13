import json
import logging
import os
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from config import H2VisualizationConfig

logger = logging.getLogger(__name__)


class H2Visualizer:
    def __init__(self, cfg: H2VisualizationConfig, figures_dir: str) -> None:
        self.cfg = cfg
        self.figures_dir = figures_dir
        os.makedirs(figures_dir, exist_ok=True)

    def _save_fig(self, fig, name: str) -> str:
        path = os.path.join(self.figures_dir, name)
        fig.savefig(path, dpi=self.cfg.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved figure: {path}")
        return path

    def plot_gate_metrics(self, c_score_results: Dict, z3_results: Dict) -> str:
        fig, axes = plt.subplots(1, 2, figsize=(self.cfg.fig_width, self.cfg.fig_height))
        c = self.cfg.colors

        # C_score panel
        ax = axes[0]
        c_score = c_score_results.get("c_score", 0.0)
        ci_lower = c_score_results.get("ci_lower", 0.0)
        ci_upper = c_score_results.get("ci_upper", 0.0)
        color = c["pass_color"] if c_score > 0 else c["fail_color"]
        ax.bar(["C_score"], [c_score], color=color, alpha=0.8)
        ax.errorbar(["C_score"], [c_score], yerr=[[c_score - ci_lower], [ci_upper - c_score]],
                    fmt="none", color="black", capsize=5)
        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        ax.set_ylabel("C_score")
        ax.set_title("C_score (Conditioned)\nwith 95% Bootstrap CI")

        # ΔP panel
        ax2 = axes[1]
        delta_p = z3_results.get("delta_p", 0.0)
        z3_ci_lower = z3_results.get("ci_lower", 0.0)
        z3_ci_upper = z3_results.get("ci_upper", 0.0)
        color2 = c["pass_color"] if delta_p > 0.05 else c["fail_color"]
        ax2.bar(["ΔP(Z3)"], [delta_p], color=color2, alpha=0.8)
        ax2.errorbar(["ΔP(Z3)"], [delta_p], yerr=[[delta_p - z3_ci_lower], [z3_ci_upper - delta_p]],
                     fmt="none", color="black", capsize=5)
        ax2.axhline(0, color="black", linestyle="--", linewidth=1)
        ax2.axhline(0.05, color="orange", linestyle=":", linewidth=1, label="threshold=0.05")
        ax2.set_ylabel("ΔP")
        ax2.set_title("Z3 Eligibility Δ\nwith 95% Bootstrap CI")
        ax2.legend()

        fig.suptitle("h-m2 Gate Metrics", fontweight="bold")
        fig.tight_layout()
        return self._save_fig(fig, self.cfg.figures["gate_metrics"])

    def plot_jaccard_heatmap(self, c_score_results: Dict) -> str:
        fig, axes = plt.subplots(1, 3, figsize=(self.cfg.fig_width * 1.5, self.cfg.fig_height))

        def draw_venn_panel(ax, title, j_obs, e_j, c_score):
            vals = [j_obs, e_j, max(0, c_score)]
            labels = ["J_obs", "E[J]", "C_score"]
            colors = [self.cfg.colors["baseline"], self.cfg.colors["syncode"], self.cfg.colors["mypy"]]
            ax.bar(labels, vals, color=colors, alpha=0.8)
            ax.set_title(title)
            ax.set_ylim(0, max(vals) * 1.3 if max(vals) > 0 else 1)

        draw_venn_panel(axes[0], "Raw (all problems)",
                        c_score_results.get("raw_j_obs", 0),
                        c_score_results.get("raw_e_j", 0),
                        c_score_results.get("raw_c_score", 0))
        draw_venn_panel(axes[1], "Conditioned stratum",
                        c_score_results.get("j_obs", 0),
                        c_score_results.get("e_j", 0),
                        c_score_results.get("c_score", 0))

        # Quintile panel
        quintile_results = c_score_results.get("quintile_results", {})
        if quintile_results:
            q_labels = [f"Q{k}" for k in sorted(quintile_results.keys())]
            q_c_scores = [quintile_results[k].get("c_score", 0) for k in sorted(quintile_results.keys())]
            axes[2].bar(q_labels, q_c_scores, color=self.cfg.colors["mypy"], alpha=0.8)
            axes[2].axhline(0, color="black", linestyle="--")
            axes[2].set_title("C_score by Difficulty Quintile")
        else:
            axes[2].text(0.5, 0.5, "No quintile data", ha="center", va="center")

        fig.suptitle("Jaccard Complement Analysis", fontweight="bold")
        fig.tight_layout()
        return self._save_fig(fig, self.cfg.figures["jaccard_heatmap"])

    def plot_fmd_distribution(self, fmd_classifications: Dict) -> str:
        strata_counts = {"syntax": 0, "type": 0, "functional": 0, "success": 0, "other": 0}
        for labels in fmd_classifications.values():
            for lbl in labels:
                strata_counts[lbl if lbl in strata_counts else "other"] += 1

        labels = [k for k, v in strata_counts.items() if v > 0]
        sizes = [strata_counts[k] for k in labels]
        colors = [self.cfg.colors["fail_color"], self.cfg.colors["mypy"],
                  self.cfg.colors["syncode"], self.cfg.colors["pass_color"],
                  self.cfg.colors["baseline"]][:len(labels)]

        fig, ax = plt.subplots(figsize=(self.cfg.fig_width, self.cfg.fig_height))
        ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax.set_title("Failure Mode Distribution (FMD) — All 164×20 Samples")
        return self._save_fig(fig, self.cfg.figures["fmd_distribution"])

    def plot_z3_eligibility_comparison(self, z3_results: Dict) -> str:
        fig, ax = plt.subplots(figsize=(self.cfg.fig_width, self.cfg.fig_height))
        p_base = z3_results.get("p_baseline", 0.0)
        p_mypy = z3_results.get("p_post_mypy", 0.0)
        ci_lower = z3_results.get("ci_lower", 0.0)
        ci_upper = z3_results.get("ci_upper", 0.0)
        delta = z3_results.get("delta_p", 0.0)
        xs = ["Baseline", "Post-mypy"]
        ys = [p_base, p_mypy]
        bar_colors = [self.cfg.colors["baseline"], self.cfg.colors["mypy"]]
        bars = ax.bar(xs, ys, color=bar_colors, alpha=0.8)
        ax.errorbar(["Post-mypy"], [p_mypy], yerr=[[p_mypy - (p_base + ci_lower)], [(p_base + ci_upper) - p_mypy]],
                    fmt="none", color="black", capsize=5)
        ax.set_ylabel("P(Z3-eligible)")
        ax.set_title(f"Z3 Eligibility: Baseline vs Post-mypy\nΔP={delta:.3f} (95% CI [{ci_lower:.3f}, {ci_upper:.3f}])")
        return self._save_fig(fig, self.cfg.figures["z3_eligibility_comparison"])

    def plot_repair_convergence(self, repair_pool: Dict) -> str:
        round_success = {1: 0, 2: 0, 3: 0}
        total = 0
        for records in repair_pool.values():
            for rec in records:
                total += 1
                rounds = rec.get("rounds_used", 0)
                success = rec.get("success", False)
                if success and rounds >= 1:
                    round_success[min(rounds, 3)] += 1

        cumulative = []
        cum = 0
        for r in [1, 2, 3]:
            cum += round_success.get(r, 0)
            cumulative.append(cum / total if total > 0 else 0)

        fig, ax = plt.subplots(figsize=(self.cfg.fig_width, self.cfg.fig_height))
        ax.plot([1, 2, 3], cumulative, marker="o", color=self.cfg.colors["mypy"], linewidth=2)
        ax.set_xlabel("Repair Rounds")
        ax.set_ylabel("Cumulative Repair Success Fraction")
        ax.set_title("mypy Repair Convergence (Cumulative)")
        ax.set_xticks([1, 2, 3])
        ax.set_ylim(0, max(cumulative) * 1.2 if cumulative else 0.1)
        return self._save_fig(fig, self.cfg.figures["repair_convergence"])

    def plot_quintile_c_score(self, c_score_results: Dict) -> str:
        quintile_results = c_score_results.get("quintile_results", {})
        fig, ax = plt.subplots(figsize=(self.cfg.fig_width, self.cfg.fig_height))
        if quintile_results:
            qs = sorted(quintile_results.keys())
            c_scores = [quintile_results[q].get("c_score", 0) for q in qs]
            ax.bar([f"Q{q}" for q in qs], c_scores, color=self.cfg.colors["mypy"], alpha=0.8)
            ax.axhline(0, color="black", linestyle="--")
            ax.set_ylabel("C_score")
            ax.set_title("C_score by Difficulty Quintile\n(Q0=hardest, Q4=easiest)")
        else:
            ax.text(0.5, 0.5, "No quintile data", ha="center", va="center")
        return self._save_fig(fig, self.cfg.figures["quintile_c_score"])

    def generate_all(
        self,
        c_score_results: Dict,
        z3_results: Dict,
        fmd_classifications: Dict,
        repair_pool: Dict,
    ) -> List[str]:
        figures = []
        try:
            figures.append(self.plot_gate_metrics(c_score_results, z3_results))
        except Exception as e:
            logger.error(f"gate_metrics failed: {e}")
        try:
            figures.append(self.plot_jaccard_heatmap(c_score_results))
        except Exception as e:
            logger.error(f"jaccard_heatmap failed: {e}")
        try:
            figures.append(self.plot_fmd_distribution(fmd_classifications))
        except Exception as e:
            logger.error(f"fmd_distribution failed: {e}")
        try:
            figures.append(self.plot_z3_eligibility_comparison(z3_results))
        except Exception as e:
            logger.error(f"z3_eligibility_comparison failed: {e}")
        try:
            figures.append(self.plot_repair_convergence(repair_pool))
        except Exception as e:
            logger.error(f"repair_convergence failed: {e}")
        try:
            figures.append(self.plot_quintile_c_score(c_score_results))
        except Exception as e:
            logger.error(f"quintile_c_score failed: {e}")
        return figures
