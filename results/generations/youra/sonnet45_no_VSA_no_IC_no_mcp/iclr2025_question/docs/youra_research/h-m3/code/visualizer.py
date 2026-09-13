"""Visualization module for viability classification results."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path


class ViabilityVisualizer:
    """Generate 4 required figures for H-M3."""

    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_accuracy_comparison(self, metrics: dict):
        """
        Bar chart: Random baseline (50%), Gate 1 actual, target (80%).

        Args:
            metrics: Dict with keys 'baseline' and 'gate1', each with 'accuracy'
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        categories = ["Random\nBaseline", "Gate 1\nActual"]
        accuracies = [metrics["baseline"]["accuracy"], metrics["gate1"]["accuracy"]]

        bars = ax.bar(categories, accuracies, color=["gray", "steelblue"], alpha=0.7)
        ax.axhline(y=0.80, color="red", linestyle="--", linewidth=2, label="Target (80%)")

        ax.set_ylabel("Accuracy", fontsize=12)
        ax.set_ylim([0, 1.0])
        ax.set_title("Viability Prediction Accuracy Comparison", fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)

        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                    f"{acc:.1%}", ha="center", va="bottom", fontsize=11, fontweight="bold")

        plt.tight_layout()
        plt.savefig(self.output_dir / "accuracy_comparison.png", dpi=300)
        plt.close()

    def plot_confusion_matrix(self, cm: dict):
        """
        2x2 heatmap: TP/TN/FP/FN.

        Args:
            cm: Dict with keys TP, TN, FP, FN
        """
        fig, ax = plt.subplots(figsize=(6, 6))

        matrix = np.array([[cm["TN"], cm["FP"]], [cm["FN"], cm["TP"]]])
        labels = ["viable", "non-viable"]

        sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels,
                    cbar_kws={"label": "Count"}, ax=ax)

        ax.set_xlabel("Predicted", fontsize=12)
        ax.set_ylabel("Actual", fontsize=12)
        ax.set_title("Confusion Matrix (Gate 1)", fontsize=14, fontweight="bold")

        plt.tight_layout()
        plt.savefig(self.output_dir / "confusion_matrix.png", dpi=300)
        plt.close()

    def plot_prediction_distribution(self, df: pd.DataFrame, predictions: list, y_true: list):
        """
        Histogram: Predicted vs actual viability by overhead level.

        Args:
            df: DataFrame with O_full column
            predictions: Gate 1 predictions (list of "viable"/"non-viable")
            y_true: Ground truth labels
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Bin by overhead level
        df_copy = df.copy()
        df_copy["predicted"] = predictions
        df_copy["actual"] = y_true
        df_copy["overhead_level"] = pd.cut(df_copy["O_full"], bins=[0, 0.20, 0.80, 1.0],
                                           labels=["low", "mid", "high"])

        # Count by level and label
        counts = df_copy.groupby(["overhead_level", "predicted", "actual"]).size().unstack(fill_value=0)

        if counts.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
        else:
            counts.plot(kind="bar", ax=ax, color=["lightgreen", "salmon"], alpha=0.7)

        ax.set_xlabel("Overhead Level", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.set_title("Prediction Distribution by Overhead Level", fontsize=14, fontweight="bold")
        ax.legend(title="Actual", fontsize=10)
        ax.tick_params(axis='x', rotation=0)

        plt.tight_layout()
        plt.savefig(self.output_dir / "prediction_distribution.png", dpi=300)
        plt.close()

    def plot_error_analysis(self, df: pd.DataFrame, y_true: list, y_pred: list):
        """
        Scatter plot: O_10 vs O_full, color-coded by correct/incorrect.

        Args:
            df: DataFrame with O_10, O_full columns
            y_true: Ground truth labels
            y_pred: Gate 1 predictions
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        df_copy = df.copy()
        df_copy["correct"] = [t == p for t, p in zip(y_true, y_pred)]

        correct = df_copy[df_copy["correct"]]
        incorrect = df_copy[~df_copy["correct"]]

        ax.scatter(correct["O_10"], correct["O_full"], c="green", alpha=0.6, s=80, label="Correct")
        ax.scatter(incorrect["O_10"], incorrect["O_full"], c="red", alpha=0.6, s=80, marker="x", label="Incorrect")

        # Threshold line
        threshold = df["threshold"].iloc[0] if "threshold" in df.columns else 0.10
        ax.axhline(y=threshold, color="orange", linestyle="--", linewidth=2, label=f"Threshold ({threshold:.1%})")
        ax.axvline(x=threshold, color="orange", linestyle="--", linewidth=2)

        ax.set_xlabel("O_10 (10-sample overhead)", fontsize=12)
        ax.set_ylabel("O_full (full-scale overhead)", fontsize=12)
        ax.set_title("Error Analysis: O_10 vs O_full", fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.output_dir / "error_analysis.png", dpi=300)
        plt.close()

    def save_all_figures(self, df: pd.DataFrame, metrics: dict, predictions_gate1: list, y_true: list):
        """Generate all 4 required figures."""
        self.plot_accuracy_comparison(metrics)
        self.plot_confusion_matrix(metrics["gate1"]["confusion_matrix"])
        self.plot_prediction_distribution(df, predictions_gate1, y_true)
        self.plot_error_analysis(df, y_true, predictions_gate1)
