"""
Metrics Calculator: CV accuracy, generalization gap, per-domain metrics
"""

import numpy as np
from typing import Dict, List
from sklearn.metrics import confusion_matrix


class MetricsCalculator:
    """Calculate evaluation metrics for meta-classifier."""
    
    @staticmethod
    def compute_cv_accuracy(cv_results: Dict) -> float:
        """Compute mean test accuracy across folds."""
        return float(np.mean(cv_results["test_scores"]))
    
    @staticmethod
    def compute_generalization_gap(cv_results: Dict) -> float:
        """Compute mean (train_acc - test_acc) across folds."""
        train_scores = np.array(cv_results["train_scores"])
        test_scores = np.array(cv_results["test_scores"])
        gaps = train_scores - test_scores
        return float(np.mean(gaps))
    
    @staticmethod
    def compute_baseline_delta(
        cv_accuracy: float,
        baseline_accuracy: float
    ) -> float:
        """Compute improvement over baseline."""
        return cv_accuracy - baseline_accuracy
    
    @staticmethod
    def compute_per_domain_accuracy(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        benchmark_domains: List[str]
    ) -> Dict[str, float]:
        """
        Compute accuracy per domain.
        
        Args:
            y_true: True labels (N,)
            y_pred: Predicted labels (N,)
            benchmark_domains: List of domain names (N,)
        
        Returns:
            domain_accuracies: {domain: accuracy}
        """
        unique_domains = set(benchmark_domains)
        domain_accuracies = {}
        
        for domain in unique_domains:
            domain_mask = np.array([d == domain for d in benchmark_domains])
            if domain_mask.sum() > 0:
                domain_acc = (y_true[domain_mask] == y_pred[domain_mask]).mean()
                domain_accuracies[domain] = float(domain_acc)
        
        return domain_accuracies
    
    @staticmethod
    def generate_confusion_matrix(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        class_names: List[str]
    ) -> np.ndarray:
        """
        Generate confusion matrix.
        
        Args:
            y_true: True labels (N,)
            y_pred: Predicted labels (N,)
            class_names: List of class names
        
        Returns:
            cm: Confusion matrix (C, C)
        """
        return confusion_matrix(y_true, y_pred, labels=range(len(class_names)))
