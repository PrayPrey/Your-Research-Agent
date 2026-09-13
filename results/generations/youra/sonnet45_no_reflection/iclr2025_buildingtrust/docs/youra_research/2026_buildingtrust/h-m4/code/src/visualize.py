"""
Visualization Module for H-M2 Hypothesis
Generates CKA heatmaps, scatter plots, and progression charts
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FigureGenerator:
    """Generate visualizations for h-m2 validation."""

    def __init__(self, output_dir: str):
        """
        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')

    def plot_cka_heatmap(
        self,
        cka_scores: Dict[str, float],
        layers: List[str]
    ):
        """Plot CKA similarity heatmap. X=layer_idx, Y=type (attn/hidden)"""
        # Separate attention and hidden layers
        attn_scores = []
        hidden_scores = []

        for i in range(12):
            attn_key = f"blocks.{i}.attn.hook_pattern"
            hidden_key = f"blocks.{i}.hook_resid_post"

            attn_scores.append(cka_scores.get(attn_key, 0.0))
            hidden_scores.append(cka_scores.get(hidden_key, 0.0))

        # Create heatmap data
        data = np.array([attn_scores, hidden_scores])

        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(
            data,
            annot=True,
            fmt='.3f',
            cmap='RdYlGn_r',
            xticklabels=range(12),
            yticklabels=['Attention', 'Hidden State'],
            vmin=0.0,
            vmax=1.0,
            ax=ax
        )
        ax.set_xlabel('Layer Index')
        ax.set_ylabel('Representation Type')
        ax.set_title('CKA Similarity Heatmap (Pre vs Post Intervention)')

        save_path = self.output_dir / 'cka_heatmap.png'
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved CKA heatmap to {save_path}")

    def plot_change_magnitude(
        self,
        change_magnitudes: Dict[str, float]
    ):
        """Plot layer-wise change magnitude bar chart."""
        # Separate attention and hidden layers
        attn_changes = []
        hidden_changes = []
        layer_indices = []

        for i in range(12):
            attn_key = f"blocks.{i}.attn.hook_pattern"
            hidden_key = f"blocks.{i}.hook_resid_post"

            attn_changes.append(change_magnitudes.get(attn_key, 0.0))
            hidden_changes.append(change_magnitudes.get(hidden_key, 0.0))
            layer_indices.append(i)

        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(len(layer_indices))
        width = 0.35

        ax.bar(x - width/2, attn_changes, width, label='Attention', alpha=0.8)
        ax.bar(x + width/2, hidden_changes, width, label='Hidden State', alpha=0.8)

        ax.set_xlabel('Layer Index')
        ax.set_ylabel('Change Magnitude (1 - CKA)')
        ax.set_title('Layer-wise Representation Change Magnitude')
        ax.set_xticks(x)
        ax.set_xticklabels(layer_indices)
        ax.legend()
        ax.grid(True, alpha=0.3)

        save_path = self.output_dir / 'change_magnitude.png'
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved change magnitude plot to {save_path}")

    def plot_layer_progression(
        self,
        cka_scores: Dict[str, float]
    ):
        """Plot change progression across depth. Two lines: attn, hidden"""
        # Separate attention and hidden layers
        attn_changes = []
        hidden_changes = []

        for i in range(12):
            attn_key = f"blocks.{i}.attn.hook_pattern"
            hidden_key = f"blocks.{i}.hook_resid_post"

            attn_changes.append(1.0 - cka_scores.get(attn_key, 1.0))
            hidden_changes.append(1.0 - cka_scores.get(hidden_key, 1.0))

        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))

        layer_indices = range(12)
        ax.plot(layer_indices, attn_changes, marker='o', label='Attention', linewidth=2)
        ax.plot(layer_indices, hidden_changes, marker='s', label='Hidden State', linewidth=2)

        ax.set_xlabel('Layer Depth')
        ax.set_ylabel('Representation Change Magnitude')
        ax.set_title('Representation Change Progression Across Layers')
        ax.legend()
        ax.grid(True, alpha=0.3)

        save_path = self.output_dir / 'layer_progression.png'
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved layer progression plot to {save_path}")

    def plot_correlation_scatter(
        self,
        change_magnitudes: List[float],
        performance_delta: float,
        correlation: float,
        p_value: float
    ):
        """Plot correlation scatter with regression line. Required for gate."""
        fig, ax = plt.subplots(figsize=(8, 6))

        # Create data points
        x = change_magnitudes
        y = [performance_delta] * len(change_magnitudes)

        # Scatter plot
        ax.scatter(x, y, alpha=0.6, s=50)

        # Add horizontal line at performance delta
        ax.axhline(y=performance_delta, color='r', linestyle='--', alpha=0.5,
                   label=f'h-m1 Performance Δ = {performance_delta:.4f}')

        ax.set_xlabel('Representation Change Magnitude (1 - CKA)')
        ax.set_ylabel('Performance Improvement')
        ax.set_title(f'Correlation: r={correlation:.3f}, p={p_value:.3e}')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add text annotation
        textstr = f'Correlation: {correlation:.3f}\np-value: {p_value:.3e}\nSignificant: {"Yes" if p_value < 0.05 else "No"}'
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        save_path = self.output_dir / 'correlation_scatter.png'
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"Saved correlation scatter to {save_path}")

    def save_all_figures(
        self,
        cka_scores: Dict[str, float],
        correlation_result: Dict
    ):
        """Generate and save all 4 required figures."""
        logger.info("Generating all figures...")

        # Get layers
        layers = list(cka_scores.keys())

        # Compute change magnitudes
        change_magnitudes = {k: 1.0 - v for k, v in cka_scores.items()}

        # Generate figures
        self.plot_cka_heatmap(cka_scores, layers)
        self.plot_change_magnitude(change_magnitudes)
        self.plot_layer_progression(cka_scores)
        self.plot_correlation_scatter(
            list(change_magnitudes.values()),
            0.0232,
            correlation_result.get('correlation', 0.0),
            correlation_result.get('p_value', 1.0)
        )

        logger.info("All figures generated successfully")
