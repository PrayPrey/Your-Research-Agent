"""
Visualizer: Generate figures for validation report
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class Visualizer:
    """Visualization generator for experiment results"""

    def __init__(self, config):
        """Initialize with visualization configuration."""
        self.dpi = config.dpi
        self.figure_format = config.figure_format
        self.color_pass = config.color_pass
        self.color_fail = config.color_fail

        # Set style
        sns.set_style("whitegrid")

        logger.info("Visualizer initialized")

    def plot_kappa_results(self, kappa_results: Dict, output_path: Path) -> None:
        """
        Plot kappa values by section with threshold line.
        Args:
            kappa_results: Dict of {section: {kappa, ci_lower, ci_upper, pass}}
            output_path: Path to save figure
        """
        logger.info(f"Generating kappa results plot: {output_path}")

        fig, ax = plt.subplots(figsize=(10, 6))

        sections = list(kappa_results.keys())
        kappas = [v['kappa'] for v in kappa_results.values()]
        ci_lowers = [v['ci_lower'] for v in kappa_results.values()]
        ci_uppers = [v['ci_upper'] for v in kappa_results.values()]
        colors = [self.color_pass if v['pass'] else self.color_fail for v in kappa_results.values()]

        # Plot bars
        x = np.arange(len(sections))
        bars = ax.bar(x, kappas, color=colors, alpha=0.7, edgecolor='black')

        # Add error bars (CI)
        yerr_lower = [kappas[i] - ci_lowers[i] for i in range(len(kappas))]
        yerr_upper = [ci_uppers[i] - kappas[i] for i in range(len(kappas))]
        ax.errorbar(x, kappas, yerr=[yerr_lower, yerr_upper], fmt='none', ecolor='black', capsize=5)

        # Add threshold line
        threshold = kappa_results[sections[0]].get('threshold', 0.60)  # Default 0.60
        ax.axhline(y=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold (κ={threshold})')

        # Labels and formatting
        ax.set_xlabel('DTS Section', fontsize=12, fontweight='bold')
        ax.set_ylabel("Cohen's Kappa (κ)", fontsize=12, fontweight='bold')
        ax.set_title("Inter-Annotator Agreement by Section", fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([s.replace('_', ' ') for s in sections], rotation=45, ha='right')
        ax.set_ylim([0, 1.0])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, format=self.figure_format)
        plt.close()

        logger.info(f"  Saved to {output_path}")

    def plot_agreement_heatmap(self, aligned_df: pd.DataFrame, output_path: Path) -> None:
        """
        Plot agreement heatmap for all annotations.
        Args:
            aligned_df: DataFrame with columns [field_id, section_A, section_B, ...]
            output_path: Path to save figure
        """
        logger.info(f"Generating agreement heatmap: {output_path}")

        # Extract section columns (those with _A suffix)
        section_cols_a = [col for col in aligned_df.columns if col.endswith('_A')]
        section_cols_b = [col for col in aligned_df.columns if col.endswith('_B')]

        # Create agreement matrix (1 = agree, 0 = disagree)
        n_samples = len(aligned_df)
        n_sections = len(section_cols_a)
        agreement_matrix = np.zeros((n_samples, n_sections))

        for i, (col_a, col_b) in enumerate(zip(section_cols_a, section_cols_b)):
            coder_a = aligned_df[col_a].values
            coder_b = aligned_df[col_b].values
            agreement_matrix[:, i] = (coder_a == coder_b).astype(int)

        # Extract section names for display
        sections = [col.replace('_A', '') for col in section_cols_a]

        # Plot heatmap (sample first 30 rows for readability)
        fig, ax = plt.subplots(figsize=(8, 10))
        sns.heatmap(
            agreement_matrix[:30],  # First 30 samples
            cmap=['red', 'green'],
            cbar_kws={'label': '0=Disagree, 1=Agree'},
            xticklabels=[s.replace('_', ' ') for s in sections],
            yticklabels=range(1, 31),
            ax=ax
        )

        ax.set_xlabel('DTS Section', fontsize=12, fontweight='bold')
        ax.set_ylabel('Field Sample', fontsize=12, fontweight='bold')
        ax.set_title('Inter-Annotator Agreement Heatmap (First 30 Samples)', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, format=self.figure_format)
        plt.close()

        logger.info(f"  Saved to {output_path}")

    def plot_probe_results(self, y_true: np.ndarray, y_pred: np.ndarray, output_path: Path) -> None:
        """
        Plot confusion matrix for linear probe results.
        Args:
            y_true: True labels
            y_pred: Predicted labels
            output_path: Path to save figure
        """
        logger.info(f"Generating probe confusion matrix: {output_path}")

        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

        # Compute confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        # Plot
        fig, ax = plt.subplots(figsize=(8, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['General Info', 'Responsible AI'])
        disp.plot(ax=ax, cmap='Blues', values_format='d')

        ax.set_title('Linear Probe Confusion Matrix', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, format=self.figure_format)
        plt.close()

        logger.info(f"  Saved to {output_path}")
