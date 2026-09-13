import os
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class HM1Visualizer:

    def __init__(self, figures_dir: str) -> None:
        self.figures_dir = figures_dir
        os.makedirs(figures_dir, exist_ok=True)

    def _save(self, name: str) -> None:
        for ext in ("pdf", "png"):
            plt.savefig(os.path.join(self.figures_dir, f"{name}.{ext}"), dpi=150, bbox_inches="tight")

    def plot_gate_metrics(
        self,
        baseline_mean: float,
        syncode_mean: float,
        ci_lower: float,
        ci_upper: float,
        delta_ast: float,
        gate_result: str,
    ) -> None:
        fig, ax = plt.subplots(figsize=(6, 5))

        colors = {"PASS": "green", "PARTIAL": "orange", "FAIL": "red"}
        gate_color = colors.get(gate_result, "gray")

        bars = ax.bar(
            ["Baseline", "SynCode"],
            [baseline_mean, syncode_mean],
            color=["steelblue", "darkorange"],
        )

        # Error bar on SynCode: asymmetric CI around delta_ast
        err_lo = max(0, syncode_mean - ci_lower)
        err_hi = max(0, ci_upper - syncode_mean)
        ax.errorbar(
            1, syncode_mean,
            yerr=[[err_lo], [err_hi]],
            fmt="none", color="black", capsize=5,
        )

        ax.axhline(baseline_mean, linestyle="--", color="gray", linewidth=1)
        ax.set_ylabel("AST Parse Failure Rate", fontsize=11)
        ax.set_title("Gate Metrics: Baseline vs SynCode", fontsize=12)

        annotation = f"Δ_ast={delta_ast:.4f}\n95% CI [{ci_lower:.4f}, {ci_upper:.4f}]\n{gate_result}"
        ax.text(
            0.98, 0.97, annotation,
            transform=ax.transAxes,
            ha="right", va="top",
            fontsize=10, color=gate_color,
            bbox=dict(boxstyle="round", alpha=0.1, color=gate_color),
        )

        plt.tight_layout()
        self._save("gate_metrics")
        plt.close(fig)

    def plot_per_problem_scatter(
        self,
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
        task_ids: List[str],
    ) -> None:
        fig, ax = plt.subplots(figsize=(7, 6))

        # Color by quartile of baseline_rate
        quartiles = np.percentile(baseline_rates, [25, 50, 75])
        colors = []
        for b in baseline_rates:
            if b <= quartiles[0]:
                colors.append(0)
            elif b <= quartiles[1]:
                colors.append(1)
            elif b <= quartiles[2]:
                colors.append(2)
            else:
                colors.append(3)

        sc = ax.scatter(baseline_rates, syncode_rates, c=colors, cmap="RdYlGn_r", alpha=0.7, s=30)

        # Diagonal reference line y=x
        lim_max = max(max(baseline_rates), max(syncode_rates)) + 0.05
        ax.plot([0, lim_max], [0, lim_max], "k--", linewidth=1, label="No improvement")

        n_improved = int(np.sum(syncode_rates < baseline_rates))
        ax.set_xlabel("Baseline Failure Rate", fontsize=11)
        ax.set_ylabel("SynCode Failure Rate", fontsize=11)
        ax.set_title(f"Per-Problem Failure Rates: {n_improved}/164 problems improved", fontsize=11)
        plt.colorbar(sc, ax=ax, label="Quartile")
        plt.tight_layout()
        self._save("per_problem_scatter")
        plt.close(fig)

    def plot_fmd_comparison(
        self,
        baseline_dist: Dict[str, float],
        syncode_dist: Dict[str, float],
    ) -> None:
        categories = ["syntax", "type", "functional", "success"]
        b_vals = [baseline_dist.get(c, 0.0) for c in categories]
        s_vals = [syncode_dist.get(c, 0.0) for c in categories]

        x = np.arange(len(categories))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width / 2, b_vals, width, label="Baseline", color="steelblue")
        ax.bar(x + width / 2, s_vals, width, label="SynCode", color="darkorange")

        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylabel("Proportion of Samples", fontsize=11)
        ax.set_title("Failure Mode Distribution: Baseline vs SynCode", fontsize=12)
        ax.legend(fontsize=11)
        plt.tight_layout()
        self._save("fmd_comparison")
        plt.close(fig)

    def plot_transition_heatmap(
        self,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
        task_ids: List[str],
    ) -> None:
        n_problems = len(task_ids)
        n_samples = 20
        grid = np.ones((n_problems, n_samples), dtype=int)  # 1 = no_gain default

        for prob_idx, task_id in enumerate(task_ids):
            b_recs = baseline_pool.get(task_id, [])
            s_recs = syncode_pool.get(task_id, [])
            b_by_sample = {r.get("sample_idx", i): r for i, r in enumerate(b_recs)}
            s_by_sample = {r.get("sample_idx", i): r for i, r in enumerate(s_recs)}

            for samp_idx in range(n_samples):
                b = b_by_sample.get(samp_idx)
                s = s_by_sample.get(samp_idx)
                if b is None:
                    continue
                b_valid = b.get("ast_valid", False)
                s_valid = s.get("ast_valid", False) if s else False

                if b_valid:
                    grid[prob_idx, samp_idx] = 0  # already_correct
                elif s_valid:
                    grid[prob_idx, samp_idx] = 2  # SynCode helps (transition)
                else:
                    grid[prob_idx, samp_idx] = 1  # no_gain

        fig, ax = plt.subplots(figsize=(10, 8))
        cmap = plt.cm.get_cmap("RdYlGn", 3)
        im = ax.imshow(grid, cmap=cmap, vmin=0, vmax=2, aspect="auto")
        cbar = plt.colorbar(im, ax=ax, ticks=[0, 1, 2])
        cbar.set_ticklabels(["already correct", "no gain", "SynCode helps"])
        ax.set_xlabel("Sample Index (0-19)", fontsize=11)
        ax.set_ylabel("Problem Index (0-163)", fontsize=11)
        ax.set_title("SynCode Transition Heatmap (164×20)", fontsize=12)
        plt.tight_layout()
        self._save("transition_heatmap")
        plt.close(fig)

    def save_all(
        self,
        ast_results: dict,
        bootstrap_results: dict,
        fmd_results: dict,
        baseline_pool: Dict[str, List[dict]],
        syncode_pool: Dict[str, List[dict]],
        baseline_rates: np.ndarray,
        syncode_rates: np.ndarray,
        task_ids: List[str],
    ) -> None:
        self.plot_gate_metrics(
            baseline_mean=ast_results["baseline_mean"],
            syncode_mean=ast_results["syncode_mean"],
            ci_lower=bootstrap_results["ci_lower"],
            ci_upper=bootstrap_results["ci_upper"],
            delta_ast=bootstrap_results["delta_ast"],
            gate_result=bootstrap_results["gate_result"],
        )
        self.plot_per_problem_scatter(baseline_rates, syncode_rates, task_ids)
        self.plot_fmd_comparison(
            fmd_results["baseline_distribution"],
            fmd_results["syncode_distribution"],
        )
        self.plot_transition_heatmap(baseline_pool, syncode_pool, task_ids)
