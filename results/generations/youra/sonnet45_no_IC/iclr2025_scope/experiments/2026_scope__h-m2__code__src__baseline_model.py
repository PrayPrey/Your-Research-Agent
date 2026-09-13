"""
Baseline Model: Majority class predictor for comparison
"""

from sklearn.dummy import DummyClassifier
import numpy as np


class BaselineModel:
    """Wrapper for DummyClassifier with consistent interface."""
    
    def __init__(self, strategy: str = "most_frequent"):
        """
        Initialize baseline model.
        
        Args:
            strategy: "most_frequent" or "stratified"
        """
        self.model = DummyClassifier(strategy=strategy, random_state=42)
        self.is_fitted = False
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """Train baseline model."""
        self.model.fit(X, y)
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        return self.model.predict(X)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Calculate accuracy."""
        if not self.is_fitted:
            raise RuntimeError("Model not fitted yet")
        return self.model.score(X, y)
