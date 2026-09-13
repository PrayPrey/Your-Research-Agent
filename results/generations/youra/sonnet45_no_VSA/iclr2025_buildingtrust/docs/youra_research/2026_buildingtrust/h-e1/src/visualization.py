"""Visualization for meta-analysis results."""
import logging
from pathlib import Path
from typing import List
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from scipy import stats


logger = logging.getLogger(__name__)


class MetaAnalysisVisualizer:
    """Generate visualizations for CV-stability meta-analysis."""

    def __init__(self, output_dir: str = "figures/", dpi: int = 300):
        """Initialize visualizer.

        Args:
            output_dir: Directory to save figures
            dpi: Figure resolution
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi

    def plot_cv_vs_rho_scatter(
        self,
        cv_values: List[float],
        mean_rho_values: List[float],
        benchmark_names: List[str],
        r: float,
        p: float,
        ci_lower: float,
        ci_upper: float
    ) -> None:
        """Create scatter plot of CV vs mean rho with regression line.

        Args:
            cv_values: List of CV per benchmark
            mean_rho_values: List of mean rho per benchmark
            benchmark_names: List of benchmark names
            r: Pearson correlation coefficient
            p: p-value
            ci_lower: Lower 95% CI bound
            ci_upper: Upper 95% CI bound
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Scatter plot
        ax.scatter(
            cv_values, mean_rho_values,
            s=120, alpha=0.7, color="#3498db",
            edgecolor="black", linewidth=0.5, marker="o"
        )

        # Add labels
        for i, name in enumerate(benchmark_names):
            ax.annotate(
                name, (cv_values[i], mean_rho_values[i]),
                xytext=(5, 5), textcoords="offset points",
                fontsize=9, alpha=0.7
            )

        # Regression line
        z = np.polyfit(cv_values, mean_rho_values, 1)
        p_fit = np.poly1d(z)
        x_line = np.linspace(min(cv_values), max(cv_values), 100)
        y_line = p_fit(x_line)
        ax.plot(x_line, y_line, color="#e74c3c", linewidth=2.0, label="Linear fit")

        # Annotation
        text = f"r = {r:.3f}\np = {p:.4f}\n95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]"
        ax.text(
            0.05, 0.95, text,
            transform=ax.transAxes,
            fontsize=11, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
        )

        ax.set_xlabel("Coefficient of Variation (CV)", fontsize=12)
        ax.set_ylabel("Mean Cross-Benchmark Spearman ρ", fontsize=12)
        ax.set_title("H-E1: CV vs Cross-Benchmark Stability", fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

        output_path = self.output_dir / "cv_vs_rho_scatter.png"
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved: {output_path}")

    def plot_per_benchmark_bars(
        self,
        cv_values: List[float],
        mean_rho_values: List[float],
        benchmark_names: List[str]
    ) -> None:
        """Create dual bar chart for CV and mean rho per benchmark.

        Args:
            cv_values: List of CV per benchmark
            mean_rho_values: List of mean rho per benchmark
            benchmark_names: List of benchmark names
        """
        # Sort by CV
        sorted_idx = np.argsort(cv_values)
        cv_sorted = [cv_values[i] for i in sorted_idx]
        rho_sorted = [mean_rho_values[i] for i in sorted_idx]
        names_sorted = [benchmark_names[i] for i in sorted_idx]

        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(len(names_sorted))
        width = 0.35

        # Normalize for visualization (different scales)
        cv_norm = np.array(cv_sorted) / max(cv_sorted)
        rho_norm = np.array(rho_sorted) / max(rho_sorted)

        bars1 = ax.bar(
            x - width/2, cv_norm, width,
            label="CV (normalized)", color="#3498db",
            edgecolor="black", linewidth=0.8
        )
        bars2 = ax.bar(
            x + width/2, rho_norm, width,
            label="Mean ρ (normalized)", color="#e67e22",
            edgecolor="black", linewidth=0.8
        )

        # Add value labels
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{cv_sorted[i]:.2f}',
                ha='center', va='bottom', fontsize=8
            )
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{rho_sorted[i]:.2f}',
                ha='center', va='bottom', fontsize=8
            )

        ax.set_xlabel("Benchmark (sorted by CV)", fontsize=12)
        ax.set_ylabel("Normalized Value", fontsize=12)
        ax.set_title("Per-Benchmark CV and Mean ρ (Normalized)", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(names_sorted, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        output_path = self.output_dir / "cv_rho_per_benchmark_bars.png"
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved: {output_path}")

    def plot_pairwise_heatmap(self, correlation_matrix: pd.DataFrame) -> None:
        """Create heatmap of pairwise Spearman rho.

        Args:
            correlation_matrix: DataFrame with pairwise rho values
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        sns.heatmap(
            correlation_matrix,
            annot=True, fmt=".2f",
            cmap="RdYlGn", center=0.0,
            vmin=-1.0, vmax=1.0,
            linewidths=0.5, linecolor="gray",
            cbar_kws={"label": "Spearman ρ"},
            ax=ax
        )

        ax.set_title("Pairwise Cross-Benchmark Correlation Matrix", fontsize=14, fontweight="bold")

        output_path = self.output_dir / "pairwise_rho_heatmap.png"
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved: {output_path}")

    def plot_gate_comparison(
        self,
        target_r: float,
        actual_r: float,
        target_p: float,
        actual_p: float
    ) -> None:
        """Create gate metrics comparison chart.

        Args:
            target_r: Target Pearson r threshold
            actual_r: Actual Pearson r value
            target_p: Target p-value threshold
            actual_p: Actual p-value
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

        # Pearson r comparison
        width = 0.4
        x1 = np.array([0, 1])
        r_values = [target_r, actual_r]
        r_colors = ["#95a5a6", "#2ecc71" if actual_r < target_r else "#e74c3c"]

        bars1 = ax1.bar(x1, r_values, width, color=r_colors, edgecolor="black", linewidth=1.0)
        ax1.axhline(target_r, color="red", linestyle="--", linewidth=2.0, label="Threshold")
        ax1.set_ylabel("Pearson r", fontsize=12)
        ax1.set_title("Pearson Correlation", fontsize=13, fontweight="bold")
        ax1.set_xticks(x1)
        ax1.set_xticklabels(["Target", "Actual"])
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, val in zip(bars1, r_values):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}',
                ha='center', va='bottom' if val < 0 else 'top', fontsize=11
            )

        # p-value comparison
        x2 = np.array([0, 1])
        p_values = [target_p, actual_p]
        p_colors = ["#95a5a6", "#2ecc71" if actual_p < target_p else "#e74c3c"]

        bars2 = ax2.bar(x2, p_values, width, color=p_colors, edgecolor="black", linewidth=1.0)
        ax2.axhline(target_p, color="red", linestyle="--", linewidth=2.0, label="Threshold")
        ax2.set_ylabel("p-value", fontsize=12)
        ax2.set_title("Statistical Significance", fontsize=13, fontweight="bold")
        ax2.set_xticks(x2)
        ax2.set_xticklabels(["Target", "Actual"])
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, val in zip(bars2, p_values):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width()/2., height,
                f'{val:.4f}',
                ha='center', va='bottom', fontsize=11
            )

        fig.suptitle("MUST_WORK Gate Metrics", fontsize=15, fontweight="bold")
        plt.tight_layout()

        output_path = self.output_dir / "gate_metrics_comparison.png"
        fig.savefig(output_path, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved: {output_path}")
