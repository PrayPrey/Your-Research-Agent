from __future__ import annotations
import os
from typing import TYPE_CHECKING

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

if TYPE_CHECKING:
    from config import Config


class Visualizer:
    def __init__(self, config: "Config"):
        self.config = config
        self._figures_dir = config.figures_dir
        os.makedirs(self._figures_dir, exist_ok=True)

    def _save(self, filename: str) -> str:
        path = os.path.join(self._figures_dir, filename)
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

    def plot_contamination_rates_bar(
        self, rates_df: pd.DataFrame, p_value: float
    ) -> None:
        """59-bar sorted barplot with p-value annotation. Saves contamination_rates_barplot.png."""
        sorted_df = rates_df.sort_values("rate", ascending=False).reset_index(drop=True)
        fig, ax = plt.subplots(figsize=(18, 6))
        ax.bar(range(len(sorted_df)), sorted_df["rate"], color="steelblue")
        ax.axhline(0.05, color="red", linestyle="--", linewidth=1, label="5% threshold")
        ax.set_xticks(range(len(sorted_df)))
        ax.set_xticklabels(sorted_df["subtask"], rotation=90, fontsize=6)
        ax.set_ylabel("Contamination Rate")
        ax.set_title(f"Per-Sub-Task Contamination Rates (Kruskal-Wallis p={p_value:.4f})")
        ax.legend()
        self._save("contamination_rates_barplot.png")

    def plot_heatmap(self, rates_df: pd.DataFrame) -> None:
        """Sub-task x rate heatmap sorted by domain. Saves heatmap.png."""
        sorted_df = rates_df.sort_values("subtask").set_index("subtask")[["rate"]]
        fig, ax = plt.subplots(figsize=(3, max(6, len(sorted_df) * 0.2)))
        sns.heatmap(sorted_df, ax=ax, cmap="YlOrRd", vmin=0, vmax=1, annot=False)
        ax.set_title("Contamination Rate Heatmap by Sub-task")
        self._save("heatmap.png")

    def plot_distribution(self, rates_df: pd.DataFrame) -> None:
        """Histogram/KDE of contamination rates. Saves distribution.png."""
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(rates_df["rate"], kde=True, ax=ax, color="steelblue", bins=20)
        ax.set_xlabel("Contamination Rate")
        ax.set_ylabel("Count")
        ax.set_title("Distribution of Contamination Rates Across Sub-tasks")
        self._save("distribution.png")

    def plot_domain_boxplot(self, rates_df: pd.DataFrame) -> None:
        """Box plot: MMLU academic vs commonsense benchmarks. Saves domain_boxplot.png."""
        commonsense = {"hellaswag", "bbh"}
        rates_df = rates_df.copy()
        rates_df["domain"] = rates_df["subtask"].apply(
            lambda s: "Commonsense" if s in commonsense else "MMLU Academic"
        )
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.boxplot(data=rates_df, x="domain", y="rate", ax=ax, palette="Set2")
        ax.set_title("Contamination Rates by Domain Type")
        ax.set_ylabel("Contamination Rate")
        self._save("domain_boxplot.png")

    def plot_top_bottom(self, rates_df: pd.DataFrame) -> None:
        """Top-10/bottom-10 horizontal bar chart. Saves top_bottom.png."""
        sorted_df = rates_df.sort_values("rate", ascending=False)
        top10 = sorted_df.head(10)
        bottom10 = sorted_df.tail(10)
        combined = pd.concat([top10, bottom10])
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ["tomato"] * 10 + ["steelblue"] * 10
        ax.barh(combined["subtask"], combined["rate"], color=colors)
        ax.set_xlabel("Contamination Rate")
        ax.set_title("Top-10 and Bottom-10 Sub-tasks by Contamination Rate")
        ax.invert_yaxis()
        self._save("top_bottom.png")

    def plot_sensitivity_scatter(
        self,
        rates_primary: pd.Series,
        rates_sensitivity: pd.Series,
        rho: float,
    ) -> None:
        """Scatter: question-only vs question+choices rates per sub-task. Saves sensitivity_scatter.png."""
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(rates_primary, rates_sensitivity, alpha=0.6, color="steelblue")
        ax.plot([0, 1], [0, 1], "r--", linewidth=1)
        ax.set_xlabel("Question+Choices Rate")
        ax.set_ylabel("Question-Only Rate")
        ax.set_title(f"Sensitivity Analysis (Spearman ρ={rho:.3f})")
        self._save("sensitivity_scatter.png")

    def save_all(self, rates_df: pd.DataFrame, stats: dict) -> None:
        """Generate all figures in sequence."""
        p_value = stats.get("p_value", 1.0)
        self.plot_contamination_rates_bar(rates_df, p_value)
        self.plot_heatmap(rates_df)
        self.plot_distribution(rates_df)
        self.plot_domain_boxplot(rates_df)
        self.plot_top_bottom(rates_df)
