"""
Experiment Visualizer
Generates all required figures for h-e1 experiment
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc
from scipy.stats import gaussian_kde

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import VISUALIZATION_CONFIG


class ExperimentVisualizer:
    """Generate experiment figures."""

    def __init__(self, output_dir: str = None):
        """
        Initialize visualizer.

        Args:
            output_dir: directory to save figures (default from config)
        """
        self.config = VISUALIZATION_CONFIG
        self.output_dir = output_dir or self.config["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_gate_metrics(self, r: float, rho: float, p_r: float, p_rho: float):
        """
        MANDATORY gate metrics comparison plot.

        Args:
            r: Pearson correlation coefficient
            rho: Spearman correlation coefficient
            p_r: p-value for Pearson
            p_rho: p-value for Spearman
        """
        cfg = self.config["gate_plot"]
        target = cfg["target_correlation"]

        fig, ax = plt.subplots(figsize=self.config["figsize"])

        # Bar positions
        x = np.arange(2)
        width = cfg["bar_width"]

        # Plot bars
        bars = ax.bar(x, [r, rho], width, label="Observed", color=self.config["colors"]["success"])
        ax.axhline(y=target, color=self.config["colors"]["target"], linestyle="--", linewidth=2, label=f"Target (r={target})")

        # Labels
        ax.set_ylabel("Correlation Coefficient", fontsize=12)
        ax.set_title("Gate Condition: Correlation Metrics", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(["Pearson r", "Spearman ρ"], fontsize=11)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')

        # P-values as text
        if cfg["show_pvalue"]:
            ax.text(0, r + 0.02, f"p={p_r:.4f}", ha="center", fontsize=9)
            ax.text(1, rho + 0.02, f"p={p_rho:.4f}", ha="center", fontsize=9)

        # Gate result annotation
        gate_pass = (r > target) or (rho > target)
        result_text = "PASS" if gate_pass else "FAIL"
        result_color = self.config["colors"]["success"] if gate_pass else self.config["colors"]["timeout"]
        ax.text(0.98, 0.98, f"Gate: {result_text}", transform=ax.transAxes,
                fontsize=14, fontweight='bold', color=result_color,
                ha='right', va='top',
                bbox=dict(boxstyle='round', facecolor='white', edgecolor=result_color, linewidth=2))

        plt.tight_layout()
        output_path = f"{self.output_dir}/gate_metrics.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")

    def plot_scatter(self, derivatives: np.ndarray, outcomes: np.ndarray):
        """
        Scatter plot: confidence derivative vs timeout outcome.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]
        """
        cfg = self.config["scatter"]

        fig, ax = plt.subplots(figsize=self.config["figsize"])

        # Add jitter to binary outcomes for visibility
        np.random.seed(42)
        outcomes_jittered = outcomes + np.random.uniform(-cfg["jitter"], cfg["jitter"], size=len(outcomes))

        # Separate by outcome
        success_mask = outcomes == 0
        timeout_mask = outcomes == 1

        ax.scatter(derivatives[success_mask], outcomes_jittered[success_mask],
                   c=self.config["colors"]["success"], label="Success",
                   alpha=cfg["alpha"], s=cfg["marker_size"])
        ax.scatter(derivatives[timeout_mask], outcomes_jittered[timeout_mask],
                   c=self.config["colors"]["timeout"], label="Timeout",
                   alpha=cfg["alpha"], s=cfg["marker_size"])

        ax.set_xlabel("Confidence Derivative (Entropy Std Dev)", fontsize=12)
        ax.set_ylabel("Outcome (0=Success, 1=Timeout)", fontsize=12)
        ax.set_title("Confidence Derivative vs Timeout Outcome", fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.set_ylim(-0.2, 1.2)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = f"{self.output_dir}/scatter_plot.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")

    def plot_distributions(self, derivatives: np.ndarray, outcomes: np.ndarray):
        """
        Distribution comparison: success vs timeout groups.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]
        """
        cfg = self.config["distribution"]

        fig, ax = plt.subplots(figsize=self.config["figsize"])

        success_derivatives = derivatives[outcomes == 0]
        timeout_derivatives = derivatives[outcomes == 1]

        # Histograms
        ax.hist(success_derivatives, bins=cfg["bins"], alpha=cfg["alpha"],
                color=self.config["colors"]["success"], label=f"Success (n={len(success_derivatives)})", density=True)
        ax.hist(timeout_derivatives, bins=cfg["bins"], alpha=cfg["alpha"],
                color=self.config["colors"]["timeout"], label=f"Timeout (n={len(timeout_derivatives)})", density=True)

        # KDE overlay
        if cfg["kde"]:
            if len(success_derivatives) > 1:
                kde_success = gaussian_kde(success_derivatives)
                x_range = np.linspace(derivatives.min(), derivatives.max(), 100)
                ax.plot(x_range, kde_success(x_range), color=self.config["colors"]["success"], linewidth=2, linestyle='--')
            if len(timeout_derivatives) > 1:
                kde_timeout = gaussian_kde(timeout_derivatives)
                x_range = np.linspace(derivatives.min(), derivatives.max(), 100)
                ax.plot(x_range, kde_timeout(x_range), color=self.config["colors"]["timeout"], linewidth=2, linestyle='--')

        ax.set_xlabel("Confidence Derivative", fontsize=12)
        ax.set_ylabel("Density", fontsize=12)
        ax.set_title("Distribution of Confidence Derivatives by Outcome", fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = f"{self.output_dir}/distributions.png"
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

    def plot_roc_curve(self, derivatives: np.ndarray, outcomes: np.ndarray):
        """
        ROC curve for binary classification.

        Args:
            derivatives: confidence derivatives, shape [N]
            outcomes: binary outcomes (0=success, 1=timeout), shape [N]
        """
        cfg = self.config["roc"]

        fig, ax = plt.subplots(figsize=self.config["figsize"])

        # Compute ROC curve
        fpr, tpr, _ = roc_curve(outcomes, derivatives)
        roc_auc = auc(fpr, tpr)

        ax.plot(fpr, tpr, color=self.config["colors"]["success"],
                linewidth=cfg["linewidth"],
                label=f"ROC Curve (AUC = {roc_auc:.3f})")

        if cfg["show_diagonal"]:
            ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1, label="Random Classifier")

        ax.set_xlabel("False Positive Rate", fontsize=12)
        ax.set_ylabel("True Positive Rate", fontsize=12)
        ax.set_title("ROC Curve: Confidence Derivative as Timeout Predictor", fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        output_path = f"{self.output_dir}/roc_curve.png"
        plt.savefig(output_path, dpi=self.config["dpi"], format=self.config["format"])
        plt.close()
        print(f"  Saved: {output_path}")
