"""DepthClassifier: Binary depth classifier with feature normalization"""

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


class DepthClassifier:
    """Binary depth classifier with feature normalization."""

    def __init__(self, random_state: int = 42):
        """Initialize classifier and scaler."""
        self.scaler = StandardScaler()
        self.classifier = LogisticRegression(
            C=1.0,
            solver='lbfgs',
            max_iter=1000,
            random_state=random_state
        )
        self.is_trained = False

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train classifier. X_train: [N, 4], y_train: [N,]"""
        # Fit scaler on training data only
        X_scaled = self.scaler.fit_transform(X_train)

        # Train classifier
        self.classifier.fit(X_scaled, y_train)
        self.is_trained = True

    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Predict labels. X_test: [M, 4] -> [M,]"""
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before prediction")

        # Transform using training scaler
        X_scaled = self.scaler.transform(X_test)
        return self.classifier.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities. X: [N, 4] -> [N, 2]"""
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained before prediction")

        X_scaled = self.scaler.transform(X)
        return self.classifier.predict_proba(X_scaled)

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute accuracy. Returns: float in [0, 1]"""
        predictions = self.predict(X)
        accuracy = np.mean(predictions == y)
        return accuracy

    def get_coefficients(self) -> np.ndarray:
        """Get logistic regression coefficients for feature importance."""
        if not self.is_trained:
            raise RuntimeError("Classifier must be trained first")
        return self.classifier.coef_[0]
