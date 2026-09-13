"""
Edge Case Detector for H-M1
Detects edge case architectures (NormFree, MetaFormer, ConvNeXt)
"""
import pandas as pd
import json
from typing import Dict, List


class EdgeCaseDetector:
    """
    Detects edge case architectures that deviate from typical normalization patterns.
    """

    def __init__(self):
        pass

    def detect_edge_cases(self, features_df: pd.DataFrame) -> Dict:
        """
        Detect edge case architectures.

        Edge Cases:
        - NormFree: no_norm_flag == 1 (e.g., VGG-16)
        - MetaFormer: 'poolformer' in model name
        - ConvNeXt: 'convnext' in model name (modern CNN with LayerNorm)

        Args:
            features_df: DataFrame with columns [model_name, family, bn_count, ln_count, no_norm_flag, ...]

        Returns:
            {
                'NormFree': [EdgeCaseModel, ...],
                'MetaFormer': [...],
                'ConvNeXt': [...],
                'total_edge_cases': int,
                'edge_case_rate': float
            }
        """
        # Detect NormFree
        normfree_models = self._detect_normfree(features_df)

        # Detect MetaFormer
        metaformer_models = self._detect_metaformer(features_df)

        # Detect ConvNeXt
        convnext_models = self._detect_convnext(features_df)

        total_edge_cases = len(normfree_models) + len(metaformer_models) + len(convnext_models)
        total_models = len(features_df)
        edge_case_rate = total_edge_cases / total_models if total_models > 0 else 0.0

        return {
            'NormFree': normfree_models,
            'MetaFormer': metaformer_models,
            'ConvNeXt': convnext_models,
            'total_edge_cases': total_edge_cases,
            'edge_case_rate': edge_case_rate
        }

    def _detect_normfree(self, features_df: pd.DataFrame) -> List[Dict]:
        """Detect NormFree architectures (no normalization layers)."""
        normfree = features_df[features_df.get('no_norm_flag', 0) == 1]

        return [
            {
                'model': row['model_name'],
                'family': row['family'],
                'bn_count': int(row['bn_count']),
                'ln_count': int(row['ln_count']),
                'notes': 'No normalization layers'
            }
            for _, row in normfree.iterrows()
        ]

    def _detect_metaformer(self, features_df: pd.DataFrame) -> List[Dict]:
        """Detect MetaFormer architectures (e.g., PoolFormer)."""
        metaformer = features_df[
            features_df['model_name'].str.contains('poolformer', case=False, na=False)
        ]

        return [
            {
                'model': row['model_name'],
                'family': row['family'],
                'bn_count': int(row['bn_count']),
                'ln_count': int(row['ln_count']),
                'notes': 'Token mixer architecture'
            }
            for _, row in metaformer.iterrows()
        ]

    def _detect_convnext(self, features_df: pd.DataFrame) -> List[Dict]:
        """Detect ConvNeXt architectures (modern CNNs with LayerNorm)."""
        convnext = features_df[
            features_df['model_name'].str.contains('convnext', case=False, na=False)
        ]

        return [
            {
                'model': row['model_name'],
                'family': row['family'],
                'bn_count': int(row['bn_count']),
                'ln_count': int(row['ln_count']),
                'notes': 'Modern CNN with LayerNorm'
            }
            for _, row in convnext.iterrows()
        ]

    def save_edge_cases(self, results: Dict, output_path: str):
        """Save edge case detection results to JSON."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
