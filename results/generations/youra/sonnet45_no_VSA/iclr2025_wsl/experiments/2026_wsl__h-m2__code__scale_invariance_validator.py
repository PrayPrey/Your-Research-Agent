"""
Scale Invariance (Coefficient of Variation) Validator for H-M2

Validates intra-family scale invariance via CV = σ/μ across model scale families.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional


class ScaleInvarianceValidator:
    """Validator for scale invariance using Coefficient of Variation (CV)."""

    def __init__(self, cv_threshold: float = 0.15):
        """
        Initialize scale invariance validator.

        Args:
            cv_threshold: Maximum CV for scale invariance (default: 0.15)
        """
        self.cv_threshold = cv_threshold

    def compute_cv(self, values: np.ndarray) -> float:
        """
        Compute coefficient of variation.

        Args:
            values: Array of R values

        Returns:
            CV = σ / μ
        """
        if len(values) < 2:
            return 0.0

        mean_val = np.mean(values)
        if mean_val == 0:
            return 0.0

        std_val = np.std(values, ddof=1)
        cv = std_val / mean_val

        return cv

    def validate_scale_family(
        self,
        features_df: pd.DataFrame,
        scale_family: Optional[List[str]] = None
    ) -> Dict:
        """
        Validate scale invariance across a model scale family.

        Args:
            features_df: DataFrame with columns ['model_name', 'family', 'param_mass_ratio']
            scale_family: List of model names (default: ResNet variants)

        Returns:
            {
                'cv': float,
                'mean_R': float,
                'std_R': float,
                'models': list,
                'n_models': int,
                'passed': bool,
                'threshold': float
            }
        """
        if scale_family is None:
            # Default: ResNet scale family
            scale_family = ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']

        # Filter to scale family
        scale_df = features_df[features_df['model_name'].isin(scale_family)]

        if len(scale_df) == 0:
            return {
                'cv': None,
                'mean_R': None,
                'std_R': None,
                'models': scale_family,
                'n_models': 0,
                'passed': False,
                'threshold': self.cv_threshold,
                'error': 'No models found in scale family'
            }

        R_values = scale_df['param_mass_ratio'].values
        mean_R = np.mean(R_values)
        std_R = np.std(R_values, ddof=1)
        cv = self.compute_cv(R_values)

        return {
            'cv': cv,
            'mean_R': mean_R,
            'std_R': std_R,
            'models': scale_df['model_name'].tolist(),
            'n_models': len(R_values),
            'passed': cv < self.cv_threshold,
            'threshold': self.cv_threshold
        }

    def validate_all_families(self, features_df: pd.DataFrame) -> Dict:
        """
        Validate scale invariance for all major architecture families.

        Args:
            features_df: DataFrame with model features

        Returns:
            {
                'cnn_cv': dict,
                'transformer_cv': dict,
                'overall_passed': bool
            }
        """
        # CNN family: ResNet scale variants
        cnn_scale_family = ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']

        # Transformer family: ViT scale variants
        transformer_scale_family = ['vit_tiny_patch16_224', 'vit_small_patch16_224',
                                    'vit_base_patch16_224', 'vit_large_patch16_224']

        cnn_result = self.validate_scale_family(features_df, cnn_scale_family)
        transformer_result = self.validate_scale_family(features_df, transformer_scale_family)

        overall_passed = (
            cnn_result.get('passed', False) and
            transformer_result.get('passed', False)
        )

        return {
            'cnn_cv': cnn_result,
            'transformer_cv': transformer_result,
            'overall_passed': overall_passed
        }
