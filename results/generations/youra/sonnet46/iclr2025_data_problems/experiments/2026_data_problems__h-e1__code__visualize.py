"""
Visualizer: generate publication-quality figures for H-E1 results.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

logger = logging.getLogger(__name__)


class Visualizer:
    """Generate all figures for the H-E1 experiment."""

    CONFIG_ORDER = ["C0", "C1", "C2", "C3", "C4", "C5", "C6"]
    CONFIG_LABELS = {
        "C0": "C0\n(unfiltered)",
        "C1": "C1\n(ft ≥10%)",
        "C2": "C2\n(ft ≥30%)",
        "C3": "C3\n(ft ≥50%)",
        "C4": "C4\n(ft ≥70%)",
        "C5": "C5\n(ft ≥90%)",
        "C6": "C6\n(DoReMi)",
    }

    def __init__(self, figures_dir: str):
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Individual plots
    # ------------------------------------------------------------------

    def bar_chart_gate_metric(
        self,
        entropies: Dict[str, float],
        ci_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
        bar_color: str = "#4C72B0",
        figure_size: Tuple[int, int] = (10, 6),
        dpi: int = 150,
    ) -> str:
        """Bar chart of H(demo|occ) per configuration with optional CI."""
        configs = [c for c in self.CONFIG_ORDER if c in entropies]
        values = [entropies[c] for c in configs]
        labels = [self.CONFIG_LABELS.get(c, c) for c in configs]

        yerr_lo = np.zeros(len(configs))
        yerr_hi = np.zeros(len(configs))
        if ci_bounds:
            for i, c in enumerate(configs):
                if c in ci_bounds:
                    lo, hi = ci_bounds[c]
                    yerr_lo[i] = max(0, values[i] - lo)
                    yerr_hi[i] = max(0, hi - values[i])

        fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)
        x = np.arange(len(configs))
        bars = ax.bar(x, values, color=bar_color, alpha=0.85, width=0.6)
        if ci_bounds:
            ax.errorbar(
                x, values,
                yerr=[yerr_lo, yerr_hi],
                fmt="none", color="black", capsize=5, linewidth=1.5,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylabel("H(Demographic | Occupation)  [bits]", fontsize=12)
        ax.set_title("Conditional Entropy by Filter Configuration", fontsize=14)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()

        out = self.figures_dir / "gate_metric_bar.png"
        fig.savefig(str(out), dpi=dpi)
        plt.close(fig)
        logger.info("Saved %s", out)
        return str(out)

    def monotonic_trend_plot(
        self,
        entropies: Dict[str, float],
        figure_size: Tuple[int, int] = (10, 6),
        dpi: int = 150,
    ) -> str:
        """Line plot of entropy across fasttext percentile configs C1-C5, DoReMi separate."""
        ft_configs = ["C1", "C2", "C3", "C4", "C5"]
        percentiles = [10, 30, 50, 70, 90]
        ft_vals = [entropies.get(c, 0.0) for c in ft_configs]

        fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)
        ax.plot(percentiles, ft_vals, marker="o", linewidth=2, color="#4C72B0", label="fasttext filter")

        # DoReMi as horizontal reference
        if "C6" in entropies:
            ax.axhline(
                entropies["C6"],
                linestyle="--",
                color="#DD8452",
                linewidth=1.5,
                label="C6 (DoReMi)",
            )

        ax.set_xlabel("fasttext Filter Percentile Threshold", fontsize=12)
        ax.set_ylabel("H(Demographic | Occupation)  [bits]", fontsize=12)
        ax.set_title("Monotonic Trend: Entropy vs. Filter Aggressiveness", fontsize=14)
        ax.legend(fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()

        out = self.figures_dir / "monotonic_trend.png"
        fig.savefig(str(out), dpi=dpi)
        plt.close(fig)
        logger.info("Saved %s", out)
        return str(out)

    def demographic_heatmap(
        self,
        joint_counts_c1: Dict,
        joint_counts_c5: Dict,
        figure_size: Tuple[int, int] = (12, 8),
        dpi: int = 150,
    ) -> str:
        """Side-by-side heatmap: co-occurrence density C1 vs C5."""
        def to_matrix(jc: Dict) -> Tuple[np.ndarray, List[str], List[str]]:
            occs = sorted({k[0] for k in jc})
            demos = sorted({k[1] for k in jc})
            mat = np.zeros((len(demos), len(occs)))
            for (o, d), cnt in jc.items():
                if o in occs and d in demos:
                    mat[demos.index(d), occs.index(o)] = cnt
            return mat, occs, demos

        mat1, occs1, demos1 = to_matrix(joint_counts_c1)
        mat2, occs2, demos2 = to_matrix(joint_counts_c5)

        # Use common vocab for comparability
        all_occs = sorted(set(occs1) | set(occs2))
        all_demos = sorted(set(demos1) | set(demos2))

        def reindex(jc, occs, demos):
            mat = np.zeros((len(demos), len(occs)))
            for (o, d), cnt in jc.items():
                if o in occs and d in demos:
                    mat[demos.index(d), occs.index(o)] = cnt
            return mat

        m1 = reindex(joint_counts_c1, all_occs, all_demos)
        m2 = reindex(joint_counts_c5, all_occs, all_demos)

        fig, axes = plt.subplots(1, 2, figsize=figure_size, dpi=dpi)
        kw = dict(xticklabels=all_occs, yticklabels=all_demos, cmap="Blues",
                  linewidths=0.3, annot=False)
        sns.heatmap(m1, ax=axes[0], **kw)
        axes[0].set_title("C1 (ft ≥10%)", fontsize=12)
        axes[0].set_xlabel("Occupation", fontsize=10)
        axes[0].set_ylabel("Demographic", fontsize=10)

        sns.heatmap(m2, ax=axes[1], **kw)
        axes[1].set_title("C5 (ft ≥90%)", fontsize=12)
        axes[1].set_xlabel("Occupation", fontsize=10)
        axes[1].set_ylabel("")

        plt.suptitle("Occupation × Demographic Co-occurrence Density", fontsize=14, y=1.02)
        plt.tight_layout()

        out = self.figures_dir / "demographic_heatmap.png"
        fig.savefig(str(out), dpi=dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info("Saved %s", out)
        return str(out)

    def relative_change_chart(
        self,
        relative_changes: Dict[str, float],
        gate_threshold: float = 5.0,
        figure_size: Tuple[int, int] = (10, 6),
        dpi: int = 150,
    ) -> str:
        """Horizontal bar chart of relative entropy changes with 5% threshold line."""
        labels = list(relative_changes.keys())
        values = list(relative_changes.values())
        colors = ["#DD8452" if abs(v) >= gate_threshold else "#4C72B0" for v in values]

        fig, ax = plt.subplots(figsize=figure_size, dpi=dpi)
        y = np.arange(len(labels))
        ax.barh(y, values, color=colors, alpha=0.85, height=0.6)
        ax.axvline(gate_threshold, color="red", linestyle="--", linewidth=1.5,
                   label=f"Gate threshold ({gate_threshold:.0f}%)")
        ax.axvline(-gate_threshold, color="red", linestyle="--", linewidth=1.5)
        ax.axvline(0, color="gray", linestyle="-", linewidth=0.8)

        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=11)
        ax.set_xlabel("Relative Entropy Change (%)", fontsize=12)
        ax.set_title("Relative Entropy Change Between Adjacent Configurations", fontsize=14)
        ax.legend(fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()

        out = self.figures_dir / "relative_change.png"
        fig.savefig(str(out), dpi=dpi)
        plt.close(fig)
        logger.info("Saved %s", out)
        return str(out)

    # ------------------------------------------------------------------
    # Batch
    # ------------------------------------------------------------------

    def generate_all(
        self,
        entropies: Dict[str, float],
        joint_counts: Dict[str, Dict],
        stats_results: Dict[str, Any],
        ci_bounds: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> List[str]:
        """Generate all 4 figures, return list of output paths."""
        paths: List[str] = []

        paths.append(self.bar_chart_gate_metric(entropies, ci_bounds))
        paths.append(self.monotonic_trend_plot(entropies))

        jc_c1 = joint_counts.get("C1", {})
        jc_c5 = joint_counts.get("C5", {})
        paths.append(self.demographic_heatmap(jc_c1, jc_c5))

        rel_changes = stats_results.get("relative_changes", {})
        if not rel_changes:
            # compute from entropies if missing
            ft_configs = ["C1", "C2", "C3", "C4", "C5"]
            for i in range(len(ft_configs) - 1):
                h_a = entropies.get(ft_configs[i], 0.0)
                h_b = entropies.get(ft_configs[i + 1], 0.0)
                if h_a > 0:
                    rel_changes[f"{ft_configs[i]}→{ft_configs[i+1]}"] = (h_b - h_a) / h_a * 100.0
        paths.append(self.relative_change_chart(rel_changes))

        return paths
