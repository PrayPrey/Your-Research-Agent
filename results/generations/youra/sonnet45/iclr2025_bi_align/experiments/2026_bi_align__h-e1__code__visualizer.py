"""Visualization module.

This module generates figures for the validation report.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict
import os


class Visualizer:
    """Visualizer for experimental results."""

    def __init__(self, output_dir: str = "./figures", dpi: int = 300):
        """Initialize visualizer.

        Args:
            output_dir: Directory for output figures
            dpi: Resolution for saved figures
        """
        self.output_dir = output_dir
        self.dpi = dpi

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Set style
        try:
            plt.style.use('seaborn-v0_8-darkgrid')
        except:
            plt.style.use('seaborn-darkgrid')

    def plot_gate_metrics(self, metrics: Dict[str, float],
                         targets: Dict[str, float],
                         output_path: str):
        """Plot gate metrics comparison (MANDATORY).

        Args:
            metrics: Dictionary of actual metric values
            targets: Dictionary of target threshold values
            output_path: Path for output figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Prepare data
        metric_names = list(metrics.keys())
        actual_values = [metrics[k] for k in metric_names]
        target_values = [targets.get(k, 0) for k in metric_names]

        x = np.arange(len(metric_names))
        width = 0.35

        # Plot bars
        bars1 = ax.bar(x - width/2, actual_values, width, label='Actual', color='steelblue')
        bars2 = ax.bar(x + width/2, target_values, width, label='Target', color='orange')

        # Customize
        ax.set_xlabel('Metric')
        ax.set_ylabel('Value')
        ax.set_title('Gate Metrics: Target vs Actual')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved gate metrics plot: {output_path}")

    def plot_distribution(self, features: np.ndarray, marker_name: str,
                         output_path: str):
        """Plot feature distribution histogram.

        Args:
            features: Array of feature values
            marker_name: Name of the marker type
            output_path: Path for output figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot histogram
        ax.hist(features, bins=50, alpha=0.7, color='steelblue', edgecolor='black')

        # Add mean and std lines
        mean = np.mean(features)
        std = np.std(features)
        ax.axvline(mean, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean:.2f}')
        ax.axvline(mean + std, color='orange', linestyle=':', linewidth=1.5, label=f'±1 SD: {std:.2f}')
        ax.axvline(mean - std, color='orange', linestyle=':', linewidth=1.5)

        # Customize
        ax.set_xlabel(f'{marker_name} Frequency (per 100 words)')
        ax.set_ylabel('Count')
        ax.set_title(f'Distribution of {marker_name}')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved distribution plot: {output_path}")

    def plot_split_comparison(self, split_data: Dict[str, np.ndarray],
                             marker_name: str, output_path: str):
        """Plot box plot comparison across splits.

        Args:
            split_data: Dictionary mapping split names to feature arrays
            marker_name: Name of the marker type
            output_path: Path for output figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        data_list = []
        labels = []
        for split_name, features in split_data.items():
            data_list.append(features)
            labels.append(split_name)

        # Plot box plot
        bp = ax.boxplot(data_list, labels=labels, patch_artist=True)

        # Customize boxes
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')

        # Customize
        ax.set_xlabel('Dataset Split')
        ax.set_ylabel(f'{marker_name} Frequency (per 100 words)')
        ax.set_title(f'{marker_name} Distribution Across Splits')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved split comparison plot: {output_path}")

    def plot_correlation(self, modal: np.ndarray, hedging: np.ndarray,
                        output_path: str):
        """Plot correlation scatter plot.

        Args:
            modal: Array of modal verb frequencies
            hedging: Array of hedging marker frequencies
            output_path: Path for output figure
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        # Plot scatter
        ax.scatter(modal, hedging, alpha=0.1, s=10, color='steelblue')

        # Add correlation coefficient
        corr = np.corrcoef(modal, hedging)[0, 1]

        # Customize
        ax.set_xlabel('Modal Verb Frequency (per 100 words)')
        ax.set_ylabel('Hedging Marker Frequency (per 100 words)')
        ax.set_title(f'Modal vs Hedging Correlation (r={corr:.3f})')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Saved correlation plot: {output_path}")
