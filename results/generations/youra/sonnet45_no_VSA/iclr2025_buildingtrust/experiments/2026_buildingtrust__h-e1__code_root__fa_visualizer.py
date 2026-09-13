"""Visualization for H-E1 Factor Analysis results."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List
import os


class FactorVisualizer:
    """Generate validation figures for factor analysis."""

    def __init__(self, output_dir: str = "figures/"):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_scree(self, eigenvalues: np.ndarray, threshold: float = 1.0) -> str:
        """
        Create scree plot showing eigenvalues.

        Args:
            eigenvalues: [M] eigenvalues from PCA
            threshold: Kaiser criterion threshold (default 1.0)

        Returns:
            str: Path to saved figure
        """
        print("\n[Visualizer] Creating scree plot...")

        plt.figure(figsize=(8, 5))
        factors = np.arange(1, len(eigenvalues) + 1)

        plt.plot(factors, eigenvalues, 'o-', linewidth=2, markersize=8)
        plt.axhline(y=threshold, color='r', linestyle='--', linewidth=2, label=f'Kaiser threshold ({threshold})')

        plt.xlabel('Factor Number', fontsize=12)
        plt.ylabel('Eigenvalue', fontsize=12)
        plt.title('Scree Plot - Factor Eigenvalues', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Mark retained factors
        n_retained = int(np.sum(eigenvalues > threshold))
        plt.axvspan(0.5, n_retained + 0.5, alpha=0.2, color='green', label=f'{n_retained} factors retained')

        filepath = os.path.join(self.output_dir, 'scree_plot.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[Visualizer] Saved scree plot to {filepath}")
        return filepath

    def plot_loadings_heatmap(self, loadings: np.ndarray, benchmarks: List[str],
                                threshold: float = 0.4) -> str:
        """
        Create heatmap of factor loadings.

        Args:
            loadings: [M, n_factors] factor loadings matrix
            benchmarks: List of benchmark names
            threshold: Threshold for significant loadings (default 0.4)

        Returns:
            str: Path to saved figure
        """
        print("\n[Visualizer] Creating factor loadings heatmap...")

        n_factors = loadings.shape[1]
        factor_labels = [f'Factor {i+1}' for i in range(n_factors)]

        plt.figure(figsize=(max(6, n_factors * 2), max(8, len(benchmarks) * 0.5)))

        # Create heatmap
        sns.heatmap(
            loadings,
            annot=True,
            fmt='.2f',
            cmap='RdBu_r',
            center=0,
            vmin=-1,
            vmax=1,
            xticklabels=factor_labels,
            yticklabels=benchmarks,
            cbar_kws={'label': 'Loading'}
        )

        plt.title('Factor Loadings Heatmap', fontsize=14, fontweight='bold')
        plt.xlabel('Factors', fontsize=12)
        plt.ylabel('Benchmarks', fontsize=12)

        filepath = os.path.join(self.output_dir, 'factor_loadings_heatmap.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[Visualizer] Saved loadings heatmap to {filepath}")

        # Print significant loadings
        print(f"[Visualizer] Significant loadings (|loading| > {threshold}):")
        for i, benchmark in enumerate(benchmarks):
            for j in range(n_factors):
                if abs(loadings[i, j]) > threshold:
                    print(f"  {benchmark} → Factor {j+1}: {loadings[i, j]:.3f}")

        return filepath

    def plot_cumulative_variance(self, cumulative_var: np.ndarray, threshold: float = 0.7) -> str:
        """
        Plot cumulative explained variance.

        Args:
            cumulative_var: [n_factors] cumulative variance
            threshold: Gate threshold (default 0.7)

        Returns:
            str: Path to saved figure
        """
        print("\n[Visualizer] Creating cumulative variance plot...")

        plt.figure(figsize=(8, 5))
        factors = np.arange(1, len(cumulative_var) + 1)

        plt.plot(factors, cumulative_var, 'o-', linewidth=2, markersize=8, color='#2ecc71')
        plt.axhline(y=threshold, color='r', linestyle='--', linewidth=2, label=f'Gate threshold ({threshold:.0%})')

        plt.xlabel('Number of Factors', fontsize=12)
        plt.ylabel('Cumulative Variance Explained', fontsize=12)
        plt.title('Cumulative Explained Variance', fontsize=14, fontweight='bold')
        plt.ylim(0, 1.05)
        plt.grid(True, alpha=0.3)
        plt.legend()

        # Annotate final variance
        plt.text(len(cumulative_var), cumulative_var[-1], f'  {cumulative_var[-1]:.2%}',
                 verticalalignment='center', fontsize=11, fontweight='bold')

        filepath = os.path.join(self.output_dir, 'cumulative_variance.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[Visualizer] Saved cumulative variance plot to {filepath}")
        return filepath

    def plot_gate_metrics(self, target: float, actual: float, passed: bool) -> str:
        """
        Create gate pass/fail bar chart.

        Args:
            target: Target cumulative variance (e.g., 0.7)
            actual: Actual cumulative variance
            passed: Whether gate passed

        Returns:
            str: Path to saved figure
        """
        print("\n[Visualizer] Creating gate metrics chart...")

        plt.figure(figsize=(8, 5))

        labels = ['Target\n(70%)', 'Actual\nResult']
        values = [target, actual]
        colors = ['#3498db', '#2ecc71' if passed else '#e74c3c']

        bars = plt.bar(labels, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{val:.1%}',
                     ha='center', va='bottom', fontsize=14, fontweight='bold')

        plt.ylabel('Cumulative Variance Explained', fontsize=12)
        plt.title(f'Gate Check: {"PASSED ✓" if passed else "FAILED ✗"}',
                  fontsize=14, fontweight='bold',
                  color='#2ecc71' if passed else '#e74c3c')
        plt.ylim(0, 1.1)
        plt.grid(axis='y', alpha=0.3)

        filepath = os.path.join(self.output_dir, 'gate_metrics.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"[Visualizer] Saved gate metrics to {filepath}")
        return filepath

    def plot_factor_scores(self, scores: np.ndarray, models: List[str]) -> str:
        """
        Plot model factor scores (2D or 3D scatter).

        Args:
            scores: [N, n_factors] factor scores
            models: List of model names

        Returns:
            str: Path to saved figure
        """
        print("\n[Visualizer] Creating factor scores scatter plot...")

        n_factors = scores.shape[1]

        if n_factors >= 2:
            plt.figure(figsize=(10, 8))

            if n_factors == 2:
                plt.scatter(scores[:, 0], scores[:, 1], s=100, alpha=0.6, edgecolors='black')
                plt.xlabel('Factor 1', fontsize=12)
                plt.ylabel('Factor 2', fontsize=12)
            else:  # n_factors >= 3, use first 2 factors
                plt.scatter(scores[:, 0], scores[:, 1], s=100, alpha=0.6, edgecolors='black')
                plt.xlabel('Factor 1', fontsize=12)
                plt.ylabel('Factor 2', fontsize=12)

            # Annotate some models (top 5 by distance from origin)
            distances = np.linalg.norm(scores[:, :2], axis=1)
            top_indices = np.argsort(distances)[-5:]

            for idx in top_indices:
                plt.annotate(models[idx], (scores[idx, 0], scores[idx, 1]),
                             xytext=(5, 5), textcoords='offset points', fontsize=8)

            plt.title('Model Factor Scores', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
            plt.axvline(x=0, color='k', linestyle='-', linewidth=0.5)

            filepath = os.path.join(self.output_dir, 'factor_scores_scatter.png')
            plt.tight_layout()
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"[Visualizer] Saved factor scores plot to {filepath}")
            return filepath
        else:
            print("[Visualizer] Only 1 factor, skipping scatter plot")
            return None
