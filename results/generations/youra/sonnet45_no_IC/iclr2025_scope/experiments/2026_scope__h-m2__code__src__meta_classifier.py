"""
Meta-Classifier: Random Forest with small-data hyperparameters
"""

from sklearn.ensemble import RandomForestClassifier
import numpy as np
from typing import List


class MetaClassifier:
    """Random Forest meta-classifier with small-data configuration."""
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 10,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42
    ):
        """
        Initialize meta-classifier.
        
        Args:
            n_estimators: Number of trees
            max_depth: Maximum tree depth
            min_samples_split: Min samples to split node
            min_samples_leaf: Min samples in leaf
            random_state: Random seed
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=-1
        )
        self.is_fitted = False
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """Train meta-classifier."""
        self.model.fit(X, y)
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict method families."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        return self.model.predict_proba(X)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate accuracy."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        return self.model.score(X, y)
    
    def get_feature_importances(self) -> np.ndarray:
        """Get feature importance scores."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        return self.model.feature_importances_
