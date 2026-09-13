"""Model Training Module for Repository Maintenance Classification."""

import numpy as np
import pandas as pd
import pickle
from typing import Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression


class MaintenanceClassifier:
    """Logistic Regression classifier for repository maintenance prediction."""

    def __init__(self, random_state: int = 42):
        """Initialize classifier with configuration.

        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = LogisticRegression(
            max_iter=1000,
            solver='lbfgs',
            class_weight='balanced',
            random_state=random_state
        )
        self.feature_names = None
        self.is_fitted = False

    def prepare_data(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        test_size: float = 0.20
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data into train/test sets with stratification.

        Args:
            X: Feature matrix (DataFrame)
            y: Labels array
            test_size: Fraction of data for test set

        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        self.feature_names = X.columns.tolist()

        X_train, X_test, y_train, y_test = train_test_split(
            X.values,
            y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )

        return X_train, X_test, y_train, y_test

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train Logistic Regression model with normalization.

        Args:
            X_train: Training features
            y_train: Training labels

        Returns:
            Dict with training info (convergence status, iterations)
        """
        # Fit scaler on training data only
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_fitted = True

        # Check convergence
        n_iter = self.model.n_iter_[0] if hasattr(self.model, 'n_iter_') else None

        training_info = {
            'converged': n_iter < 1000 if n_iter else True,
            'n_iter': int(n_iter) if n_iter else 0,
            'classes': self.model.classes_.tolist(),
            'n_features': X_train.shape[1]
        }

        return training_info

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels for test data.

        Args:
            X: Feature matrix (raw, will be scaled internally)

        Returns:
            Predicted labels
        """
        if not self.is_fitted:
            raise ValueError("Model not trained. Call train() first.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities for test data.

        Args:
            X: Feature matrix (raw, will be scaled internally)

        Returns:
            Probability matrix (n_samples, 2)
        """
        if not self.is_fitted:
            raise ValueError("Model not trained. Call train() first.")

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def get_feature_importance(self) -> pd.DataFrame:
        """Extract feature importance from logistic regression coefficients.

        Returns:
            DataFrame with feature names and absolute coefficient values
        """
        if not self.is_fitted:
            raise ValueError("Model not trained. Call train() first.")

        coefficients = self.model.coef_[0]
        importance = pd.DataFrame({
            'feature': self.feature_names,
            'coefficient': coefficients,
            'abs_coefficient': np.abs(coefficients)
        })
        importance = importance.sort_values('abs_coefficient', ascending=False)

        return importance

    def save_model(self, model_path: str, scaler_path: str) -> None:
        """Persist trained model and scaler to disk.

        Args:
            model_path: Path to save model (.pkl)
            scaler_path: Path to save scaler (.pkl)
        """
        if not self.is_fitted:
            raise ValueError("Model not trained. Call train() first.")

        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)

        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)

        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")

    def load_model(self, model_path: str, scaler_path: str) -> None:
        """Load trained model and scaler from disk.

        Args:
            model_path: Path to model file (.pkl)
            scaler_path: Path to scaler file (.pkl)
        """
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)

        self.is_fitted = True
        print("Model and scaler loaded successfully")
