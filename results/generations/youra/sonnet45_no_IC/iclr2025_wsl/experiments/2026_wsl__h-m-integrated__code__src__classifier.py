"""
Binary Classification Module
Trains and evaluates logistic regression classifier for ResNet vs ViT
"""

import numpy as np
import pickle
from typing import Dict
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report


class BinaryClassifier:
    """Train and evaluate binary classifier"""

    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        self.C = C
        self.max_iter = max_iter
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.clf = LogisticRegression(
            C=C,
            max_iter=max_iter,
            solver='lbfgs',
            random_state=random_state
        )
        self.is_fitted = False

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train logistic regression classifier.
        X_train: [N_train, F], y_train: [N_train]
        """
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train classifier
        self.clf.fit(X_train_scaled, y_train)
        self.is_fitted = True

        # Compute training accuracy
        train_pred = self.clf.predict(X_train_scaled)
        train_acc = accuracy_score(y_train, train_pred)
        print(f"  Training accuracy: {train_acc:.3f}")

    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """
        Predict labels for test set.
        X_test: [N_test, F] -> [N_test]
        """
        if not self.is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")

        X_test_scaled = self.scaler.transform(X_test)
        return self.clf.predict(X_test_scaled)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Compute test accuracy and confusion matrix.
        Returns: {"accuracy": float, "confusion_matrix": [[TN, FP], [FN, TP]]}
        """
        y_pred = self.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)

        print(f"  Test accuracy: {accuracy:.3f}")
        print(f"  Confusion matrix:\n{conf_matrix}")

        return {
            "accuracy": accuracy,
            "confusion_matrix": conf_matrix.tolist(),
            "predictions": y_pred.tolist()
        }

    def get_coefficients(self) -> np.ndarray:
        """Get classifier coefficients for feature importance"""
        if not self.is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")
        return self.clf.coef_[0]

    def save_model(self, filepath: str) -> None:
        """Pickle classifier and scaler"""
        if not self.is_fitted:
            raise ValueError("Classifier not fitted. Call fit() first.")

        model_data = {
            "clf": self.clf,
            "scaler": self.scaler,
            "C": self.C,
            "max_iter": self.max_iter,
            "random_state": self.random_state
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"✓ Model saved to {filepath}")

    @staticmethod
    def load_model(filepath: str) -> 'BinaryClassifier':
        """Load pickled classifier"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        classifier = BinaryClassifier(
            C=model_data["C"],
            max_iter=model_data["max_iter"],
            random_state=model_data["random_state"]
        )
        classifier.clf = model_data["clf"]
        classifier.scaler = model_data["scaler"]
        classifier.is_fitted = True

        return classifier
