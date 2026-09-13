"""
Visualizer: Generate 6 analysis figures
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List
from pathlib import Path


class Visualizer:
    """Generate analysis visualizations."""
    
    def __init__(self, output_dir: str, dpi: int = 300):
        """
        Initialize visualizer.
        
        Args:
            output_dir: Directory to save figures
            dpi: Figure resolution
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        sns.set_style("whitegrid")
    
    def plot_gate_metrics_comparison(
        self,
        cv_accuracy: float,
        generalization_gap: float,
        baseline_accuracy: float,
        gate_result: str
    ):
        """MANDATORY: Plot gate metrics comparison."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # CV Accuracy vs Baseline
        axes[0].bar(["Baseline", "Meta-Classifier"], [baseline_accuracy, cv_accuracy])
        axes[0].axhline(0.35, color='r', linestyle='--', label='PASS threshold')
        axes[0].set_ylabel("Accuracy")
        axes[0].set_title("CV Accuracy vs Baseline")
        axes[0].legend()
        
        # Generalization Gap
        axes[1].bar(["Gap"], [generalization_gap], color='orange')
        axes[1].axhline(0.20, color='r', linestyle='--', label='PASS threshold')
        axes[1].axhline(0.25, color='y', linestyle='--', label='PARTIAL threshold')
        axes[1].set_ylabel("Gap (Train - Test)")
        axes[1].set_title("Generalization Gap")
        axes[1].legend()
        
        # Gate Result
        gate_colors = {"PASS": "green", "PARTIAL": "yellow", "FAIL": "red"}
        axes[2].text(0.5, 0.5, gate_result, fontsize=40, ha='center', va='center',
                     color=gate_colors.get(gate_result, "black"), weight='bold')
        axes[2].set_xlim(0, 1)
        axes[2].set_ylim(0, 1)
        axes[2].axis('off')
        axes[2].set_title("Gate Result")
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "gate_metrics_comparison.png", dpi=self.dpi)
        plt.close()
    
    def plot_learning_curve(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_class,
        model_params: Dict
    ):
        """Plot learning curve with different training sizes."""
        from sklearn.model_selection import learning_curve
        
        train_sizes = np.linspace(0.3, 1.0, 5)
        train_sizes_abs, train_scores, test_scores = learning_curve(
            model_class(**model_params),
            X, y,
            train_sizes=train_sizes,
            cv=5,
            scoring='accuracy',
            n_jobs=-1
        )
        
        plt.figure(figsize=(10, 6))
        plt.plot(train_sizes_abs, train_scores.mean(axis=1), label='Train accuracy', marker='o')
        plt.plot(train_sizes_abs, test_scores.mean(axis=1), label='Test accuracy', marker='s')
        plt.fill_between(train_sizes_abs, 
                         train_scores.mean(axis=1) - train_scores.std(axis=1),
                         train_scores.mean(axis=1) + train_scores.std(axis=1),
                         alpha=0.2)
        plt.fill_between(train_sizes_abs,
                         test_scores.mean(axis=1) - test_scores.std(axis=1),
                         test_scores.mean(axis=1) + test_scores.std(axis=1),
                         alpha=0.2)
        plt.xlabel("Training Set Size")
        plt.ylabel("Accuracy")
        plt.title("Learning Curve")
        plt.legend()
        plt.grid(True)
        plt.savefig(self.output_dir / "learning_curve.png", dpi=self.dpi)
        plt.close()
    
    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        class_names: List[str]
    ):
        """Plot confusion matrix heatmap."""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=class_names, yticklabels=class_names)
        plt.xlabel("Predicted Family")
        plt.ylabel("True Family")
        plt.title("Confusion Matrix")
        plt.tight_layout()
        plt.savefig(self.output_dir / "confusion_matrix.png", dpi=self.dpi)
        plt.close()
    
    def plot_per_domain_accuracy(self, domain_accuracies: Dict[str, float]):
        """Plot accuracy breakdown by domain."""
        domains = list(domain_accuracies.keys())
        accuracies = list(domain_accuracies.values())
        
        plt.figure(figsize=(10, 6))
        plt.bar(domains, accuracies)
        plt.axhline(0.35, color='r', linestyle='--', label='PASS threshold')
        plt.ylabel("Accuracy")
        plt.xlabel("Domain")
        plt.title("Per-Domain Accuracy")
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / "per_domain_accuracy.png", dpi=self.dpi)
        plt.close()
    
    def plot_feature_importance(
        self,
        importances: np.ndarray,
        feature_names: List[str]
    ):
        """Plot feature importance scores."""
        indices = np.argsort(importances)[::-1][:20]  # Top 20
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(indices)), importances[indices])
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.xlabel("Importance")
        plt.title("Feature Importance (Top 20)")
        plt.tight_layout()
        plt.savefig(self.output_dir / "feature_importance.png", dpi=self.dpi)
        plt.close()
    
    def plot_generalization_gap_per_fold(self, cv_results: Dict):
        """Plot train vs test accuracy per fold."""
        train_scores = cv_results["train_scores"]
        test_scores = cv_results["test_scores"]
        folds = list(range(1, len(train_scores) + 1))
        gaps = np.array(train_scores) - np.array(test_scores)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Train vs Test per fold
        axes[0].plot(folds, train_scores, marker='o', label='Train')
        axes[0].plot(folds, test_scores, marker='s', label='Test')
        axes[0].set_xlabel("Fold")
        axes[0].set_ylabel("Accuracy")
        axes[0].set_title("Train vs Test Accuracy per Fold")
        axes[0].legend()
        axes[0].grid(True)
        
        # Gap per fold
        axes[1].bar(folds, gaps, color='orange')
        axes[1].axhline(0.20, color='r', linestyle='--', label='PASS threshold')
        axes[1].set_xlabel("Fold")
        axes[1].set_ylabel("Gap (Train - Test)")
        axes[1].set_title("Generalization Gap per Fold")
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "generalization_gap_per_fold.png", dpi=self.dpi)
        plt.close()
