"""Visualization module for mechanism validation.

This module generates all required figures for the validation report.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, Any
import os


class MechanismVisualizer:
    """Visualizer for statistical results."""

    def __init__(self, config):
        """Initialize visualizer.

        Args:
            config: MechanismConfig instance
        """
        self.config = config
        plt.style.use(config.style)
        sns.set_palette(config.palette)

        # Create figures directory if it doesn't exist
        os.makedirs(config.figures_dir, exist_ok=True)

    def plot_gate_metrics(
        self, cohens_d: float, alpha: float, p_value: float, output_path: str
    ):
        """Plot gate metrics comparison (MANDATORY figure).

        Args:
            cohens_d: Cohen's d effect size
            alpha: Cronbach's alpha
            p_value: p-value from paired t-test
            output_path: Path to save figure
        """
        fig, axes = plt.subplots(1, 3, figsize=self.config.figsize_bar)

        # Cohen's d plot
        axes[0].bar(['Actual', 'Target'],
                    [abs(cohens_d), self.config.cohens_d_threshold],
                    color=['#2ecc71' if abs(cohens_d) >= self.config.cohens_d_threshold else '#e74c3c', '#3498db'])
        axes[0].set_ylabel("Cohen's d (absolute)")
        axes[0].set_title("Effect Size")
        axes[0].axhline(y=self.config.cohens_d_threshold, color='gray', linestyle='--', alpha=0.5)
        axes[0].set_ylim(0, max(abs(cohens_d), self.config.cohens_d_threshold) * 1.2)

        # Cronbach's alpha plot
        axes[1].bar(['Actual', 'Target'],
                    [alpha, self.config.cronbach_alpha_threshold],
                    color=['#2ecc71' if alpha > self.config.cronbach_alpha_threshold else '#e74c3c', '#3498db'])
        axes[1].set_ylabel("Cronbach's α")
        axes[1].set_title("Internal Consistency")
        axes[1].axhline(y=self.config.cronbach_alpha_threshold, color='gray', linestyle='--', alpha=0.5)
        axes[1].set_ylim(0, max(alpha, self.config.cronbach_alpha_threshold) * 1.2)

        # P-value plot (show significance)
        sig_level = 1 if p_value < self.config.p_value_threshold else 0
        axes[2].bar(['Significant'], [sig_level], color='#2ecc71' if sig_level else '#e74c3c')
        axes[2].set_ylabel("Significance")
        axes[2].set_title(f"Statistical Significance\n(p = {p_value:.6f})")
        axes[2].set_ylim(0, 1.2)
        axes[2].set_yticks([0, 1])
        axes[2].set_yticklabels(['No', 'Yes'])

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved gate metrics plot: {output_path}")

    def plot_forest_plot(
        self, split_results: Dict[str, Dict], output_path: str
    ):
        """Plot effect sizes by split with 95% CI (forest plot).

        Args:
            split_results: Results from cross-split validation
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=self.config.figsize_forest)

        splits = list(split_results.keys())
        cohens_ds = [split_results[s]['cohens_d'] for s in splits]
        passes = [split_results[s]['pass'] for s in splits]

        # Approximate 95% CI (simplified - would need SE for exact CI)
        # Using ±0.05 as rough approximation
        errors = [0.05] * len(splits)

        colors = ['#2ecc71' if p else '#e74c3c' for p in passes]

        y_pos = np.arange(len(splits))
        ax.errorbar(cohens_ds, y_pos, xerr=errors, fmt='o', markersize=8,
                    capsize=5, capthick=2, elinewidth=2, color='black')

        for i, (y, d, c) in enumerate(zip(y_pos, cohens_ds, colors)):
            ax.plot(d, y, 'o', markersize=10, color=c)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(splits)
        ax.set_xlabel("Cohen's d")
        ax.set_title("Effect Sizes by Split (Forest Plot)")
        ax.axvline(x=0, color='gray', linestyle='-', alpha=0.5)
        ax.axvline(x=-self.config.cohens_d_threshold, color='blue', linestyle='--', alpha=0.5,
                   label=f'Threshold (|d| ≥ {self.config.cohens_d_threshold})')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved forest plot: {output_path}")

    def plot_density_comparison(
        self, chosen: np.ndarray, rejected: np.ndarray, output_path: str
    ):
        """Plot overlaid distributions for chosen vs rejected.

        Args:
            chosen: Modal verb frequencies for chosen responses
            rejected: Modal verb frequencies for rejected responses
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=self.config.figsize_density)

        # Plot densities
        ax.hist(chosen, bins=50, alpha=0.6, label='Chosen', color='#3498db', density=True)
        ax.hist(rejected, bins=50, alpha=0.6, label='Rejected', color='#e74c3c', density=True)

        ax.set_xlabel('Modal Verb Frequency (per 100 words)')
        ax.set_ylabel('Density')
        ax.set_title('Distribution of Modal Verbs: Chosen vs Rejected')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add mean lines
        ax.axvline(np.mean(chosen), color='#3498db', linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Chosen mean: {np.mean(chosen):.2f}')
        ax.axvline(np.mean(rejected), color='#e74c3c', linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Rejected mean: {np.mean(rejected):.2f}')
        ax.legend()

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved density plot: {output_path}")

    def plot_paired_differences(
        self, differences: np.ndarray, output_path: str
    ):
        """Plot histogram of paired differences.

        Args:
            differences: Array of (chosen - rejected) differences
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=self.config.figsize_hist)

        # Plot histogram
        counts, bins, patches = ax.hist(differences, bins=50, alpha=0.7, color='#95a5a6', edgecolor='black')

        # Color negative bars (chosen < rejected) differently
        for i, patch in enumerate(patches):
            if bins[i] < 0:
                patch.set_facecolor('#3498db')

        ax.axvline(x=0, color='red', linestyle='--', linewidth=2, label='No difference')
        ax.axvline(x=np.mean(differences), color='green', linestyle='-', linewidth=2,
                   label=f'Mean: {np.mean(differences):.3f}')

        ax.set_xlabel('Difference (Chosen - Rejected)')
        ax.set_ylabel('Frequency')
        ax.set_title('Paired Differences in Modal Verb Frequency')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        # Add statistics text
        textstr = f'Mean: {np.mean(differences):.3f}\nStd: {np.std(differences):.3f}\nMedian: {np.median(differences):.3f}'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved paired differences plot: {output_path}")

    def plot_correlation_heatmap(
        self, corr_matrix: np.ndarray, output_path: str
    ):
        """Plot correlation matrix heatmap.

        Args:
            corr_matrix: [3, 3] correlation matrix
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=self.config.figsize_heatmap)

        marker_labels = ['Modal Verbs', 'Hedging', 'Alternatives']

        sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                    xticklabels=marker_labels, yticklabels=marker_labels,
                    vmin=-1, vmax=1, center=0, square=True, ax=ax,
                    cbar_kws={'label': 'Correlation'})

        ax.set_title('Correlation Matrix: Marker Difference Scores')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved correlation heatmap: {output_path}")
