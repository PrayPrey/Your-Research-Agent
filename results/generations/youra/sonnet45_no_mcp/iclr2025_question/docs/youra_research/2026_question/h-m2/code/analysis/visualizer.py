"""Visualization generation for error signature analysis."""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict


class SignatureVisualizer:
    """Generate visualizations for error signature analysis."""

    def __init__(self):
        """Initialize visualizer."""
        sns.set_style("whitegrid")

    def plot_gate_comparison(
        self,
        nq_div_mean: float,
        tqa_div_mean: float,
        output_path: str
    ):
        """
        Generate gate metrics comparison bar chart.

        Args:
            nq_div_mean: NQ diversity mean
            tqa_div_mean: TQA diversity mean
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        datasets = ['NaturalQuestions\n(Knowledge Gaps)', 'TruthfulQA\n(Misconceptions)']
        means = [nq_div_mean, tqa_div_mean]
        colors = ['#2E86AB', '#A23B72']

        bars = ax.bar(datasets, means, color=colors, alpha=0.7)

        ax.set_ylabel('Mean Semantic Diversity', fontsize=12)
        ax.set_title('Gate Metrics Comparison: Diversity Across Error Types', fontsize=14, fontweight='bold')
        ax.set_ylim(0, max(means) * 1.2)

        # Add value labels on bars
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{mean:.4f}',
                   ha='center', va='bottom', fontsize=11)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved gate comparison to {output_path}")

    def plot_diversity_distributions(
        self,
        nq_scores: List[float],
        tqa_scores: List[float],
        output_path: str
    ):
        """Generate box plots for diversity distributions."""
        fig, ax = plt.subplots(figsize=(8, 6))

        data = [nq_scores, tqa_scores]
        labels = ['NaturalQuestions\n(Knowledge Gaps)', 'TruthfulQA\n(Misconceptions)']

        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        # Color boxes
        colors = ['#2E86AB', '#A23B72']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Semantic Diversity', fontsize=12)
        ax.set_title('Diversity Distribution Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved diversity distribution to {output_path}")

    def plot_agreement_distributions(
        self,
        nq_scores: List[float],
        tqa_scores: List[float],
        output_path: str
    ):
        """Generate box plots for agreement distributions."""
        fig, ax = plt.subplots(figsize=(8, 6))

        data = [nq_scores, tqa_scores]
        labels = ['NaturalQuestions\n(Knowledge Gaps)', 'TruthfulQA\n(Misconceptions)']

        bp = ax.boxplot(data, labels=labels, patch_artist=True)

        # Color boxes
        colors = ['#2E86AB', '#A23B72']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Sampling Agreement', fontsize=12)
        ax.set_title('Agreement Distribution Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved agreement distribution to {output_path}")

    def plot_signature_space(
        self,
        nq_diversity: List[float],
        nq_agreement: List[float],
        tqa_diversity: List[float],
        tqa_agreement: List[float],
        output_path: str
    ):
        """
        Generate 2D signature space scatter plot.

        Args:
            nq_diversity: [100] NQ diversity scores
            nq_agreement: [100] NQ agreement scores
            tqa_diversity: [100] TQA diversity scores
            tqa_agreement: [100] TQA agreement scores
            output_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Scatter plots
        ax.scatter(nq_diversity, nq_agreement,
                  label='NaturalQuestions (Knowledge Gaps)',
                  alpha=0.6, s=50, color='#2E86AB')
        ax.scatter(tqa_diversity, tqa_agreement,
                  label='TruthfulQA (Misconceptions)',
                  alpha=0.6, s=50, color='#A23B72')

        ax.set_xlabel('Semantic Diversity', fontsize=12)
        ax.set_ylabel('Sampling Agreement', fontsize=12)
        ax.set_title('Error Type Signature Space (2D)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300)
        plt.close()
        print(f"Saved signature space to {output_path}")
