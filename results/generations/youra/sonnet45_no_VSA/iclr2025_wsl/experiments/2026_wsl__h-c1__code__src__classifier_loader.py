"""Classifier Loader - loads h-e1 classifier or trains fallback"""

import joblib
import logging
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

logger = logging.getLogger(__name__)


class ClassifierLoader:
    def __init__(self, classifier_path: str = None, scaler_path: str = None):
        self.classifier_path = classifier_path
        self.scaler_path = scaler_path

    def load_or_train(
        self,
        fallback_features_df: pd.DataFrame = None,
        fallback_labels: pd.Series = None
    ) -> tuple:
        """Load h-e1 classifier or train fallback.

        Args:
            fallback_features_df: Features for fallback training
            fallback_labels: Labels for fallback training

        Returns:
            (classifier, scaler) tuple
        """
        try:
            classifier = joblib.load(self.classifier_path)
            scaler = joblib.load(self.scaler_path)
            logger.info(f"Loaded classifier from {self.classifier_path}")
            logger.info(f"Loaded scaler from {self.scaler_path}")
            return classifier, scaler

        except FileNotFoundError as e:
            logger.warning(f"Classifier not found: {e}")
            logger.warning("Training fallback classifier on provided features...")

            if fallback_features_df is None or fallback_labels is None:
                raise ValueError(
                    "Classifier files missing and no fallback data provided. "
                    "Cannot proceed without training data."
                )

            # Train fallback
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(fallback_features_df)

            classifier = LogisticRegression(
                random_state=42,
                max_iter=1000,
                class_weight='balanced'
            )
            classifier.fit(X_scaled, fallback_labels)

            # Verify accuracy
            train_pred = classifier.predict(X_scaled)
            train_acc = accuracy_score(fallback_labels, train_pred)
            logger.info(f"Fallback classifier training accuracy: {train_acc:.3f}")

            if train_acc < 0.80:
                logger.warning(
                    f"Fallback classifier accuracy ({train_acc:.3f}) < 0.80. "
                    "Results may be unreliable."
                )

            return classifier, scaler

    def save_classifier(self, classifier, scaler, classifier_path: str, scaler_path: str):
        """Save classifier and scaler to disk."""
        joblib.dump(classifier, classifier_path)
        joblib.dump(scaler, scaler_path)
        logger.info(f"Saved classifier to {classifier_path}")
        logger.info(f"Saved scaler to {scaler_path}")
