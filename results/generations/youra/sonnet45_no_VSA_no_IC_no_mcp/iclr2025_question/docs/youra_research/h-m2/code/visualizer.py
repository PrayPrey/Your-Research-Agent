"""Visualization generation for H-M2 validation."""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


class Gate2Visualizer:
    """Generate visualizations for Gate 2 validation."""

    def __init__(self, output_dir: str):
        """Initialize with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_error_reduction_histogram(self, reductions: np.ndarray):
        """Plot histogram of per-hypothesis error reduction percentages."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(reductions, bins=20, alpha=0.7, edgecolor='black', color='#2ca02c')
        ax.axvline(40.0, color='red', linestyle='--', linewidth=2, label='Target (40%)')
        ax.set_xlabel('Error Reduction (%)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Error Reduction (Gate 1 → Gate 2)', fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'error_reduction_histogram.png', dpi=300)
        plt.close(fig)

    def plot_gate_comparison_scatter(self, O_full: np.ndarray, pred_g1: np.ndarray, pred_g2: np.ndarray):
        """Plot O_pred vs O_full for both gates."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(O_full, pred_g1, alpha=0.7, s=100, edgecolor='black', linewidth=0.5,
                   color='#1f77b4', label='Gate 1 Prior')
        ax.scatter(O_full, pred_g2, alpha=0.7, s=100, edgecolor='black', linewidth=0.5,
                   color='#ff7f0e', label='Gate 2 Posterior')
        # Diagonal line (perfect prediction)
        lim = [O_full.min(), O_full.max()]
        ax.plot(lim, lim, 'k--', alpha=0.5, linewidth=2)
        ax.set_xlabel('O_full (Ground Truth)', fontsize=12)
        ax.set_ylabel('O_pred (Predicted)', fontsize=12)
        ax.set_title('Prediction Accuracy: Gate 1 vs Gate 2', fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'gate_comparison_scatter.png', dpi=300)
        plt.close(fig)

    def plot_paired_errors(self, errors_g1: np.ndarray, errors_g2: np.ndarray):
        """Plot paired error comparison with connecting lines."""
        fig, ax = plt.subplots(figsize=(10, 6))
        n = len(errors_g1)
        x = np.arange(n)
        for i in range(n):
            ax.plot([0, 1], [errors_g1[i], errors_g2[i]], 'o-', color='gray', alpha=0.5)
        ax.scatter([0]*n, errors_g1, color='#1f77b4', s=100, alpha=0.7, label='Gate 1', zorder=3)
        ax.scatter([1]*n, errors_g2, color='#ff7f0e', s=100, alpha=0.7, label='Gate 2', zorder=3)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Gate 1', 'Gate 2'])
        ax.set_ylabel('Relative Error', fontsize=12)
        ax.set_title('Paired Error Comparison (Each Line = One Hypothesis)', fontsize=14)
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'paired_errors.png', dpi=300)
        plt.close(fig)

    def plot_boxplot_comparison(self, errors_g1: np.ndarray, errors_g2: np.ndarray, p_value: float):
        """Plot box plot comparing Gate 1 vs Gate 2 errors with p-value annotation."""
        fig, ax = plt.subplots(figsize=(8, 6))
        data = [errors_g1, errors_g2]
        bp = ax.boxplot(data, widths=0.6, showmeans=True, meanline=True, patch_artist=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2),
                        meanprops=dict(color='green', linewidth=2))
        ax.set_xticklabels(['Gate 1', 'Gate 2'])
        ax.set_ylabel('Relative Error', fontsize=12)
        ax.set_title('Statistical Comparison of Prediction Errors', fontsize=14)
        # Add p-value annotation
        y_max = max(errors_g1.max(), errors_g2.max())
        ax.text(1.5, y_max * 0.9, f'p-value = {p_value:.4f}',
                fontsize=12, bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        ax.grid(alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig(self.output_dir / 'statistical_comparison_boxplot.png', dpi=300)
        plt.close(fig)

    def plot_metrics_comparison(self, target_reduction: float, actual_reduction: float,
                                target_pvalue: float, actual_pvalue: float):
        """Plot target vs actual metrics bar chart (MANDATORY figure)."""
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        # Error reduction comparison
        ax[0].bar(['Target', 'Actual'], [target_reduction, actual_reduction],
                  color=['#cccccc', '#2ca02c'], edgecolor='black', linewidth=1.5)
        ax[0].axhline(40.0, color='red', linestyle='--', linewidth=2, label='Threshold (40%)')
        ax[0].set_ylabel('Error Reduction (%)', fontsize=12)
        ax[0].set_title('Error Reduction: Target vs Actual', fontsize=14)
        ax[0].legend()
        ax[0].grid(alpha=0.3, axis='y')

        # p-value comparison
        ax[1].bar(['Target', 'Actual'], [target_pvalue, actual_pvalue],
                  color=['#cccccc', '#ff7f0e'], edgecolor='black', linewidth=1.5)
        ax[1].axhline(0.05, color='red', linestyle='--', linewidth=2, label='Significance (p<0.05)')
        ax[1].set_ylabel('p-value', fontsize=12)
        ax[1].set_title('Statistical Significance: Target vs Actual', fontsize=14)
        ax[1].legend()
        ax[1].grid(alpha=0.3, axis='y')
        ax[1].set_ylim(0, max(0.1, actual_pvalue * 1.2))

        plt.tight_layout()
        plt.savefig(self.output_dir / 'metrics_comparison.png', dpi=300)
        plt.close(fig)
