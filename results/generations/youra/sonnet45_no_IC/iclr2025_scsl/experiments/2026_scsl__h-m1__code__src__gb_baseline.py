"""Gradient Boosting baseline for H-M1 - comparison model."""

from sklearn.ensemble import GradientBoostingClassifier
import numpy as np


class GradientBoostingBaseline:
    def __init__(
        self,
        n_estimators: int = 50,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        """Initialize GB classifier with standard hyperparameters."""
        self.model = GradientBoostingClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state
        )

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train GB model.

        Args:
            X_train: Training features [N, 8] (pre-scaled)
            y_train: Training labels [N]

        Returns:
            Training info dict with convergence status
        """
        self.model.fit(X_train, y_train)

        return {
            'converged': True,
            'n_estimators_used': self.model.n_estimators,
            'train_score': self.model.score(X_train, y_train)
        }

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels. X: [N, 8] -> predictions: [N]"""
        return self.model.predict(X)

    def get_feature_importance(self) -> np.ndarray:
        """Extract feature importance scores.

        Returns:
            Feature importance array [8] from model.feature_importances_
        """
        return self.model.feature_importances_
