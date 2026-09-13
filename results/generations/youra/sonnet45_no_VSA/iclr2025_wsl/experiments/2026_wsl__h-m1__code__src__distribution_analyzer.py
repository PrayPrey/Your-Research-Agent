"""
Normalization Distribution Analyzer for H-M1
Computes per-family normalization layer statistics
"""
import pandas as pd
import numpy as np
import json
from typing import Dict


class NormalizationDistributionAnalyzer:
    """
    Analyzes normalization layer distributions across architecture families.
    """

    def __init__(self):
        pass

    def compute_distributions(self, features_df: pd.DataFrame) -> Dict:
        """
        Compute per-family normalization layer statistics.

        Args:
            features_df: DataFrame with columns [model_name, family, bn_count, ln_count, gn_count, ...]

        Returns:
            {
                'CNN': {
                    'bn_count': {'mean': float, 'median': float, 'std': float},
                    'ln_count': {...},
                    'gn_count': {...},
                    'dominant_norm': str
                },
                'Transformer': {...},
                'Hybrid': {...}
            }
        """
        results = {}

        families = ['CNN', 'Transformer', 'Hybrid']
        for family in families:
            family_df = features_df[features_df['family'] == family]

            if len(family_df) == 0:
                continue

            # Compute statistics for each normalization type
            family_stats = {}
            for norm_type in ['bn_count', 'ln_count', 'gn_count']:
                if norm_type in family_df.columns:
                    family_stats[norm_type] = {
                        'mean': float(family_df[norm_type].mean()),
                        'median': float(family_df[norm_type].median()),
                        'std': float(family_df[norm_type].std())
                    }

            # Determine dominant normalization type
            family_stats['dominant_norm'] = self._determine_dominant_norm(family_df)

            results[family] = family_stats

        return results

    def _determine_dominant_norm(self, family_df: pd.DataFrame) -> str:
        """
        Determine which normalization type dominates in this family.

        Dominance: >50% of models have this norm type as the max count.

        Args:
            family_df: DataFrame filtered to single family

        Returns:
            'BatchNorm', 'LayerNorm', 'GroupNorm', or 'Mixed'
        """
        if len(family_df) == 0:
            return 'Unknown'

        # Count which norm type has max count for each model
        bn_dominant = (family_df['bn_count'] > family_df['ln_count']) & \
                     (family_df['bn_count'] > family_df['gn_count'])
        ln_dominant = (family_df['ln_count'] > family_df['bn_count']) & \
                     (family_df['ln_count'] > family_df['gn_count'])
        gn_dominant = (family_df['gn_count'] > family_df['bn_count']) & \
                     (family_df['gn_count'] > family_df['ln_count'])

        bn_count = bn_dominant.sum()
        ln_count = ln_dominant.sum()
        gn_count = gn_dominant.sum()

        total = len(family_df)

        # Check if any type dominates (>50%)
        if bn_count / total > 0.5:
            return 'BatchNorm'
        elif ln_count / total > 0.5:
            return 'LayerNorm'
        elif gn_count / total > 0.5:
            return 'GroupNorm'
        else:
            return 'Mixed'

    def save_distributions(self, results: Dict, output_path: str):
        """Save distribution statistics to JSON."""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
