"""
Feature Completeness Validator
Validates that ≥95% of model-benchmark combinations have complete features
Based on 03_logic.md specifications
"""
import pandas as pd
import numpy as np
from typing import Dict, List


class FeatureValidator:
    """Validates feature completeness and data quality."""

    def __init__(self, feature_df: pd.DataFrame, threshold: float = 95.0):
        self.feature_df = feature_df
        self.threshold = threshold
        # Core features that MUST be present for completeness
        self.core_features = [
            'pass@1',
            'runtime_q25', 'runtime_q50', 'runtime_q75'
        ]
        # All features for reporting
        self.all_features = [
            'pass@1', 'pass@10', 'pass@100',
            'runtime_q25', 'runtime_q50', 'runtime_q75',
            'error_syntax', 'error_runtime', 'error_timeout'
        ]
        # For backward compatibility
        self.required_features = self.all_features

    def calculate_completeness(self) -> float:
        """
        Calculate percentage of complete model-benchmark pairs.

        For EXISTENCE hypothesis, a pair is complete if CORE features are present:
        - pass@1 (from published literature)
        - runtime quartiles (from benchmark execution)

        Extended features (pass@10, pass@100, error distributions) are optional
        and depend on data availability.
        """
        if len(self.feature_df) == 0:
            return 0.0

        total_pairs = len(self.feature_df)
        complete_pairs = 0

        for _, row in self.feature_df.iterrows():
            # Check if CORE features are present (not all features)
            is_complete = all(
                pd.notna(row.get(feat)) for feat in self.core_features
            )
            if is_complete:
                complete_pairs += 1

        completeness = (complete_pairs / total_pairs) * 100.0
        return completeness

    def check_standardization(self) -> Dict:
        """Check that features are standardized across benchmarks."""
        results = {}

        for feature in self.required_features:
            if feature not in self.feature_df.columns:
                results[feature] = {'standardized': False, 'reason': 'Missing column'}
                continue

            values = self.feature_df[feature].dropna()
            if len(values) == 0:
                results[feature] = {'standardized': False, 'reason': 'No data'}
                continue

            # Check for reasonable ranges
            if 'pass@' in feature:
                valid = all((0 <= v <= 100) for v in values)
                results[feature] = {'standardized': valid, 'range': [values.min(), values.max()]}
            elif 'runtime' in feature:
                valid = all(v >= 0 for v in values)
                results[feature] = {'standardized': valid, 'range': [values.min(), values.max()]}
            elif 'error' in feature:
                valid = all((0 <= v <= 100) for v in values)
                results[feature] = {'standardized': valid, 'range': [values.min(), values.max()]}

        return results

    def identify_missing_data(self) -> pd.DataFrame:
        """Identify patterns in missing data."""
        missing_data = []

        for idx, row in self.feature_df.iterrows():
            missing_features = [
                feat for feat in self.required_features
                if pd.isna(row.get(feat))
            ]

            if missing_features:
                missing_data.append({
                    'model': row.get('model', 'Unknown'),
                    'benchmark': row.get('benchmark', 'Unknown'),
                    'missing_features': ', '.join(missing_features),
                    'missing_count': len(missing_features)
                })

        return pd.DataFrame(missing_data)

    def validate_gate_condition(self) -> bool:
        """
        Validate EXISTENCE hypothesis gate condition.
        Returns True if completeness >= threshold (default 95%)
        """
        completeness = self.calculate_completeness()
        return completeness >= self.threshold

    def generate_report(self) -> Dict:
        """Generate comprehensive validation report."""
        completeness = self.calculate_completeness()
        standardization = self.check_standardization()
        missing_data = self.identify_missing_data()

        report = {
            'completeness_rate': completeness,
            'gate_passed': self.validate_gate_condition(),
            'threshold': self.threshold,
            'total_pairs': len(self.feature_df),
            'complete_pairs': int((completeness / 100.0) * len(self.feature_df)),
            'standardization': standardization,
            'missing_data_count': len(missing_data),
            'missing_data_summary': missing_data.to_dict('records') if len(missing_data) > 0 else []
        }

        return report
