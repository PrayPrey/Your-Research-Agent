"""
Divergence Comparison Visualizer for h-m2
Extends h-m1 visualizer with divergence-specific plots.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Add h-m1 to path
h_m1_path = Path(__file__).parent.parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(h_m1_path))

from visualization.visualizer import ExperimentVisualizer


class DivergenceComparisonVisualizer(ExperimentVisualizer):
    """
    Extends h-m1's ExperimentVisualizer with divergence analysis plots.

    Inherits:
        - Basic plotting setup
        - Output directory management

    Adds:
        - Timeout subgroup comparison (divergent vs difficult)
        - Divergence marker scatter plots
        - Classification pie chart
    """

    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_timeout_subgroup_comparison_bar(
        self,
        divergent_stats: dict,
        difficult_stats: dict,
        save_path: str = None
    ):
        """
        MANDATORY plot for gate metric visualization.
        Bar chart comparing mean variance: divergent vs difficult.

        Args:
            divergent_stats: {"mean_variance": float, "count": int}
            difficult_stats: {"mean_variance": float, "count": int}
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        groups = ["Divergent", "Difficult"]
        means = [
            divergent_stats["mean_variance"],
            difficult_stats["mean_variance"]
        ]
        counts = [
            divergent_stats["count"],
            difficult_stats["count"]
        ]

        colors = ["#e74c3c", "#f39c12"]  # Red (divergent), Orange (difficult)
        bars = ax.bar(groups, means, color=colors, alpha=0.7, edgecolor="black")

        # Add count labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"n={count}",
                ha="center",
                va="bottom",
                fontsize=10
            )

        ax.set_ylabel("Mean Confidence Variance", fontsize=12)
        ax.set_title("Timeout Subgroup Comparison (h-m2 Gate Metric)", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(means) * 1.2)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "timeout_subgroup_comparison_bar.png"

        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"✓ Saved: {save_path}")

    def plot_variance_by_divergence_boxplot(
        self,
        divergent_variances: list,
        difficult_variances: list,
        save_path: str = None
    ):
        """
        Box plot showing variance distributions for divergent vs difficult.

        Args:
            divergent_variances: List of variance values for divergent group
            difficult_variances: List of variance values for difficult group
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        data = [divergent_variances, difficult_variances]
        labels = ["Divergent", "Difficult"]

        bp = ax.boxplot(
            data,
            labels=labels,
            patch_artist=True,
            notch=False,
            showmeans=True
        )

        # Color boxes
        colors = ["#e74c3c", "#f39c12"]
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.5)

        ax.set_ylabel("Confidence Variance", fontsize=12)
        ax.set_title("Variance Distribution by Divergence Classification", fontsize=14)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "variance_by_divergence_boxplot.png"

        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"✓ Saved: {save_path}")

    def plot_divergence_marker_scatter(
        self,
        timeout_results: list,
        save_path_collision: str = None,
        save_path_backtrack: str = None
    ):
        """
        Two scatter plots: collisions vs variance, backtracks vs variance.
        Color-coded by divergence classification.

        Args:
            timeout_results: List of dicts with variance, is_divergent, divergence_markers
        """
        # Extract data
        variances = [r["variance"] for r in timeout_results]
        collisions = [r["divergence_markers"]["collision_count"] for r in timeout_results]
        backtracks = [r["divergence_markers"]["backtrack_count"] for r in timeout_results]
        is_divergent = [r["is_divergent"] for r in timeout_results]

        colors = ["#e74c3c" if div else "#3498db" for div in is_divergent]

        # Plot 1: Collisions vs Variance
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(collisions, variances, c=colors, alpha=0.6, s=50, edgecolors="black")
        ax.set_xlabel("State Hash Collisions", fontsize=12)
        ax.set_ylabel("Confidence Variance", fontsize=12)
        ax.set_title("Collision Count vs. Variance", fontsize=14)
        ax.grid(alpha=0.3)

        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#e74c3c", label="Divergent"),
            Patch(facecolor="#3498db", label="Difficult")
        ]
        ax.legend(handles=legend_elements)

        plt.tight_layout()

        if save_path_collision is None:
            save_path_collision = self.output_dir / "collision_variance_scatter.png"

        plt.savefig(save_path_collision, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {save_path_collision}")

        # Plot 2: Backtracks vs Variance
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(backtracks, variances, c=colors, alpha=0.6, s=50, edgecolors="black")
        ax.set_xlabel("Backtrack Count", fontsize=12)
        ax.set_ylabel("Confidence Variance", fontsize=12)
        ax.set_title("Backtrack Count vs. Variance", fontsize=14)
        ax.grid(alpha=0.3)
        ax.legend(handles=legend_elements)

        plt.tight_layout()

        if save_path_backtrack is None:
            save_path_backtrack = self.output_dir / "backtrack_variance_scatter.png"

        plt.savefig(save_path_backtrack, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"✓ Saved: {save_path_backtrack}")

    def plot_divergence_classification_pie(
        self,
        divergent_count: int,
        difficult_count: int,
        save_path: str = None
    ):
        """
        Pie chart showing proportion of divergent vs difficult timeouts.
        """
        fig, ax = plt.subplots(figsize=(7, 7))

        sizes = [divergent_count, difficult_count]
        labels = [f"Divergent\n(n={divergent_count})", f"Difficult\n(n={difficult_count})"]
        colors = ["#e74c3c", "#f39c12"]

        ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 12}
        )

        ax.set_title("Timeout Classification Distribution", fontsize=14, fontweight="bold")

        plt.tight_layout()

        if save_path is None:
            save_path = self.output_dir / "divergence_classification_pie.png"

        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close()

        print(f"✓ Saved: {save_path}")


def test_visualizer():
    """Test divergence visualizer."""
    print("Testing DivergenceComparisonVisualizer...")

    import tempfile
    output_dir = tempfile.mkdtemp()

    viz = DivergenceComparisonVisualizer(output_dir)

    # Mock data
    divergent_stats = {"mean_variance": 0.35, "count": 15}
    difficult_stats = {"mean_variance": 0.25, "count": 25}

    timeout_results = [
        {"variance": 0.4, "is_divergent": True, "divergence_markers": {"collision_count": 5, "backtrack_count": 3}},
        {"variance": 0.2, "is_divergent": False, "divergence_markers": {"collision_count": 1, "backtrack_count": 2}},
    ]

    # Test all plots
    viz.plot_timeout_subgroup_comparison_bar(divergent_stats, difficult_stats)
    viz.plot_variance_by_divergence_boxplot([0.4, 0.35], [0.2, 0.25])
    viz.plot_divergence_marker_scatter(timeout_results)
    viz.plot_divergence_classification_pie(15, 25)

    print(f"✓ All plots generated in: {output_dir}")


if __name__ == "__main__":
    test_visualizer()
