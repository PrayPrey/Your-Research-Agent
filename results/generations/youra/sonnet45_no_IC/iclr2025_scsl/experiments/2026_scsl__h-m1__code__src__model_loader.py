"""Model loader for H-M1 - loads H-E1 trained model or retrains if needed."""

import pickle
import sys
from pathlib import Path
from typing import Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np


class ModelLoader:
    def __init__(self, h_e1_base_path: str = '../../h-e1/code'):
        """Initialize loader with H-E1 base directory path."""
        self.h_e1_base_path = Path(h_e1_base_path)
        # Model files are in h-e1/code/models/
        self.model_path = self.h_e1_base_path / 'models' / 'lr_classifier.pkl'
        self.scaler_path = self.h_e1_base_path / 'models' / 'feature_scaler.pkl'
        # Data file is in h-e1/code/data/
        self.data_path = self.h_e1_base_path / 'data' / 'raw_metadata.csv'

    def load_trained_lr(self) -> Tuple[LogisticRegression, StandardScaler]:
        """Load trained LR model and scaler from H-E1 artifacts.

        Returns:
            Tuple of (model, scaler)

        Raises:
            FileNotFoundError: If model files not found, triggers retrain fallback
        """
        try:
            with open(self.model_path, 'rb') as f:
                model = pickle.load(f)
            with open(self.scaler_path, 'rb') as f:
                scaler = pickle.load(f)

            # Verify model structure (6 real features only)
            assert model.coef_.shape == (1, 6), f"Invalid coef shape: {model.coef_.shape} (expected (1, 6) for 6 real features)"
            assert hasattr(scaler, 'mean_') and hasattr(scaler, 'scale_'), "Invalid scaler"

            print(f"✓ Loaded H-E1 model from {self.model_path}")
            return model, scaler

        except FileNotFoundError as e:
            print(f"⚠ Model files not found: {e}")
            print(" Falling back to retrain using H-E1 pipeline...")
            return self.retrain_fallback()

    def retrain_fallback(self) -> Tuple[LogisticRegression, StandardScaler]:
        """Retrain LR model using H-E1 MaintenanceClassifier.

        Returns:
            Tuple of (trained_model, fitted_scaler)
        """
        # Add H-E1 to path
        sys.path.insert(0, str(self.h_e1_base_path))

        from src.trainer import MaintenanceClassifier
        from src.feature_engineer import FeatureEngineer
        from config import ExperimentConfig

        print(" Loading H-E1 dataset...")
        # Use direct path instead of config
        if not self.data_path.exists():
            raise FileNotFoundError(f"H-E1 dataset not found: {self.data_path}")

        # Load and prepare data
        raw_data = pd.read_csv(self.data_path)
        engineer = FeatureEngineer()
        X = engineer.transform_features(raw_data)
        y = engineer.create_labels(raw_data, threshold_days=180)

        # Train model
        print(" Training MaintenanceClassifier...")
        classifier = MaintenanceClassifier(random_state=42)
        X_train, X_test, y_train, y_test = classifier.prepare_data(X, y)
        classifier.train(X_train, y_train)

        print(f"✓ Retrained model (Acc: {classifier.model.score(X_test, y_test):.3f})")

        return classifier.model, classifier.scaler

    def _load_h_e1_data(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Load H-E1 dataset for retraining. Returns: (X, y)"""
        sys.path.insert(0, str(self.h_e1_base_path))
        from src.feature_engineer import FeatureEngineer
        from config import ExperimentConfig

        config = ExperimentConfig()
        data_path = self.h_e1_base_path / config.data_output_path
        raw_data = pd.read_csv(data_path)

        engineer = FeatureEngineer()
        X = engineer.transform_features(raw_data)
        y = engineer.create_labels(raw_data, threshold_days=180)

        return X, y
