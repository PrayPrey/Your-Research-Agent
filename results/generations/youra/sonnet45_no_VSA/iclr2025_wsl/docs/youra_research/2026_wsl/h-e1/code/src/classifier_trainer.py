"""Classifier training module"""

import pandas as pd
import joblib
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from config import CLASSIFIER_CONFIG, FEATURE_NAMES


class LogisticClassifierTrainer:
    """Train LogisticRegression classifier on extracted features"""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.logger = logging.getLogger(__name__)

    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> tuple:
        """
        Train LogisticRegression with StandardScaler preprocessing.

        Args:
            X_train: Feature matrix (N x 5)
            y_train: Family labels

        Returns:
            (classifier, scaler) tuple
        """
        self.logger.info("Training LogisticRegression classifier...")

        # Feature scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        # Train classifier
        classifier = LogisticRegression(**CLASSIFIER_CONFIG)
        classifier.fit(X_train_scaled, y_train)

        self.logger.info("Training completed")
        self.logger.info(f"Training samples: {len(X_train)}")
        self.logger.info(f"Classes: {classifier.classes_}")

        return classifier, scaler

    def save_artifacts(self, classifier, scaler, output_dir: str):
        """Save trained classifier and scaler to disk"""
        classifier_path = f"{output_dir}/classifier.pkl"
        scaler_path = f"{output_dir}/scaler.pkl"

        joblib.dump(classifier, classifier_path)
        joblib.dump(scaler, scaler_path)

        self.logger.info(f"Saved classifier to {classifier_path}")
        self.logger.info(f"Saved scaler to {scaler_path}")

    def load_artifacts(self, model_dir: str) -> tuple:
        """Load classifier and scaler from disk"""
        classifier_path = f"{model_dir}/classifier.pkl"
        scaler_path = f"{model_dir}/scaler.pkl"

        classifier = joblib.load(classifier_path)
        scaler = joblib.load(scaler_path)

        self.logger.info(f"Loaded classifier from {classifier_path}")
        return classifier, scaler
