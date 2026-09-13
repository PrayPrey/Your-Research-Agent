"""Visualization generation for H-M1 analysis."""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict


CONFIG = {
    "figsize": (8, 6),
    "dpi": 300,
    "format": "png",
    "type_colors": {
        "attention": "#1f77b4",
        "gradient": "#ff7f0e",
        "regularization": "#2ca02c",
        "normalization": "#d62728",
    },
    "scatter": {
        "marker_size": 100,
        "alpha": 0.7,
        "edgecolor": "black",
        "linewidth": 0.5,
        "regression_line_color": "gray",
        "regression_line_style": "--",
        "regression_line_width": 2,
    },
    "bar": {
        "width": 0.6,
        "alpha": 0.8,
        "edgecolor": "black",
        "linewidth": 1,
    },
    "residual": {
        "marker": "o",
        "marker_size": 80,
        "color": "#9467bd",
        "alpha": 0.6,
        "edgecolor": "black",
        "linewidth": 0.5,
        "zero_line_color": "red",
        "zero_line_style": "--",
        "zero_line_width": 1.5,
    },
}


class Visualizer:
    """Generate publication-quality visualizations."""

    def __init__(self, output_dir: str):
        """Initialize with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_correlation_scatter(
        self,
        o10: List[float],
        ofull: List[float],
        types: List[str],
        r: float,
        p: float,
        k: float
    ):
        """Plot O_10 vs O_full scatter with regression line."""
        fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

        # Scatter points colored by type
        colors = [CONFIG["type_colors"][t] for t in types]
        ax.scatter(
            o10, ofull,
            c=colors,
            s=CONFIG["scatter"]["marker_size"],
            alpha=CONFIG["scatter"]["alpha"],
            edgecolor=CONFIG["scatter"]["edgecolor"],
            linewidth=CONFIG["scatter"]["linewidth"]
        )

        # Regression line
        x_range = [min(o10), max(o10)]
        y_range = [k * x for x in x_range]
        ax.plot(
            x_range, y_range,
            color=CONFIG["scatter"]["regression_line_color"],
            linestyle=CONFIG["scatter"]["regression_line_style"],
            linewidth=CONFIG["scatter"]["regression_line_width"],
            label=f"y = {k:.2f}x"
        )

        # Annotations
        ax.text(
            0.05, 0.95,
            f"r = {r:.3f}\np = {p:.4f}",
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8),
            fontsize=12
        )

        ax.set_xlabel("10-sample Overhead (%)", fontsize=12)
        ax.set_ylabel("Full-scale Overhead (%)", fontsize=12)
        ax.set_title("Micro-Pilot vs Full-Scale Overhead Correlation", fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)

        output_path = self.output_dir / "correlation_scatter.png"
        plt.savefig(output_path, format=CONFIG["format"], dpi=CONFIG["dpi"], bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_path}")

    def plot_scaling_factors(self, k_by_type: Dict[str, float]):
        """Plot per-type scaling factors as bar chart."""
        fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

        types = list(k_by_type.keys())
        k_values = list(k_by_type.values())
        colors = [CONFIG["type_colors"][t] for t in types]

        ax.bar(
            types, k_values,
            width=CONFIG["bar"]["width"],
            alpha=CONFIG["bar"]["alpha"],
            color=colors,
            edgecolor=CONFIG["bar"]["edgecolor"],
            linewidth=CONFIG["bar"]["linewidth"]
        )

        ax.set_xlabel("Hypothesis Type", fontsize=12)
        ax.set_ylabel("Scaling Factor (k)", fontsize=12)
        ax.set_title("Per-Type Scaling Factors", fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

        output_path = self.output_dir / "scaling_factors.png"
        plt.savefig(output_path, format=CONFIG["format"], dpi=CONFIG["dpi"], bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_path}")

    def plot_residuals(self, o10: List[float], residuals: List[float]):
        """Plot residuals vs O_10 to check linearity."""
        fig, ax = plt.subplots(figsize=CONFIG["figsize"], dpi=CONFIG["dpi"])

        ax.scatter(
            o10, residuals,
            marker=CONFIG["residual"]["marker"],
            s=CONFIG["residual"]["marker_size"],
            color=CONFIG["residual"]["color"],
            alpha=CONFIG["residual"]["alpha"],
            edgecolor=CONFIG["residual"]["edgecolor"],
            linewidth=CONFIG["residual"]["linewidth"]
        )

        # Zero line
        ax.axhline(
            0,
            color=CONFIG["residual"]["zero_line_color"],
            linestyle=CONFIG["residual"]["zero_line_style"],
            linewidth=CONFIG["residual"]["zero_line_width"]
        )

        ax.set_xlabel("10-sample Overhead (%)", fontsize=12)
        ax.set_ylabel("Residuals (%)", fontsize=12)
        ax.set_title("Residual Plot (Linearity Check)", fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)

        output_path = self.output_dir / "residuals.png"
        plt.savefig(output_path, format=CONFIG["format"], dpi=CONFIG["dpi"], bbox_inches="tight")
        plt.close()
        print(f"Saved: {output_path}")
