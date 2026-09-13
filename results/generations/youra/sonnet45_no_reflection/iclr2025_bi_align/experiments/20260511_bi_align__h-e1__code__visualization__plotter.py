"""Visualization for gate metrics and results."""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict
import os


class ResultsVisualizer:
    """Generate figures for validation report."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        sns.set_style("whitegrid")

    def plot_gate_metrics(self, metrics: Dict, save_path: str = None) -> None:
        """Plot gate metrics comparison (MANDATORY)."""
        if save_path is None:
            save_path = os.path.join(self.output_dir, "gate_metrics.png")

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        # ICC
        ax = axes[0]
        ax.bar(["Actual"], [metrics["icc"]["value"]], color="steelblue")
        ax.axhline(metrics["icc"]["threshold"], color="red", linestyle="--", label="Threshold")
        ax.set_ylabel("ICC Value")
        ax.set_title("ICC (Intraclass Correlation)")
        ax.set_ylim([0, 1])
        ax.legend()

        # ANOVA p-value
        ax = axes[1]
        ax.bar(["Actual"], [metrics["anova_p"]["value"]], color="forestgreen")
        ax.axhline(metrics["anova_p"]["threshold"], color="red", linestyle="--", label="Threshold")
        ax.set_ylabel("p-value")
        ax.set_title("ANOVA p-value")
        ax.set_ylim([0, max(0.1, metrics["anova_p"]["value"] * 1.2)])
        ax.legend()

        # Cohen's f
        ax = axes[2]
        ax.bar(["Actual"], [metrics["cohens_f"]["value"]], color="coral")
        ax.axhline(metrics["cohens_f"]["threshold"], color="red", linestyle="--", label="Threshold")
        ax.set_ylabel("Effect Size")
        ax.set_title("Cohen's f (Effect Size)")
        ax.set_ylim([0, max(0.2, metrics["cohens_f"]["value"] * 1.2)])
        ax.legend()

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {save_path}")

    def plot_capability_consistency(self, results_df: pd.DataFrame, save_path: str = None) -> None:
        """Plot accuracy vs lambda with error bars."""
        if save_path is None:
            save_path = os.path.join(self.output_dir, "capability_consistency.png")

        fig, ax = plt.subplots(figsize=(8, 6))

        # Group by lambda and compute mean/std
        grouped = results_df.groupby("lambda")["correct"].agg(["mean", "std"])

        # Plot with error bars
        ax.errorbar(
            grouped.index,
            grouped["mean"],
            yerr=grouped["std"],
            marker="o",
            markersize=8,
            linewidth=2,
            capsize=5,
            label="Accuracy"
        )

        ax.set_xlabel("Compliance Level (λ)", fontsize=12)
        ax.set_ylabel("Accuracy", fontsize=12)
        ax.set_title("Capability Consistency Across Compliance Levels", fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim([0, 1])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {save_path}")

    def plot_subject_heatmap(self, results_df: pd.DataFrame, save_path: str = None) -> None:
        """Plot MMLU subject × lambda heatmap."""
        if save_path is None:
            save_path = os.path.join(self.output_dir, "subject_heatmap.png")

        # Filter MMLU data (has 'subject' column)
        mmlu_data = results_df[results_df["subject"].notna()].copy()

        # Pivot to subject × lambda
        pivot = mmlu_data.pivot_table(
            values="correct",
            index="subject",
            columns="lambda",
            aggfunc="mean"
        )

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 12))
        sns.heatmap(
            pivot,
            cmap="YlGnBu",
            annot=False,
            cbar_kws={"label": "Accuracy"},
            ax=ax,
            vmin=0,
            vmax=1
        )

        ax.set_xlabel("Compliance Level (λ)", fontsize=12)
        ax.set_ylabel("MMLU Subject", fontsize=12)
        ax.set_title("MMLU Subject Accuracy Heatmap", fontsize=14)

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {save_path}")

    def plot_distributions(self, results_df: pd.DataFrame, save_path: str = None) -> None:
        """Plot violin plots per lambda."""
        if save_path is None:
            save_path = os.path.join(self.output_dir, "accuracy_distributions.png")

        fig, ax = plt.subplots(figsize=(10, 6))

        # Create violin plot
        sns.violinplot(
            data=results_df,
            x="lambda",
            y="correct",
            ax=ax,
            palette="Set2"
        )

        ax.set_xlabel("Compliance Level (λ)", fontsize=12)
        ax.set_ylabel("Accuracy (Per Item)", fontsize=12)
        ax.set_title("Accuracy Distribution Across Compliance Levels", fontsize=14)
        ax.set_ylim([-0.1, 1.1])

        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {save_path}")
