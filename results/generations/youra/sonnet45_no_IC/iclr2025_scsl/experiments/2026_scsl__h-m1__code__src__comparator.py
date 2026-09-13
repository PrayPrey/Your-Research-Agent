"""Model comparator for H-M1 - LR vs GB performance and feature importance."""

from sklearn.metrics import accuracy_score, f1_score
import numpy as np
from typing import Dict, Tuple


class ModelComparator:
    def __init__(
        self,
        lr_model,
        gb_model,
        scaler,
        feature_names: list
    ):
        """Initialize comparator with both models."""
        self.lr_model = lr_model
        self.gb_model = gb_model
        self.scaler = scaler
        self.feature_names = feature_names

    def compute_performance_gap(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """Compute accuracy/F1 gap between LR and GB.

        Args:
            X_test: Test features [N, 8] (raw, will be scaled)
            y_test: Test labels [N]

        Returns:
            Dict with keys: lr_accuracy, gb_accuracy, gap, lr_f1, gb_f1
        """
        # Scale test data
        X_test_scaled = self.scaler.transform(X_test)

        # LR predictions
        lr_pred = self.lr_model.predict(X_test_scaled)
        lr_acc = accuracy_score(y_test, lr_pred)
        lr_f1 = f1_score(y_test, lr_pred)

        # GB predictions
        gb_pred = self.gb_model.predict(X_test_scaled)
        gb_acc = accuracy_score(y_test, gb_pred)
        gb_f1 = f1_score(y_test, gb_pred)

        # Performance gap
        gap = abs(lr_acc - gb_acc)

        return {
            'lr_accuracy': lr_acc,
            'gb_accuracy': gb_acc,
            'gap': gap,
            'lr_f1': lr_f1,
            'gb_f1': gb_f1,
            'lr_pred': lr_pred,
            'gb_pred': gb_pred
        }

    def compare_feature_importance(
        self,
        lr_importance: Dict[str, float],
        gb_importance: np.ndarray
    ) -> Dict[str, any]:
        """Compare feature importance between models.

        Args:
            lr_importance: Dict from LR coefficient magnitudes
            gb_importance: Array [8] from GB feature_importances_

        Returns:
            Dict with keys: lr_top3, gb_top3, overlap_count, overlap_features
        """
        # GB importance as dict
        gb_importance_dict = dict(zip(self.feature_names, gb_importance))

        # Top-3 features for each model
        lr_top3 = sorted(lr_importance, key=lr_importance.get, reverse=True)[:3]
        gb_top3 = sorted(gb_importance_dict, key=gb_importance_dict.get, reverse=True)[:3]

        # Overlap
        overlap = set(lr_top3) & set(gb_top3)
        overlap_count = len(overlap)

        return {
            'lr_top3': lr_top3,
            'gb_top3': gb_top3,
            'overlap_count': overlap_count,
            'overlap_features': list(overlap),
            'lr_importance': lr_importance,
            'gb_importance': gb_importance_dict
        }

    def check_linear_sufficiency(
        self,
        gap: float,
        threshold: float = 0.05
    ) -> bool:
        """Check if linear model is sufficient. Returns: gap <= threshold"""
        return gap <= threshold
