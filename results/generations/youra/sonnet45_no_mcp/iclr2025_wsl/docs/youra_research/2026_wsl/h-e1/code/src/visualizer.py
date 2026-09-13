"""Visualizer: Generate analysis figures"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List
import os


class Visualizer:
    """Generate 5 analysis figures."""

    def __init__(self, output_dir: str):
        """Initialize with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_gate_metrics(self, baseline: float, actual: float, target: float, passed: bool) -> None:
        """MANDATORY: Gate condition visualization. Saves to figures/gate_metrics.png"""
        fig, ax = plt.subplots(figsize=(10, 6))

        x = ['Baseline', 'Actual', 'Target']
        y = [baseline, actual, target]
        colors = ['gray', 'green' if passed else 'red', 'blue']

        bars = ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black')

        # Add threshold line
        ax.axhline(y=target, color='black', linestyle='--', linewidth=2, label=f'Threshold ({target:.0%})')

        # Add value labels on bars
        for bar, val in zip(bars, y):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel('Accuracy', fontsize=12)
        ax.set_title(f'Gate Condition: {"PASS ✓" if passed else "FAIL ✗"}', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/gate_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_confusion_matrix(self, cm: np.ndarray, class_names: List[str]) -> None:
        """Confusion matrix heatmap. Saves to figures/confusion_matrix.png"""
        fig, ax = plt.subplots(figsize=(8, 6))

        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                   xticklabels=class_names, yticklabels=class_names, ax=ax)

        ax.set_xlabel('Predicted', fontsize=12)
        ax.set_ylabel('True', fontsize=12)
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/confusion_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_feature_distributions(self, features_shallow: np.ndarray, features_deep: np.ndarray) -> None:
        """Box plots for 4 features. Saves to figures/feature_distributions.png"""
        feature_names = ['Mean', 'Std', 'Min', 'Max']

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.flatten()

        for i, (ax, name) in enumerate(zip(axes, feature_names)):
            data = [features_shallow[:, i], features_deep[:, i]]
            bp = ax.boxplot(data, labels=['Shallow', 'Deep'], patch_artist=True)

            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][1].set_facecolor('lightcoral')

            ax.set_ylabel(name, fontsize=12)
            ax.set_title(f'{name} Distribution', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/feature_distributions.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_feature_importance(self, coefficients: np.ndarray, feature_names: List[str]) -> None:
        """Logistic regression coefficients. Saves to figures/feature_importance.png"""
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['green' if c > 0 else 'red' for c in coefficients]
        bars = ax.barh(feature_names, coefficients, color=colors, alpha=0.7, edgecolor='black')

        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
        ax.set_xlabel('Coefficient Value', fontsize=12)
        ax.set_title('Feature Importance (Logistic Regression Coefficients)', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/feature_importance.png', dpi=300, bbox_inches='tight')
        plt.close()

    def plot_train_test_comparison(self, train_acc: float, test_acc: float) -> None:
        """Train vs test accuracy bars. Saves to figures/train_test_comparison.png"""
        fig, ax = plt.subplots(figsize=(8, 6))

        x = ['Train', 'Test']
        y = [train_acc, test_acc]
        colors = ['steelblue', 'coral']

        bars = ax.bar(x, y, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels
        for bar, val in zip(bars, y):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel('Accuracy', fontsize=12)
        ax.set_title('Training vs Test Accuracy', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.0)
        ax.grid(axis='y', alpha=0.3)

        # Add overfitting indicator
        gap = abs(train_acc - test_acc)
        ax.text(0.5, 0.95, f'Gap: {gap:.1%}', transform=ax.transAxes,
               ha='center', va='top', fontsize=10,
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/train_test_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
