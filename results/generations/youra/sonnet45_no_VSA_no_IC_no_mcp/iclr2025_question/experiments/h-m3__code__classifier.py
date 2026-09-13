"""Gate 1 viability classifier and random baseline."""

import numpy as np


class Gate1ViabilityClassifier:
    """Predict hypothesis viability using Gate 1 micro-pilot overhead."""

    def __init__(self, k: float, threshold: float = 0.10):
        """
        Args:
            k: Scaling factor from H-M1 (slope of O_10 vs O_full)
            threshold: Viability threshold (default 10%)
        """
        self.k = k
        self.threshold = threshold

    def predict(self, O_10: float) -> tuple[str, float]:
        """
        Predict viability for single hypothesis.

        Args:
            O_10: 10-sample overhead (proportion 0.0-1.0)

        Returns:
            prediction: "non-viable" if O_pred > threshold, else "viable"
            O_pred: Predicted full-scale overhead
        """
        O_pred = O_10 * self.k
        prediction = "non-viable" if O_pred > self.threshold else "viable"
        return prediction, O_pred

    def predict_batch(self, O_10_array: np.ndarray) -> tuple[list, list]:
        """Predict viability for batch of hypotheses."""
        predictions = []
        O_preds = []
        for O_10 in O_10_array:
            pred, O_pred = self.predict(O_10)
            predictions.append(pred)
            O_preds.append(O_pred)
        return predictions, O_preds


class RandomBaseline:
    """Random guessing baseline (50% for each class)."""

    def __init__(self, seed: int = 42):
        """
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed

    def predict(self, n_samples: int) -> list[str]:
        """
        Random predictions: 50% probability for each class.

        Args:
            n_samples: Number of predictions (30 for our corpus)

        Returns:
            predictions: List of "viable" or "non-viable"
        """
        np.random.seed(self.seed)
        return list(np.random.choice(["viable", "non-viable"], size=n_samples))
