"""Visualizer: Generate comparison plots for h-m2
Extended from h-m1 with within-family validation visualization
"""

import matplotlib.pyplot as plt
import numpy as np
import os
from typing import List


class Visualizer:
    """Generate visualization figures for h-m2 experiment."""

    def __init__(self, output_dir: str = "./outputs/figures"):
        """Initialize visualizer with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_accuracy_comparison(self, h_e1_accuracy: float, h_m1_accuracy: float,
                                 h_m2_accuracy: float = None,
                                 random_baseline: float = 0.5,
                                 random_test_accuracy: float = None) -> None:
        """Generate mandatory accuracy comparison bar chart.

        Args:
            h_e1_accuracy: H-E1 test accuracy (all weight stats)
            h_m1_accuracy: H-M1 test accuracy (gradient-flow features)
            h_m2_accuracy: H-M2 test accuracy (architectural features)
            random_baseline: Theoretical random baseline (0.5)
            random_test_accuracy: Random model test accuracy (optional)
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        if h_m2_accuracy is not None and random_test_accuracy is not None:
            methods = ["H-E1\n(Weight Stats)", "H-M1\n(Gradient Flow)",
                      "H-M2\n(Architecture)", "Random\nBaseline", "Random Models\n(Untrained)"]
            accuracies = [h_e1_accuracy, h_m1_accuracy, h_m2_accuracy, random_baseline, random_test_accuracy]
            colors = ["green", "blue", "purple", "gray", "lightcoral"]
        elif h_m2_accuracy is not None:
            methods = ["H-E1\n(Weight Stats)", "H-M1\n(Gradient Flow)",
                      "H-M2\n(Architecture)", "Random\nBaseline"]
            accuracies = [h_e1_accuracy, h_m1_accuracy, h_m2_accuracy, random_baseline]
            colors = ["green", "blue", "purple", "gray"]
        else:
            methods = ["H-E1\n(Weight Stats)", "H-M1\n(Gradient Flow)", "Random\nBaseline"]
            accuracies = [h_e1_accuracy, h_m1_accuracy, random_baseline]
            colors = ["green", "blue", "gray"]

        bars = ax.bar(methods, accuracies, color=colors, alpha=0.7, edgecolor='black')

        # Add accuracy labels on bars
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                   f"{acc:.1%}", ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel("Test Accuracy", fontsize=12)
        ax.set_title("H-M2: Architectural Constraints Mechanism Validation", fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.15)
        ax.axhline(y=0.5, color='red', linestyle='--', linewidth=1.5, label='SHOULD_WORK Gate (50%)')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/accuracy_comparison.png", dpi=150, bbox_inches='tight')
        plt.close()

    def plot_within_family_comparison(self, family_results: dict,
                                      all_families_accuracy: float) -> None:
        """Generate within-family vs all-families bar chart (NEW for H-M2).

        Args:
            family_results: {'resnet': {accuracy, ...}, 'vgg': {...}, 'densenet': {...}}
            all_families_accuracy: Overall test accuracy
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        families = list(family_results.keys()) + ['All Families']
        accuracies = [family_results[f]['accuracy'] for f in family_results.keys()] + [all_families_accuracy]
        colors = ['steelblue', 'coral', 'lightgreen', 'gray'][:len(families)]

        bars = ax.bar(families, accuracies, color=colors, alpha=0.7, edgecolor='black')

        # Add accuracy labels
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                   f"{acc:.1%}", ha='center', va='bottom', fontsize=12, fontweight='bold')

        ax.set_ylabel("Test Accuracy", fontsize=12)
        ax.set_title("H-M2: Within-Family Depth Classification", fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.15)
        ax.axhline(y=0.65, color='orange', linestyle='--', linewidth=1.5, label='Within-Family Target (65%)')
        ax.axhline(y=0.5, color='red', linestyle=':', linewidth=1.5, label='Random Baseline (50%)')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/within_family_comparison.png", dpi=150, bbox_inches='tight')
        plt.close()

    def plot_feature_importance(self, coefficients: np.ndarray,
                                feature_names: List[str]) -> None:
        """Plot feature importance from logistic regression coefficients.

        Args:
            coefficients: Logistic regression coefficients [8,]
            feature_names: Names of 8 architectural features
        """
        fig, ax = plt.subplots(figsize=(10, 7))

        # Sort by absolute magnitude
        sorted_indices = np.argsort(np.abs(coefficients))[::-1]
        sorted_coef = coefficients[sorted_indices]
        sorted_names = [feature_names[i] for i in sorted_indices]

        colors = ['darkgreen' if c > 0 else 'darkred' for c in sorted_coef]
        bars = ax.barh(sorted_names, sorted_coef, color=colors, alpha=0.7, edgecolor='black')

        ax.set_xlabel("Coefficient Magnitude", fontsize=12)
        ax.set_title("H-M2: Feature Importance (Architectural Features)", fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linewidth=1)
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, sorted_coef)):
            ax.text(val + 0.05 if val > 0 else val - 0.05, i,
                   f"{val:.2f}", va='center', ha='left' if val > 0 else 'right', fontsize=10)

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/feature_importance.png", dpi=150, bbox_inches='tight')
        plt.close()

    def plot_confusion_matrix(self, cm: np.ndarray, class_names: List[str]) -> None:
        """Plot confusion matrix.

        Args:
            cm: Confusion matrix [2, 2]
            class_names: Class labels ['shallow', 'deep']
        """
        fig, ax = plt.subplots(figsize=(6, 5))

        im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.figure.colorbar(im, ax=ax)

        ax.set(xticks=np.arange(cm.shape[1]),
               yticks=np.arange(cm.shape[0]),
               xticklabels=class_names,
               yticklabels=class_names,
               ylabel='True Label',
               xlabel='Predicted Label',
               title='H-M2: Confusion Matrix')

        # Add text annotations
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, format(cm[i, j], 'd'),
                       ha="center", va="center",
                       color="white" if cm[i, j] > thresh else "black",
                       fontsize=14, fontweight='bold')

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/confusion_matrix.png", dpi=150, bbox_inches='tight')
        plt.close()

    def plot_feature_distributions(self, X_shallow: np.ndarray, X_deep: np.ndarray,
                                   feature_names: List[str]) -> None:
        """Plot feature distributions for shallow vs deep models.

        Args:
            X_shallow: Features from shallow models [N_shallow, 8]
            X_deep: Features from deep models [N_deep, 8]
            feature_names: Names of 8 architectural features
        """
        n_features = X_shallow.shape[1]
        n_rows = (n_features + 2) // 3
        fig, axes = plt.subplots(n_rows, 3, figsize=(15, n_rows * 4))
        axes = axes.flatten()

        for i in range(n_features):
            ax = axes[i]

            # Box plots
            data = [X_shallow[:, i], X_deep[:, i]]
            bp = ax.boxplot(data, labels=['Shallow', 'Deep'], patch_artist=True)

            # Color boxes
            bp['boxes'][0].set_facecolor('lightblue')
            bp['boxes'][1].set_facecolor('lightcoral')

            ax.set_title(feature_names[i], fontsize=11, fontweight='bold')
            ax.set_ylabel('Feature Value', fontsize=10)
            ax.grid(axis='y', alpha=0.3)

        # Hide unused subplots
        for i in range(n_features, len(axes)):
            axes[i].axis('off')

        plt.suptitle('H-M2: Architectural Feature Distributions (Shallow vs Deep)',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/feature_distributions.png", dpi=150, bbox_inches='tight')
        plt.close()

    def plot_train_test_comparison(self, train_accuracy: float, test_accuracy: float) -> None:
        """Plot train vs test accuracy comparison.

        Args:
            train_accuracy: Training set accuracy
            test_accuracy: Test set accuracy
        """
        fig, ax = plt.subplots(figsize=(7, 5))

        splits = ['Train', 'Test']
        accuracies = [train_accuracy, test_accuracy]
        colors = ['steelblue', 'coral']

        bars = ax.bar(splits, accuracies, color=colors, alpha=0.7, edgecolor='black')

        # Add accuracy labels
        for bar, acc in zip(bars, accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                   f"{acc:.1%}", ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel("Accuracy", fontsize=12)
        ax.set_title("H-M2: Train vs Test Performance", fontsize=14, fontweight='bold')
        ax.set_ylim(0, 1.15)
        ax.axhline(y=0.5, color='red', linestyle='--', linewidth=1.5, label='Random Baseline')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/train_test_comparison.png", dpi=150, bbox_inches='tight')
        plt.close()

    def plot_gate_metrics(self, baseline: float, actual: float,
                         target: float, passed: bool) -> None:
        """Plot gate condition metrics.

        Args:
            baseline: Random baseline (0.5)
            actual: Actual test accuracy
            target: Gate threshold (0.5 for h-m2)
            passed: Whether gate passed
        """
        fig, ax = plt.subplots(figsize=(8, 5))

        categories = ['Baseline\n(Random)', 'Target\n(Gate)', 'Actual\n(H-M2)']
        values = [baseline, target, actual]
        colors = ['gray', 'orange', 'green' if passed else 'red']

        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.02,
                   f"{val:.1%}", ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel("Test Accuracy", fontsize=12)
        ax.set_title(f"H-M2: Gate Condition - {'PASS ✓' if passed else 'FAIL ✗'}",
                    fontsize=14, fontweight='bold', color='green' if passed else 'red')
        ax.set_ylim(0, 1.15)
        ax.axhline(y=target, color='orange', linestyle='--', linewidth=1.5, label=f'Gate Threshold ({target:.0%})')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/gate_metrics.png", dpi=150, bbox_inches='tight')
        plt.close()
