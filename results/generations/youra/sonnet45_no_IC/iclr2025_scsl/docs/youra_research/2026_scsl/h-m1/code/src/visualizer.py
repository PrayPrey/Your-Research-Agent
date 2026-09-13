"""Visualization Module for Repository Maintenance Classification."""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc
from pathlib import Path


class ResultVisualizer:
    """Generates visualizations for experiment results."""

    def __init__(self, output_dir: str, dpi: int = 300, format: str = 'png'):
        """Initialize visualizer with output configuration.

        Args:
            output_dir: Directory to save figures
            dpi: Resolution for saved figures
            format: File format (png, pdf, svg)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        self.format = format

        # Set style
        sns.set_style('whitegrid')
        plt.rcParams['figure.dpi'] = dpi
        plt.rcParams['savefig.dpi'] = dpi

    def plot_gate_metrics(self, metrics: dict, targets: dict, save_name: str = 'gate_metrics') -> None:
        """Plot gate metrics comparison (actual vs target).

        Args:
            metrics: Dict with actual metric values
            targets: Dict with target thresholds
            save_name: Filename for saved figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        metrics_to_plot = ['accuracy', 'f1']
        labels = ['Accuracy', 'F1 Score']
        actual_values = [metrics.get('accuracy', 0), metrics.get('f1', 0)]
        target_values = [targets.get('accuracy', 0.75), targets.get('f1', 0.73)]

        x = np.arange(len(labels))
        width = 0.35

        bars1 = ax.bar(x - width/2, target_values, width, label='Target', color='lightblue', alpha=0.7)
        bars2 = ax.bar(x + width/2, actual_values, width, label='Actual', color='steelblue')

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=10)

        ax.set_xlabel('Metric', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Gate Metrics: Target vs Actual', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend(fontsize=10)
        ax.set_ylim([0, 1.0])
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / f'{save_name}.{self.format}'
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, save_name: str = 'confusion_matrix') -> None:
        """Plot confusion matrix heatmap.

        Args:
            y_true: Ground truth labels
            y_pred: Predicted labels
            save_name: Filename for saved figure
        """
        cm = confusion_matrix(y_true, y_pred)

        fig, ax = plt.subplots(figsize=(8, 6))

        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True,
                   xticklabels=['Abandoned', 'Maintained'],
                   yticklabels=['Abandoned', 'Maintained'],
                   ax=ax)

        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')

        plt.tight_layout()
        save_path = self.output_dir / f'{save_name}.{self.format}'
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

    def plot_feature_importance(self, coefficients: np.ndarray, feature_names: list, save_name: str = 'feature_importance') -> None:
        """Plot feature importance based on logistic regression coefficients.

        Args:
            coefficients: Model coefficients
            feature_names: List of feature names
            save_name: Filename for saved figure
        """
        # Sort by absolute value
        abs_coef = np.abs(coefficients)
        sorted_idx = np.argsort(abs_coef)[::-1]

        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['green' if c > 0 else 'red' for c in coefficients[sorted_idx]]

        bars = ax.barh(range(len(sorted_idx)), abs_coef[sorted_idx], color=colors, alpha=0.7)
        ax.set_yticks(range(len(sorted_idx)))
        ax.set_yticklabels([feature_names[i] for i in sorted_idx])
        ax.set_xlabel('Absolute Coefficient Value', fontsize=12)
        ax.set_title('Feature Importance (LR Coefficients)', fontsize=14, fontweight='bold')
        ax.invert_yaxis()

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='green', alpha=0.7, label='Positive'),
                          Patch(facecolor='red', alpha=0.7, label='Negative')]
        ax.legend(handles=legend_elements, loc='lower right')

        plt.tight_layout()
        save_path = self.output_dir / f'{save_name}.{self.format}'
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

    def plot_roc_curve(self, y_true: np.ndarray, y_proba: np.ndarray, save_name: str = 'roc_curve') -> None:
        """Plot ROC curve with AUC score.

        Args:
            y_true: Ground truth labels
            y_proba: Predicted probabilities (for positive class)
            save_name: Filename for saved figure
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        roc_auc = auc(fpr, tpr)

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random classifier')

        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate', fontsize=12)
        ax.set_ylabel('True Positive Rate', fontsize=12)
        ax.set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=14, fontweight='bold')
        ax.legend(loc='lower right', fontsize=10)
        ax.grid(alpha=0.3)

        plt.tight_layout()
        save_path = self.output_dir / f'{save_name}.{self.format}'
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

    def plot_class_distribution(self, y_train: np.ndarray, y_test: np.ndarray, save_name: str = 'class_distribution') -> None:
        """Plot class distribution in train and test sets.

        Args:
            y_train: Training labels
            y_test: Test labels
            save_name: Filename for saved figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Train set
        train_counts = np.bincount(y_train)
        ax1.bar(['Abandoned', 'Maintained'], train_counts, color=['coral', 'skyblue'], alpha=0.7)
        ax1.set_ylabel('Count', fontsize=12)
        ax1.set_title(f'Training Set (n={len(y_train)})', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, v in enumerate(train_counts):
            ax1.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

        # Test set
        test_counts = np.bincount(y_test)
        ax2.bar(['Abandoned', 'Maintained'], test_counts, color=['coral', 'skyblue'], alpha=0.7)
        ax2.set_ylabel('Count', fontsize=12)
        ax2.set_title(f'Test Set (n={len(y_test)})', fontsize=12, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # Add value labels
        for i, v in enumerate(test_counts):
            ax2.text(i, v, str(v), ha='center', va='bottom', fontsize=10)

        fig.suptitle('Class Distribution: Maintained vs Abandoned', fontsize=14, fontweight='bold')
        plt.tight_layout()

        save_path = self.output_dir / f'{save_name}.{self.format}'
        plt.savefig(save_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        print(f"Saved: {save_path}")

    def generate_all_figures(self, metrics: dict, targets: dict, y_true: np.ndarray,
                            y_pred: np.ndarray, y_proba: np.ndarray, y_train: np.ndarray,
                            y_test: np.ndarray, coefficients: np.ndarray, feature_names: list) -> None:
        """Generate all 5 required figures.

        Args:
            metrics: Computed metrics dict
            targets: Target thresholds dict
            y_true: Test set ground truth
            y_pred: Test set predictions
            y_proba: Test set probabilities
            y_train: Training set labels
            y_test: Test set labels
            coefficients: Model coefficients
            feature_names: Feature names
        """
        print("\nGenerating visualizations...")
        self.plot_gate_metrics(metrics, targets)
        self.plot_confusion_matrix(y_true, y_pred)
        self.plot_feature_importance(coefficients, feature_names)

        # ROC curve needs probability of positive class
        if y_proba.ndim > 1:
            y_proba_pos = y_proba[:, 1]
        else:
            y_proba_pos = y_proba
        self.plot_roc_curve(y_true, y_proba_pos)

        self.plot_class_distribution(y_train, y_test)
        print("All visualizations generated successfully")
