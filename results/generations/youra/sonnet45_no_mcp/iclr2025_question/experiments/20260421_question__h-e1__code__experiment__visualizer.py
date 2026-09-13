"""Visualization for experiment results."""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve
from typing import Dict, List
import os


class Visualizer:
    """Generate visualizations for experiment results."""

    def __init__(self, output_dir: str = "./figures"):
        """
        Initialize visualizer.

        Args:
            output_dir: Directory to save figures
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_auroc_comparison(self, results: Dict[str, float]) -> None:
        """
        Bar chart: AUROC_semantic vs AUROC_ensemble with gate threshold.

        Args:
            results: Dictionary with auroc_semantic, auroc_ensemble
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        methods = ['Semantic Entropy', 'Ensemble Baseline']
        aurocs = [results['auroc_semantic'], results['auroc_ensemble']]

        bars = ax.bar(methods, aurocs, color=['#2ecc71', '#3498db'])

        # Add gate threshold lines
        ax.axhline(y=0.70, color='r', linestyle='--', label='Min AUROC (0.70)', linewidth=2)

        # Add difference annotation
        diff = results['difference']
        ax.text(0.5, max(aurocs) + 0.05, f'Δ = {diff:.4f}',
                ha='center', fontsize=12, fontweight='bold')

        ax.set_ylabel('AUROC', fontsize=12)
        ax.set_title('Uncertainty Method Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim([0, 1.0])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, auroc in zip(bars, aurocs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{auroc:.4f}',
                   ha='center', va='bottom', fontsize=11)

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, 'auroc_comparison.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()

    def plot_roc_curves(
        self,
        y_true: List[int],
        semantic_scores: List[float],
        ensemble_scores: List[float]
    ) -> None:
        """
        ROC curves for both methods.

        Args:
            y_true: True labels
            semantic_scores: Semantic entropy scores
            ensemble_scores: Ensemble baseline scores
        """
        fig, ax = plt.subplots(figsize=(8, 8))

        # Compute ROC curves
        fpr_sem, tpr_sem, _ = roc_curve(y_true, semantic_scores)
        fpr_ens, tpr_ens, _ = roc_curve(y_true, ensemble_scores)

        # Plot curves
        ax.plot(fpr_sem, tpr_sem, label='Semantic Entropy', linewidth=2, color='#2ecc71')
        ax.plot(fpr_ens, tpr_ens, label='Ensemble Baseline', linewidth=2, color='#3498db')
        ax.plot([0, 1], [0, 1], 'k--', label='Random', linewidth=1)

        ax.set_xlabel('False Positive Rate', fontsize=12)
        ax.set_ylabel('True Positive Rate', fontsize=12)
        ax.set_title('ROC Curves', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(alpha=0.3)

        plt.tight_layout()
        save_path = os.path.join(self.output_dir, 'roc_curves.png')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
        plt.close()
