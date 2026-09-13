"""Mechanism analyzer for H-M1 - coefficient analysis and PCA visualization."""

from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List


class MechanismAnalyzer:
    def __init__(self, lr_model: LogisticRegression, feature_names: List[str]):
        """Initialize analyzer with trained LR model.

        Args:
            lr_model: Trained sklearn LogisticRegression
            feature_names: List of 6 feature names (REAL DATA ONLY)
        """
        self.lr_model = lr_model
        self.feature_names = feature_names

    def extract_coefficients(self) -> Dict[str, float]:
        """Extract coefficients from LR model.

        Returns:
            Dict mapping feature_name -> coefficient_value
        """
        coef = self.lr_model.coef_[0]  # Shape: [6] for 6 real features
        coefficients = dict(zip(self.feature_names, coef))
        return coefficients

    def verify_coefficient_signs(
        self,
        coefficients: Dict[str, float]
    ) -> Tuple[bool, Dict[str, str]]:
        """Verify coefficient signs match expected causal pathway.

        Expected:
            - days_since_last_commit: negative
            - All other features: positive

        Returns:
            Tuple of (all_correct: bool, sign_report: dict)
        """
        # REAL FEATURES ONLY - removed tautological features
        expected_signs = {
            'days_since_last': 'negative',
            'stars_log': 'positive',
            'forks_log': 'positive',
            'contributors_log': 'positive',
            'commits_log': 'positive',
            'issues_log': 'positive',
        }

        sign_report = {}
        all_correct = True

        for feature, expected in expected_signs.items():
            actual_value = coefficients.get(feature, 0)
            if expected == 'negative':
                is_correct = actual_value < 0
            else:  # positive
                is_correct = actual_value > 0

            sign_report[feature] = {
                'expected': expected,
                'actual_value': actual_value,
                'actual_sign': 'negative' if actual_value < 0 else 'positive',
                'correct': is_correct
            }

            if not is_correct:
                all_correct = False

        return all_correct, sign_report

    def compute_feature_importance(
        self,
        use_abs: bool = True
    ) -> Dict[str, float]:
        """Compute feature importance from coefficient magnitudes.

        Args:
            use_abs: If True, use absolute values

        Returns:
            Dict mapping feature_name -> importance_score
        """
        coefficients = self.extract_coefficients()
        if use_abs:
            importance = {k: abs(v) for k, v in coefficients.items()}
        else:
            importance = coefficients

        return importance

    def pca_projection(
        self,
        X: np.ndarray,
        n_components: int = 2
    ) -> Tuple[np.ndarray, PCA]:
        """Project features to 2D using PCA.

        Args:
            X: Feature matrix [N, 8] (pre-scaled)
            n_components: Number of PCA components

        Returns:
            Tuple of (X_2d: [N, 2], fitted_pca)
        """
        pca = PCA(n_components=n_components)
        X_2d = pca.fit_transform(X)  # [N, 8] -> [N, 2]

        print(f"✓ PCA explained variance: {pca.explained_variance_ratio_}")

        return X_2d, pca

    def generate_decision_boundary_mesh(
        self,
        X_2d: np.ndarray,
        pca: PCA,
        lr_model: LogisticRegression
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate mesh grid for decision boundary visualization.

        Args:
            X_2d: 2D projected data [N, 2]
            pca: Fitted PCA object
            lr_model: Trained LR model

        Returns:
            Tuple of (xx: [100, 100], yy: [100, 100], Z: [100, 100])
        """
        # Create mesh grid
        x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
        y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
        xx, yy = np.meshgrid(
            np.linspace(x_min, x_max, 100),
            np.linspace(y_min, y_max, 100)
        )

        # Mesh to 2D points
        mesh_2d = np.c_[xx.ravel(), yy.ravel()]  # [10000, 2]

        # Project back to original 8D space
        mesh_original = pca.inverse_transform(mesh_2d)  # [10000, 8]

        # Predict on mesh
        Z = lr_model.predict(mesh_original).reshape(xx.shape)  # [100, 100]

        return xx, yy, Z
