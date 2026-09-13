"""
Cross-Validation Trainer: Leave-5-out CV with fold-wise metrics
"""

from sklearn.model_selection import KFold
import numpy as np
from typing import Dict, Any


class CrossValidationTrainer:
    """Leave-K-out cross-validation trainer."""
    
    def __init__(self, n_splits: int = 13, random_state: int = 42):
        """
        Initialize CV trainer.
        
        Args:
            n_splits: Number of folds (default 13 for 63 samples = ~5 per fold)
            random_state: Random seed
        """
        self.n_splits = n_splits
        self.kfold = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    
    def run_cv(
        self,
        model_class,
        model_params: Dict,
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, Any]:
        """
        Run cross-validation.
        
        Args:
            model_class: Model class to instantiate
            model_params: Model initialization parameters
            X: Feature matrix (N, F)
            y: Target labels (N,)
        
        Returns:
            cv_results: Dict with keys:
                - train_scores: List of train accuracies per fold
                - test_scores: List of test accuracies per fold
                - predictions: Array of predictions for each sample (N,)
                - train_indices: List of train index arrays per fold
                - test_indices: List of test index arrays per fold
        """
        train_scores = []
        test_scores = []
        predictions = np.full(len(y), -1, dtype=int)
        train_indices_all = []
        test_indices_all = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(self.kfold.split(X)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Initialize and train model
            model = model_class(**model_params)
            model.fit(X_train, y_train)
            
            # Calculate train/test accuracy
            train_acc = model.score(X_train, y_train)
            test_acc = model.score(X_test, y_test)
            
            # Store predictions
            y_pred = model.predict(X_test)
            predictions[test_idx] = y_pred
            
            train_scores.append(train_acc)
            test_scores.append(test_acc)
            train_indices_all.append(train_idx)
            test_indices_all.append(test_idx)
        
        return {
            "train_scores": train_scores,
            "test_scores": test_scores,
            "predictions": predictions,
            "train_indices": train_indices_all,
            "test_indices": test_indices_all
        }
