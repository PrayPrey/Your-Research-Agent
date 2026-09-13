"""Visualization module for analysis results."""

from typing import Dict, List, Any
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from torch import Tensor

sns.set_style("whitegrid")


class AnalysisVisualizer:
    """Generate visualizations for low-rank analysis results."""

    def __init__(self, output_dir: str):
        """Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_rank_vs_depth(self, results: Dict[int, Dict[str, Any]]) -> None:
        """Plot effective rank vs layer depth.

        Args:
            results: Analysis results dict {layer_idx: {effective_rank, ...}}
        """
        layers = sorted(results.keys())
        ranks = [results[layer]["effective_rank"] for layer in layers]

        plt.figure(figsize=(10, 6))
        plt.plot(layers, ranks, marker="o", linewidth=2, markersize=8)
        plt.axhline(y=256, color="r", linestyle="--", label="Threshold (r=256)")
        plt.xlabel("Layer Index", fontsize=12)
        plt.ylabel("Effective Rank", fontsize=12)
        plt.title("Effective Rank vs Layer Depth (LLaMA-7B)", fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "rank_vs_depth.png"), dpi=300)
        plt.close()

    def plot_entropy_regression(
        self, results: Dict[int, Dict[str, Any]], regression_stats: Dict[str, float]
    ) -> None:
        """Plot entropy vs layer depth with regression line.

        Args:
            results: Analysis results dict
            regression_stats: Regression statistics {slope, intercept, p_value, r_squared}
        """
        layers = sorted(results.keys())
        entropies = [results[layer]["operator_entropy"] for layer in layers]

        # Fitted line
        slope = regression_stats["slope"]
        intercept = regression_stats["intercept"]
        fitted = [slope * layer + intercept for layer in layers]

        plt.figure(figsize=(10, 6))
        plt.scatter(layers, entropies, s=100, alpha=0.6, label="Measured")
        plt.plot(layers, fitted, "r--", linewidth=2, label="Linear Fit")
        plt.xlabel("Layer Index", fontsize=12)
        plt.ylabel("Operator Entropy", fontsize=12)
        plt.title(
            f"Operator Entropy vs Layer Depth\n"
            f"β={slope:.4f}, p={regression_stats['p_value']:.4e}, R²={regression_stats['r_squared']:.3f}",
            fontsize=14,
        )
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.output_dir, "entropy_regression.png"), dpi=300
        )
        plt.close()

    def plot_singular_values(
        self, layer_idx: int, singular_values: Tensor
    ) -> None:
        """Plot singular value distribution as heatmap.

        Args:
            layer_idx: Layer index for title
            singular_values: Singular values tensor [B*H, L]
        """
        # Convert to numpy
        S = singular_values.numpy()

        # Take first 100 samples for visualization
        S_subset = S[:100, :100] if S.shape[0] > 100 else S

        plt.figure(figsize=(10, 8))
        sns.heatmap(S_subset, cmap="viridis", cbar_kws={"label": "Singular Value"})
        plt.xlabel("Singular Value Index", fontsize=12)
        plt.ylabel("Sample Index", fontsize=12)
        plt.title(f"Singular Value Distribution (Layer {layer_idx})", fontsize=14)
        plt.tight_layout()
        plt.savefig(
            os.path.join(self.output_dir, f"singular_values_layer_{layer_idx}.png"),
            dpi=300,
        )
        plt.close()

    def plot_rank_sensitivity(
        self, thresholds: List[float], ranks: Dict[float, List[float]]
    ) -> None:
        """Plot rank vs variance threshold sensitivity.

        Args:
            thresholds: List of variance thresholds
            ranks: Dict mapping threshold to list of ranks per layer
        """
        plt.figure(figsize=(10, 6))

        for threshold in thresholds:
            if threshold in ranks:
                plt.plot(
                    range(len(ranks[threshold])),
                    ranks[threshold],
                    marker="o",
                    label=f"Threshold={threshold}",
                )

        plt.xlabel("Layer Index (relative)", fontsize=12)
        plt.ylabel("Effective Rank", fontsize=12)
        plt.title("Rank Sensitivity to Variance Threshold", fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "rank_sensitivity.png"), dpi=300)
        plt.close()

    def plot_gate_metrics(
        self, target_metrics: Dict[str, Any], actual_metrics: Dict[str, Any]
    ) -> None:
        """Plot gate validation metrics comparison.

        Args:
            target_metrics: Target/threshold values
            actual_metrics: Measured values
        """
        metrics = ["max_rank", "entropy_slope"]
        targets = [
            target_metrics.get("max_rank", 256),
            target_metrics.get("entropy_slope", 0),
        ]
        actuals = [
            actual_metrics.get("max_rank", 0),
            actual_metrics.get("entropy_slope", 0),
        ]

        x = np.arange(len(metrics))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(x - width / 2, targets, width, label="Target/Threshold", alpha=0.8)
        ax.bar(x + width / 2, actuals, width, label="Actual", alpha=0.8)

        ax.set_xlabel("Metrics", fontsize=12)
        ax.set_ylabel("Value", fontsize=12)
        ax.set_title("Gate Validation Metrics Comparison", fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(["Max Rank (r_eff < 256)", "Entropy Slope (β < 0)"])
        ax.legend()
        ax.grid(True, alpha=0.3, axis="y")

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "gate_metrics.png"), dpi=300)
        plt.close()
