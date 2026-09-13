"""
Edge Case Threshold Violation Analyzer for H-M2

Detects models that violate expected R thresholds for their family.
"""

import pandas as pd
from typing import Dict, List


class EdgeCaseAnalyzer:
    """Analyzer for threshold violations and edge cases."""

    def __init__(self, cnn_threshold: float = 0.6, transformer_threshold: float = 0.2):
        """
        Initialize edge case analyzer.

        Args:
            cnn_threshold: Minimum R for CNNs (default: 0.6)
            transformer_threshold: Maximum R for Transformers (default: 0.2)
        """
        self.cnn_threshold = cnn_threshold
        self.transformer_threshold = transformer_threshold

    def detect_violations(self, features_df: pd.DataFrame) -> Dict:
        """
        Detect threshold violations across all families.

        Args:
            features_df: DataFrame with columns ['model_name', 'family', 'param_mass_ratio']

        Returns:
            {
                'cnn_violations': list,
                'transformer_violations': list,
                'cnn_violation_rate': float,
                'transformer_violation_rate': float,
                'total_violations': int
            }
        """
        cnn_models = features_df[features_df['family'] == 'CNN']
        transformer_models = features_df[features_df['family'] == 'Transformer']

        # CNN violations: R < 0.6
        cnn_violations = cnn_models[cnn_models['param_mass_ratio'] < self.cnn_threshold]
        cnn_violation_list = cnn_violations[['model_name', 'param_mass_ratio']].to_dict('records')

        # Transformer violations: R > 0.2
        transformer_violations = transformer_models[
            transformer_models['param_mass_ratio'] > self.transformer_threshold
        ]
        transformer_violation_list = transformer_violations[['model_name', 'param_mass_ratio']].to_dict('records')

        # Violation rates
        cnn_violation_rate = len(cnn_violations) / len(cnn_models) if len(cnn_models) > 0 else 0.0
        transformer_violation_rate = (
            len(transformer_violations) / len(transformer_models)
            if len(transformer_models) > 0 else 0.0
        )

        return {
            'cnn_violations': cnn_violation_list,
            'transformer_violations': transformer_violation_list,
            'cnn_violation_count': len(cnn_violations),
            'transformer_violation_count': len(transformer_violations),
            'cnn_total': len(cnn_models),
            'transformer_total': len(transformer_models),
            'cnn_violation_rate': cnn_violation_rate,
            'transformer_violation_rate': transformer_violation_rate,
            'total_violations': len(cnn_violations) + len(transformer_violations),
            'thresholds': {
                'cnn_min': self.cnn_threshold,
                'transformer_max': self.transformer_threshold
            }
        }

    def analyze_edge_cases(self, features_df: pd.DataFrame) -> Dict:
        """
        Analyze known edge case architectures.

        Args:
            features_df: DataFrame with model features

        Returns:
            Analysis of edge case models (NormFree, ConvNeXt, MLP-Mixer, etc.)
        """
        edge_case_patterns = {
            'normfree': ['vgg'],  # NormFree models
            'convnext': ['convnext'],  # ConvNeXt family
            'metaformer': ['poolformer'],  # MetaFormer
            'mlp_mixer': ['mixer', 'mlp_mixer'],  # MLP-Mixer
            'hybrid': ['levit', 'convit', 'pit', 'visformer']  # Hybrid architectures
        }

        edge_case_results = {}

        for category, patterns in edge_case_patterns.items():
            # Find models matching patterns
            mask = features_df['model_name'].str.contains('|'.join(patterns), case=False, na=False)
            edge_models = features_df[mask]

            if len(edge_models) > 0:
                edge_case_results[category] = {
                    'count': len(edge_models),
                    'models': edge_models[['model_name', 'family', 'param_mass_ratio']].to_dict('records'),
                    'mean_R': edge_models['param_mass_ratio'].mean(),
                    'std_R': edge_models['param_mass_ratio'].std()
                }

        return edge_case_results
