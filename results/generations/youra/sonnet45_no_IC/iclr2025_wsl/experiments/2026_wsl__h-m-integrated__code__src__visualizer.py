"""
Visualization Module
Generate required and recommended visualizations
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List


class Visualizer:
    """Generate visualizations for experiment report"""

    def __init__(self, output_dir: str, dpi: int = 300):
        self.output_dir = output_dir
        self.dpi = dpi
        os.makedirs(output_dir, exist_ok=True)

        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.dpi'] = dpi

    def plot_gate_comparison(
        self,
        target: float,
        baseline: float,
        proposed: float
    ) -> str:
        """
        REQUIRED: Bar chart showing target vs baseline vs proposed accuracy.
        Returns: filepath to saved PNG
        """
        fig, ax = plt.subplots(figsize=(8, 6))

        # Data
        labels = ['Target\n(Gate)', 'Norms-only\nBaseline', 'Norms+Spectral\nProposed']
        values = [target, baseline, proposed]

        # Colors: green if >= target, yellow if >= 0.70, red otherwise
        colors = []
        for val in values:
            if val >= target:
                colors.append('#2ecc71')  # Green
            elif val >= 0.70:
                colors.append('#f39c12')  # Yellow
            else:
                colors.append('#e74c3c')  # Red

        # Plot bars
        bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black')

        # Add value labels on bars
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{val:.2%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Add horizontal line at target
        ax.axhline(y=target, color='red', linestyle='--', linewidth=2, label=f'Target ({target:.0%})')

        # Labels and title
        ax.set_ylabel('Test Accuracy', fontsize=12, fontweight='bold')
        ax.set_title('H-E1 Gate Comparison: Binary Classification Accuracy', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.legend(fontsize=10)

        # Save
        filepath = os.path.join(self.output_dir, 'gate_comparison.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Gate comparison plot saved to {filepath}")
        return filepath

    def plot_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        labels: List[str]
    ) -> str:
        """
        Confusion matrix heatmap.
        Returns: filepath
        """
        from sklearn.metrics import confusion_matrix

        cm = confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels, ax=ax)

        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix: ResNet vs ViT Classification', fontsize=14, fontweight='bold')

        filepath = os.path.join(self.output_dir, 'confusion_matrix.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Confusion matrix saved to {filepath}")
        return filepath

    def plot_feature_importance(
        self,
        coefficients: np.ndarray,
        top_k: int = 10
    ) -> str:
        """
        Bar chart of top-K feature coefficients.
        Returns: filepath
        """
        # Get top K by absolute value
        abs_coef = np.abs(coefficients)
        top_indices = np.argsort(abs_coef)[-top_k:][::-1]
        top_coefs = coefficients[top_indices]

        # Generate feature names
        feature_names = [f"Feature {i}" for i in top_indices]

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#e74c3c' if c < 0 else '#2ecc71' for c in top_coefs]

        bars = ax.barh(feature_names, top_coefs, color=colors, alpha=0.8, edgecolor='black')

        ax.set_xlabel('Coefficient Value', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_k} Feature Importances (Logistic Regression)', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)

        filepath = os.path.join(self.output_dir, 'feature_importance.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Feature importance plot saved to {filepath}")
        return filepath

    def plot_permutation_distribution(
        self,
        permuted_acc: List[float],
        actual_acc: float
    ) -> str:
        """
        Histogram with actual accuracy marked.
        Returns: filepath
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot histogram
        ax.hist(permuted_acc, bins=50, color='#3498db', alpha=0.7, edgecolor='black', label='Permuted Accuracies')

        # Mark actual accuracy
        ax.axvline(x=actual_acc, color='red', linestyle='--', linewidth=3, label=f'Actual Accuracy ({actual_acc:.2%})')

        # Labels and title
        ax.set_xlabel('Accuracy', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Permutation Test Distribution (1000 iterations)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)

        filepath = os.path.join(self.output_dir, 'permutation_dist.png')
        plt.tight_layout()
        plt.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        print(f"✓ Permutation distribution plot saved to {filepath}")
        return filepath
