"""
Feature Importance Extractor for H-M1
Extracts and ranks feature importance from trained classifier
"""
import pickle
import numpy as np
import pandas as pd
from typing import Dict
from pathlib import Path


class FeatureImportanceExtractor:
    """
    Extracts feature importance from trained Logistic Regression classifier.
    """

    def __init__(self, classifier_path: str):
        """
        Args:
            classifier_path: Path to classifier.pkl file
        """
        self.classifier_path = classifier_path
        self.classifier = None

    def load_classifier(self):
        """Load classifier from pickle file."""
        import sys
        import importlib

        # Add parent directory to path to find modules
        parent_dir = str(Path(self.classifier_path).parent.parent / 'src')
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        with open(self.classifier_path, 'rb') as f:
            try:
                self.classifier = pickle.load(f)
            except Exception as e:
                # Try with different encoding
                try:
                    self.classifier = pickle.load(f, encoding='latin1')
                except:
                    # Last resort: use joblib if available
                    try:
                        import joblib
                        self.classifier = joblib.load(self.classifier_path)
                    except:
                        raise RuntimeError(f"Failed to load classifier from {self.classifier_path}: {e}")

    def extract_importance(
        self,
        feature_names: list = None
    ) -> Dict:
        """
        Extract feature importance from classifier coefficients.

        For multi-class LogisticRegression (one-vs-rest):
        - Coefficient matrix: (n_classes, n_features)
        - Importance: Average |coefficient| across classes

        Args:
            feature_names: List of feature names (default from h-e1:
                           ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio'])

        Returns:
            {
                'feature_importance': {feature: coefficient, ...},
                'feature_ranking': [(feature, coefficient, rank), ...],
                'bn_count_coef': float,
                'ln_count_coef': float,
                'bn_passed': bool,  # > 0.1
                'ln_passed': bool,  # > 0.1
                's1_criterion_passed': bool  # Both > 0.1
            }
        """
        if self.classifier is None:
            self.load_classifier()

        # Default feature names (from h-e1)
        if feature_names is None:
            feature_names = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

        # Extract coefficients
        # Shape: (n_classes, n_features) for multi-class
        # Average absolute coefficient across classes
        coef_matrix = self.classifier.coef_  # (3, 5) for 3 classes, 5 features
        feature_importance = np.mean(np.abs(coef_matrix), axis=0)  # (5,)

        # Create feature importance dict
        importance_dict = {
            name: float(coef) for name, coef in zip(feature_names, feature_importance)
        }

        # Rank features by importance (descending)
        ranked = sorted(
            [(name, coef, rank+1) for rank, (name, coef) in enumerate(
                sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
            )],
            key=lambda x: x[2]
        )

        # Check S1 criterion: bn_count and ln_count > 0.1
        bn_coef = importance_dict.get('bn_count', 0.0)
        ln_coef = importance_dict.get('ln_count', 0.0)
        bn_passed = bn_coef > 0.1
        ln_passed = ln_coef > 0.1
        s1_passed = bn_passed and ln_passed

        return {
            'feature_importance': importance_dict,
            'feature_ranking': ranked,
            'bn_count_coef': bn_coef,
            'ln_count_coef': ln_coef,
            'bn_passed': bn_passed,
            'ln_passed': ln_passed,
            's1_criterion_passed': s1_passed
        }

    def save_importance(self, results: Dict, output_path: str):
        """Save feature importance to CSV."""
        ranking_data = []
        for feature, coef, rank in results['feature_ranking']:
            ranking_data.append({
                'feature': feature,
                'coefficient': coef,
                'rank': rank,
                'interpretation': self._interpret_feature(feature, coef)
            })

        df = pd.DataFrame(ranking_data)
        df.to_csv(output_path, index=False)

    def _interpret_feature(self, feature: str, coef: float) -> str:
        """Interpret feature importance."""
        if coef > 1.0:
            strength = 'Strong discriminator'
        elif coef > 0.5:
            strength = 'Moderate discriminator'
        elif coef > 0.1:
            strength = 'Weak discriminator'
        else:
            strength = 'Negligible'

        # Feature-specific context
        if feature == 'param_mass_ratio':
            context = '(conv vs linear mass)'
        elif feature == 'bn_count':
            context = '(CNN signature)'
        elif feature == 'ln_count':
            context = '(Transformer signature)'
        elif feature == 'no_norm_flag':
            context = '(NormFree detection)'
        elif feature == 'gn_count':
            context = '(GroupNorm rare)'
        else:
            context = ''

        return f"{strength} {context}".strip()
