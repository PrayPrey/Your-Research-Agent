"""
Violation Rate Analyzer for H-M1
Computes per-class violation rates for normalization layer paradigms
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class ViolationRateAnalyzer:
    """
    Analyzes normalization layer violations for architecture families.

    Violation Definitions:
    - CNN violation: ln_count > bn_count (LayerNorm dominates in a CNN)
    - Transformer violation: bn_count > ln_count (BatchNorm dominates in a Transformer)
    - Hybrid: No violation (mixed patterns expected)
    """

    def __init__(self, threshold: float = 0.15):
        """
        Args:
            threshold: Maximum allowed violation rate (default 15%)
        """
        self.threshold = threshold

    def compute_violation_rates(self, features_df: pd.DataFrame) -> Dict:
        """
        Compute per-class violation rates for normalization paradigms.

        Args:
            features_df: DataFrame with columns [model_name, family, bn_count, ln_count, ...]

        Returns:
            {
                'cnn_violation_rate': float,
                'transformer_violation_rate': float,
                'cnn_violations': list[str],  # model names
                'transformer_violations': list[str],
                'cnn_passed': bool,  # ≤15% threshold
                'transformer_passed': bool,
                'gate_decision': str  # 'PASS' or 'FAIL'
            }
        """
        # Separate by family
        cnn_df = features_df[features_df['family'] == 'CNN']
        transformer_df = features_df[features_df['family'] == 'Transformer']

        # Compute CNN violations
        cnn_violation_rate, cnn_violations = self._compute_family_violation_rate(
            cnn_df, 'CNN'
        )

        # Compute Transformer violations
        transformer_violation_rate, transformer_violations = self._compute_family_violation_rate(
            transformer_df, 'Transformer'
        )

        # Check against threshold
        cnn_passed = cnn_violation_rate <= self.threshold
        transformer_passed = transformer_violation_rate <= self.threshold

        # Gate decision: both must pass
        gate_decision = 'PASS' if (cnn_passed and transformer_passed) else 'FAIL'

        return {
            'cnn_violation_rate': cnn_violation_rate,
            'transformer_violation_rate': transformer_violation_rate,
            'cnn_violations': cnn_violations,
            'transformer_violations': transformer_violations,
            'cnn_passed': cnn_passed,
            'transformer_passed': transformer_passed,
            'gate_decision': gate_decision,
            'threshold': self.threshold
        }

    def _compute_family_violation_rate(
        self,
        family_df: pd.DataFrame,
        family: str
    ) -> Tuple[float, List[str]]:
        """
        Compute violation rate for single family.

        Args:
            family_df: DataFrame filtered to single family
            family: 'CNN' or 'Transformer'

        Returns:
            (violation_rate, violating_model_names)
        """
        if len(family_df) == 0:
            return 0.0, []

        if family == 'CNN':
            # CNN violation: ln_count > bn_count
            violations = family_df[family_df['ln_count'] > family_df['bn_count']]
        elif family == 'Transformer':
            # Transformer violation: bn_count > ln_count
            violations = family_df[family_df['bn_count'] > family_df['ln_count']]
        else:
            # Hybrid: no violations expected (mixed patterns are normal)
            return 0.0, []

        violation_count = len(violations)
        total_count = len(family_df)
        violation_rate = violation_count / total_count if total_count > 0 else 0.0

        violating_models = violations['model_name'].tolist()

        return violation_rate, violating_models

    def save_violation_report(self, results: Dict, output_path: str):
        """Save violation rates to CSV."""
        report_data = []

        # CNN row
        report_data.append({
            'family': 'CNN',
            'total_models': len(results.get('cnn_violations', [])),
            'violations': len(results.get('cnn_violations', [])),
            'violation_rate': results['cnn_violation_rate'],
            'threshold': self.threshold,
            'status': 'PASS' if results['cnn_passed'] else 'FAIL'
        })

        # Transformer row
        report_data.append({
            'family': 'Transformer',
            'total_models': len(results.get('transformer_violations', [])),
            'violations': len(results.get('transformer_violations', [])),
            'violation_rate': results['transformer_violation_rate'],
            'threshold': self.threshold,
            'status': 'PASS' if results['transformer_passed'] else 'FAIL'
        })

        df = pd.DataFrame(report_data)
        df.to_csv(output_path, index=False)
