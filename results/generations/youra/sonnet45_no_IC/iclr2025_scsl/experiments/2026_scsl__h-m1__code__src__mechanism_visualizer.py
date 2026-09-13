"""Mechanism visualizer for H-M1 - generate 5 required figures."""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from typing import Dict
import numpy as np
from pathlib import Path


class MechanismVisualizer:
    def __init__(self, output_dir: str, dpi: int = 300):
        """Initialize visualizer with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        plt.style.use('seaborn-v0_8')

    def plot_coefficients(
        self,
        coefficients: Dict[str, float],
        expected_signs: Dict[str, str],
        save_path: str
    ) -> None:
        """Generate coefficient bar chart.

        Args:
            coefficients: Feature -> coefficient value
            expected_signs: Feature -> 'positive' or 'negative'
            save_path: Output file path
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        features = list(coefficients.keys())
        values = list(coefficients.values())
        colors = ['red' if expected_signs.get(f) == 'negative' else 'green' for f in features]

        ax.bar(features, values, color=colors, alpha=0.7)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.set_xlabel('Features')
        ax.set_ylabel('Coefficient Value')
        ax.set_title('LR Coefficients with Sign Verification')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        full_path = self.output_dir / save_path
        plt.savefig(full_path, dpi=self.dpi)
        plt.close()
        print(f"✓ Saved: {full_path}")

    def plot_performance_comparison(
        self,
        lr_metrics: Dict[str, float],
        gb_metrics: Dict[str, float],
        save_path: str
    ) -> None:
        """Side-by-side bar chart: LR vs GB accuracy/F1."""
        fig, ax = plt.subplots(figsize=(8, 6))

        metrics = ['Accuracy', 'F1']
        lr_values = [lr_metrics['lr_accuracy'], lr_metrics['lr_f1']]
        gb_values = [gb_metrics['gb_accuracy'], gb_metrics['gb_f1']]

        x = np.arange(len(metrics))
        width = 0.35

        ax.bar(x - width/2, lr_values, width, label='LR', color='blue', alpha=0.7)
        ax.bar(x + width/2, gb_values, width, label='GB', color='orange', alpha=0.7)

        ax.set_xlabel('Metrics')
        ax.set_ylabel('Score')
        ax.set_title(f'LR vs GB Performance (Gap: {lr_metrics["gap"]:.3f})')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.set_ylim([0, 1.1])
        plt.tight_layout()

        full_path = self.output_dir / save_path
        plt.savefig(full_path, dpi=self.dpi)
        plt.close()
        print(f"✓ Saved: {full_path}")

    def plot_decision_boundary_pca(
        self,
        X_2d: np.ndarray,
        y: np.ndarray,
        Z: np.ndarray,
        xx: np.ndarray,
        yy: np.ndarray,
        pca_variance: tuple,
        save_path: str
    ) -> None:
        """2D PCA scatter with decision boundary contour.

        Args:
            X_2d: Projected features [N, 2]
            y: Labels [N]
            Z: Decision boundary mesh [100, 100]
            xx, yy: Mesh grid coordinates [100, 100]
            pca_variance: (var_pc1, var_pc2) explained variance ratios
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # Decision boundary
        ax.contourf(xx, yy, Z, alpha=0.3, cmap='viridis')

        # Scatter plot
        scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=y, cmap='viridis', edgecolors='k', s=50)

        ax.set_xlabel(f'PC1 ({pca_variance[0]:.1%} variance)')
        ax.set_ylabel(f'PC2 ({pca_variance[1]:.1%} variance)')
        ax.set_title('Decision Boundary in PCA Space')
        plt.colorbar(scatter, ax=ax, label='Class')
        plt.tight_layout()

        full_path = self.output_dir / save_path
        plt.savefig(full_path, dpi=self.dpi)
        plt.close()
        print(f"✓ Saved: {full_path}")

    def plot_feature_importance_comparison(
        self,
        lr_importance: Dict[str, float],
        gb_importance: Dict[str, float],
        feature_names: list,
        save_path: str
    ) -> None:
        """Side-by-side feature importance bars."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort by LR importance
        sorted_features = sorted(lr_importance, key=lr_importance.get, reverse=True)
        lr_values = [lr_importance[f] for f in sorted_features]
        gb_values = [gb_importance[f] for f in sorted_features]

        x = np.arange(len(sorted_features))
        width = 0.35

        ax.bar(x - width/2, lr_values, width, label='LR (Coef Magnitude)', color='blue', alpha=0.7)
        ax.bar(x + width/2, gb_values, width, label='GB (Feature Importance)', color='orange', alpha=0.7)

        ax.set_xlabel('Features (sorted by LR importance)')
        ax.set_ylabel('Importance Score')
        ax.set_title('Feature Importance Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(sorted_features, rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()

        full_path = self.output_dir / save_path
        plt.savefig(full_path, dpi=self.dpi)
        plt.close()
        print(f"✓ Saved: {full_path}")

    def plot_confusion_matrices(
        self,
        y_test: np.ndarray,
        lr_pred: np.ndarray,
        gb_pred: np.ndarray,
        save_path: str
    ) -> None:
        """Two heatmaps: LR confusion matrix (left), GB (right)."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # LR confusion matrix
        lr_cm = confusion_matrix(y_test, lr_pred)
        sns.heatmap(lr_cm, annot=True, fmt='d', cmap='Blues', ax=ax1)
        ax1.set_title('LR Confusion Matrix')
        ax1.set_xlabel('Predicted')
        ax1.set_ylabel('Actual')

        # GB confusion matrix
        gb_cm = confusion_matrix(y_test, gb_pred)
        sns.heatmap(gb_cm, annot=True, fmt='d', cmap='Oranges', ax=ax2)
        ax2.set_title('GB Confusion Matrix')
        ax2.set_xlabel('Predicted')
        ax2.set_ylabel('Actual')

        plt.tight_layout()

        full_path = self.output_dir / save_path
        plt.savefig(full_path, dpi=self.dpi)
        plt.close()
        print(f"✓ Saved: {full_path}")
