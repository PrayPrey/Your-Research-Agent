from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

if TYPE_CHECKING:
    from config import Config

DOMAIN_COLORS = {"academic": "#1f77b4", "commonsense": "#ff7f0e"}


class Visualizer:
    """Generates H-M2 analysis figures."""

    def __init__(self, config: "Config"):
        self.config = config
        Path(config.figures_dir).mkdir(parents=True, exist_ok=True)

    def _save(self, name: str) -> None:
        """Save current figure to figures_dir/name and close."""
        path = os.path.join(self.config.figures_dir, name)
        plt.savefig(path, dpi=self.config.figure_dpi, bbox_inches="tight")
        plt.close()

    def plot_domain_corpus_heatmap(self, stratified: dict) -> None:
        """2x3 seaborn heatmap: rows=domain, cols=corpus. Saves domain_corpus_heatmap.png."""
        domains = ["academic", "commonsense"]
        corpora = ["pile", "c4", "redpajama"]
        data = {
            c: [stratified[c][d] * 100 for d in domains]
            for c in corpora
        }
        df = pd.DataFrame(data, index=domains)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.heatmap(
            df, ax=ax, annot=True, fmt=".2f", cmap="YlOrRd",
            cbar_kws={"label": "Mean Contamination Rate (%)"},
        )
        ax.set_title("Domain × Corpus Contamination Heatmap")
        ax.set_ylabel("Domain")
        ax.set_xlabel("Corpus")
        plt.tight_layout()
        self._save("domain_corpus_heatmap.png")

    def plot_domain_boxplots(self, stratified: dict, directional_tests: dict = None) -> None:
        """3-panel boxplots per corpus: academic vs commonsense. Saves domain_boxplots.png."""
        corpora = ["pile", "c4", "redpajama"]
        fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
        test_keys = {
            "pile": "pile_academic_gt_commonsense",
            "c4": "c4_commonsense_gt_academic",
            "redpajama": "redpajama_academic_gt_commonsense",
        }
        for i, corpus in enumerate(corpora):
            ax = axes[i]
            acad = [r * 100 for r in stratified[corpus]["academic_rates"]]
            comm = [r * 100 for r in stratified[corpus]["commonsense_rates"]]
            bp = ax.boxplot(
                [acad, comm],
                labels=["academic", "commonsense"],
                patch_artist=True,
            )
            bp["boxes"][0].set_facecolor(DOMAIN_COLORS["academic"])
            bp["boxes"][1].set_facecolor(DOMAIN_COLORS["commonsense"])
            ax.set_title(corpus)
            ax.set_ylabel("Contamination Rate (%)" if i == 0 else "")
            # Annotate p-value if available
            if directional_tests and test_keys[corpus] in directional_tests:
                p = directional_tests[test_keys[corpus]]["p"]
                confirmed = directional_tests[test_keys[corpus]]["direction_confirmed"]
                color = "green" if confirmed else "red"
                ax.text(
                    0.5, 0.97, f"p={p:.4f}",
                    transform=ax.transAxes, ha="center", va="top",
                    fontsize=9, color=color,
                )
        plt.suptitle("Domain-Stratified Contamination Rates by Corpus", fontsize=12)
        plt.tight_layout()
        self._save("domain_boxplots.png")

    def plot_top5_per_corpus(self, top5: dict, domain_map: dict[str, str]) -> None:
        """3 horizontal bar charts per corpus: top-5 subtasks, color-coded by domain. Saves top5_per_corpus.png."""
        corpora = ["pile", "c4", "redpajama"]
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        for i, corpus in enumerate(corpora):
            ax = axes[i]
            items = top5[corpus]
            names = [x["subtask"] for x in items]
            rates = [x["rate"] * 100 for x in items]
            colors = [DOMAIN_COLORS.get(x["domain"], "#999999") for x in items]
            bars = ax.barh(names, rates, color=colors)
            ax.set_title(f"{corpus} — Top {len(items)}")
            ax.set_xlabel("Contamination Rate (%)")
            ax.invert_yaxis()
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=DOMAIN_COLORS["academic"], label="academic"),
            Patch(facecolor=DOMAIN_COLORS["commonsense"], label="commonsense"),
        ]
        fig.legend(handles=legend_elements, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.05))
        plt.suptitle("Top-5 Contaminated Subtasks per Corpus", fontsize=12)
        plt.tight_layout()
        self._save("top5_per_corpus.png")

    def plot_directional_test_summary(self, directional_tests: dict) -> None:
        """P-value bar chart with effect size labels. Saves directional_test_summary.png."""
        test_names = list(directional_tests.keys())
        p_values = [directional_tests[t]["p"] for t in test_names]
        effect_sizes = [directional_tests[t]["effect_size_r"] for t in test_names]
        colors = [
            "green" if directional_tests[t]["direction_confirmed"] else "salmon"
            for t in test_names
        ]
        short_names = [n.replace("_gt_", ">").replace("_academic", "\nacad").replace("_commonsense", "\ncomm") for n in test_names]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(short_names, p_values, color=colors)
        ax.axhline(y=self.config.alpha, color="red", linestyle="--", label=f"α={self.config.alpha}")
        for j, t in enumerate(test_names):
            r = effect_sizes[j]
            ax.text(j, p_values[j] + 0.002, f"r={r:.2f}", ha="center", fontsize=9)
        ax.set_ylabel("p-value (one-tailed)")
        ax.set_title("Directional Test Summary: Domain Contamination Patterns")
        ax.legend()
        plt.tight_layout()
        self._save("directional_test_summary.png")
