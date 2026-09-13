"""Mechanism evaluator for H-M1 - gate checking and report generation."""

from typing import Tuple, Dict
from datetime import datetime


class MechanismEvaluator:
    def __init__(
        self,
        accuracy_gap_threshold: float = 0.05,
        feature_overlap_threshold: int = 2
    ):
        """Initialize evaluator with gate thresholds."""
        self.accuracy_gap_threshold = accuracy_gap_threshold
        self.feature_overlap_threshold = feature_overlap_threshold

    def evaluate_mechanism(
        self,
        coefficient_signs: Dict[str, bool],
        performance_gap: float,
        feature_overlap: int
    ) -> Tuple[bool, Dict[str, any]]:
        """Evaluate mechanism validation gates.

        Args:
            coefficient_signs: Feature -> is_correct_sign
            performance_gap: LR vs GB accuracy gap
            feature_overlap: Number of overlapping top-3 features

        Returns:
            Tuple of (mechanism_validated: bool, detailed_report: dict)
        """
        # Check gates
        gate_1 = all(coefficient_signs.values())  # All signs correct
        gate_2 = performance_gap <= self.accuracy_gap_threshold  # Linear sufficient
        gate_3 = feature_overlap >= self.feature_overlap_threshold  # Causal alignment

        # Overall validation
        mechanism_validated = gate_1 and gate_2 and gate_3

        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'gates': {
                'EM-1_coefficient_signs': {
                    'passed': gate_1,
                    'details': coefficient_signs
                },
                'EM-2_performance_gap': {
                    'passed': gate_2,
                    'gap': performance_gap,
                    'threshold': self.accuracy_gap_threshold
                },
                'EM-3_feature_overlap': {
                    'passed': gate_3,
                    'overlap': feature_overlap,
                    'threshold': self.feature_overlap_threshold
                }
            },
            'overall': {
                'validated': mechanism_validated,
                'result': 'PASS' if mechanism_validated else 'FAIL'
            }
        }

        return mechanism_validated, detailed_report

    def generate_mechanism_report(self, results: Dict[str, any]) -> str:
        """Generate markdown validation report."""
        gates = results['gates']
        overall = results['overall']

        report = f"""# Mechanism Validation Results - H-M1

**Date:** {results['timestamp']}
**Overall Result:** {overall['result']}

## Gate Evaluation

### EM-1: Coefficient Signs
**Status:** {'✅ PASS' if gates['EM-1_coefficient_signs']['passed'] else '❌ FAIL'}

Coefficient sign verification:
"""

        for feature, is_correct in gates['EM-1_coefficient_signs']['details'].items():
            status = '✓' if is_correct else '✗'
            report += f"- {status} {feature}: {'Correct' if is_correct else 'Incorrect'}\n"

        report += f"""
### EM-2: Performance Gap (LR vs GB)
**Status:** {'✅ PASS' if gates['EM-2_performance_gap']['passed'] else '❌ FAIL'}

- **Gap:** {gates['EM-2_performance_gap']['gap']:.4f}
- **Threshold:** {gates['EM-2_performance_gap']['threshold']:.4f}
- **Linear Sufficient:** {gates['EM-2_performance_gap']['passed']}

### EM-3: Feature Importance Alignment
**Status:** {'✅ PASS' if gates['EM-3_feature_overlap']['passed'] else '❌ FAIL'}

- **Overlap Count:** {gates['EM-3_feature_overlap']['overlap']}/3
- **Threshold:** {gates['EM-3_feature_overlap']['threshold']}

## Conclusion

Mechanism validation: **{overall['result']}**

{'All gates passed - Linear separability mechanism confirmed.' if overall['validated'] else 'Some gates failed - See details above.'}
"""

        return report
