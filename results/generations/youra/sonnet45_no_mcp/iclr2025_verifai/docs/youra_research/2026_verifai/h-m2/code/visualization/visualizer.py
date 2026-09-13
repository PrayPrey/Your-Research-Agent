"""
Experiment Visualizer for h-m1
Generates variance comparison figures for mechanism hypothesis
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VISUALIZATION_CONFIG


class ExperimentVisualizer:
    """Generate experiment figures for h-m1 variance analysis."""

    def __init__(self, output_dir: str = None):
        """
        Initialize visualizer.

        Args:
            output_dir: directory to save figures (default from config)
        """
        self.config = VISUALIZATION_CONFIG
        self.output_dir = output_dir or self.config["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_variance_comparison_bar(self, analysis: dict):
        """
        MANDATORY gate metrics comparison plot for h-m1.
        Bar chart comparing mean variance between successful and timeout groups.

        Args:
            analysis: output from VarianceGroupAnalyzer.analyze_by_outcome()
        """
        fig, ax = plt.subplots(figsize=self.config["figsize"])

        # Extract data
        groups = ['Successful', 'Timeout']
        means = [
            analysis['successful']['mean_variance'],
            analysis['timeout']['mean_variance']
        ]
        stds = [
            analysis['successful']['std_variance'],
            analysis['timeout']['std_variance']
        ]
        counts = [
            analysis['successful']['count'],
            analysis['timeout']['count']
        ]

        # Bar positions
        x = np.arange(len(groups))
        width = 0.6

        # Plot bars with error bars
        colors = [self.config["colors"]["success"], self.config["colors"]["timeout"]]
        bars = ax.bar(x, means, width, yerr=stds, capsize=5,
                      color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

        # Labels
        ax.set_ylabel("Mean Confidence Variance (Entropy Std Dev)", fontsize=12)
        ax.set_title("Gate Condition: Variance Comparison by Outcome", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f"{g}\n(n={c})" for g, c in zip(groups, counts)], fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for i, (bar, mean) in enumerate(zip(bars, means)):
            ax.text(bar.get_x() + bar.get_width()/2, mean + stds[i] + 0.01,
                   f'{mean:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Gate result annotation
        gate_pass = analysis['successful']['mean_variance'] < analysis['timeout']['mean_variance']
        result_text = "PASS" if gate_pass else "FAIL"
        result_color = self.config["colors"]["success"] if gate_pass else self.config["colors"]["timeout"]

        ax.text(0.98, 0.98, f"Gate: {result_text}", transform=ax.transAxes,
                fontsize=14, fontweight='bold', color=result_color,
                ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=result_color, linewidth=2))

        # Add statistics
        stats_text = f"p-value: {analysis['p_value']:.2e}\nt-statistic: {analysis['t_statistic']:.2f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                fontsize=9, ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        plt.tight_layout()
        output_path = f"{self.output_dir}/gate_metrics.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")

    def plot_variance_distributions(self, variances: np.ndarray, outcomes: np.ndarray):
        """
        Distribution comparison: variance distributions by outcome group.

        Args:
            variances: confidence variances, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]
        """
        cfg = self.config["distribution"]

        fig, ax = plt.subplots(figsize=self.config["figsize"])

        success_variances = variances[outcomes == 0]
        timeout_variances = variances[outcomes == 1]

        # Histograms
        ax.hist(success_variances, bins=cfg["bins"], alpha=cfg["alpha"],
                color=self.config["colors"]["success"], label=f"Success (n={len(success_variances)})", density=True)
        ax.hist(timeout_variances, bins=cfg["bins"], alpha=cfg["alpha"],
                color=self.config["colors"]["timeout"], label=f"Timeout (n={len(timeout_variances)})", density=True)

        # KDE overlay
        if cfg["kde"]:
            if len(success_variances) > 1:
                kde_success = gaussian_kde(success_variances)
                x_range = np.linspace(variances.min(), variances.max(), 100)
                ax.plot(x_range, kde_success(x_range), color=self.config["colors"]["success"], linewidth=2, linestyle='--')
            if len(timeout_variances) > 1:
                kde_timeout = gaussian_kde(timeout_variances)
                x_range = np.linspace(variances.min(), variances.max(), 100)
                ax.plot(x_range, kde_timeout(x_range), color=self.config["colors"]["timeout"], linewidth=2, linestyle='--')

        ax.set_xlabel("Confidence Variance (Entropy Std Dev)", fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.set_title("Distribution of Confidence Variance by Outcome", fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = f"{self.output_dir}/distributions.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")

    def plot_variance_boxplot(self, variances: np.ndarray, outcomes: np.ndarray):
        """
        Box plot comparing variance distributions.

        Args:
            variances: confidence variances, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]
        """
        fig, ax = plt.subplots(figsize=self.config["figsize"])

        success_variances = variances[outcomes == 0]
        timeout_variances = variances[outcomes == 1]

        # Create box plot
        positions = [1, 2]
        box_data = [success_variances, timeout_variances]
        bp = ax.boxplot(box_data, positions=positions, widths=0.6,
                        patch_artist=True, showmeans=True,
                        meanprops=dict(marker='D', markerfacecolor='red', markersize=8))

        # Color boxes
        colors = [self.config["colors"]["success"], self.config["colors"]["timeout"]]
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Labels
        ax.set_ylabel("Confidence Variance (Entropy Std Dev)", fontsize=12)
        ax.set_title("Variance Distribution by Outcome (Box Plot)", fontsize=14, fontweight='bold')
        ax.set_xticks(positions)
        ax.set_xticklabels([f"Successful\n(n={len(success_variances)})",
                           f"Timeout\n(n={len(timeout_variances)})"], fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_path = f"{self.output_dir}/variance_boxplot.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")

    def plot_trajectory_examples(self, trajectories: list, outcomes: list):
        """
        Plot entropy trajectories for example theorems.

        Args:
            trajectories: list of entropy trajectories (list of lists)
            outcomes: list of outcomes (0=success, 1=timeout)
        """
        cfg = self.config["trajectory"]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Select examples
        success_indices = [i for i, o in enumerate(outcomes) if o == 0][:cfg["n_examples_per_class"]]
        timeout_indices = [i for i, o in enumerate(outcomes) if o == 1][:cfg["n_examples_per_class"]]

        # Plot success trajectories
        for idx in success_indices:
            if idx < len(trajectories) and len(trajectories[idx]) > 0:
                ax1.plot(trajectories[idx], linewidth=cfg["linewidth"],
                        color=self.config["colors"]["success"], alpha=0.7)
        ax1.set_xlabel("Proof Step", fontsize=11)
        ax1.set_ylabel("Entropy", fontsize=11)
        ax1.set_title("Success Examples (Low Variance)", fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Plot timeout trajectories
        for idx in timeout_indices:
            if idx < len(trajectories) and len(trajectories[idx]) > 0:
                ax2.plot(trajectories[idx], linewidth=cfg["linewidth"],
                        color=self.config["colors"]["timeout"], alpha=0.7)
        ax2.set_xlabel("Proof Step", fontsize=11)
        ax2.set_ylabel("Entropy", fontsize=11)
        ax2.set_title("Timeout Examples (High Variance)", fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = f"{self.output_dir}/trajectory_examples.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")
