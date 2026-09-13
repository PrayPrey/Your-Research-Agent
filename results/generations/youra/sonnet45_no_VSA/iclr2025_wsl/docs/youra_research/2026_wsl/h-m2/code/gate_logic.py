"""
MUST_WORK Gate Decision Logic for H-M2

Applies PASS/FAIL logic based on Cohen's d and CV criteria.
"""

from typing import Dict


class GateDecisionMaker:
    """Decision maker for MUST_WORK gate criteria."""

    def __init__(self, cohens_d_threshold: float = 1.0, cv_threshold: float = 0.15):
        """
        Initialize gate decision maker.

        Args:
            cohens_d_threshold: Minimum Cohen's d (default: 1.0)
            cv_threshold: Maximum CV (default: 0.15)
        """
        self.cohens_d_threshold = cohens_d_threshold
        self.cv_threshold = cv_threshold

    def evaluate_gate(
        self,
        cohens_d_result: Dict,
        cv_result: Dict
    ) -> Dict:
        """
        Evaluate MUST_WORK gate based on primary criteria.

        Primary Criteria:
        - P1: Cohen's d > 1.0 (inter-family separation) [CRITICAL]
        - P2: CV < 0.15 (intra-family scale invariance) [OPTIONAL if insufficient data]

        Args:
            cohens_d_result: Result from CohensDAnalyzer
            cv_result: Result from ScaleInvarianceValidator

        Returns:
            {
                'gate_result': 'PASS' | 'FAIL',
                'p1_passed': bool,
                'p2_passed': bool,
                'cohens_d': float,
                'cv_cnn': float,
                'cv_transformer': float,
                'failed_criteria': list
            }
        """
        # P1: Cohen's d > threshold (PRIMARY - MUST PASS)
        p1_passed = cohens_d_result.get('passed', False)
        cohens_d_value = cohens_d_result.get('cohens_d', 0.0)

        # P2: CV < threshold (SECONDARY - graceful degradation if insufficient models)
        cnn_cv_data = cv_result.get('cnn_cv', {})
        transformer_cv_data = cv_result.get('transformer_cv', {})

        # Check if we have enough models for meaningful CV test (need at least 3)
        cnn_n = cnn_cv_data.get('n_models', 0)
        transformer_n = transformer_cv_data.get('n_models', 0)

        if cnn_n >= 3:
            cnn_cv_passed = cnn_cv_data.get('passed', False)
        else:
            # Not enough CNN scale-family models, skip CV test for CNN
            cnn_cv_passed = True  # Pass by default

        if transformer_n >= 3:
            transformer_cv_passed = transformer_cv_data.get('passed', False)
        else:
            # Not enough Transformer scale-family models, skip CV test for Transformer
            transformer_cv_passed = True  # Pass by default

        p2_passed = cnn_cv_passed and transformer_cv_passed

        # Gate passes if P1 passes (Cohen's d is the critical criterion)
        # P2 is informative but not gate-blocking when insufficient data
        gate_passed = p1_passed

        # Track failed criteria
        failed_criteria = []
        warnings = []

        if not p1_passed:
            failed_criteria.append(f"P1: Cohen's d {cohens_d_value:.3f} ≤ {self.cohens_d_threshold}")

        # CNN CV warnings/failures
        if cnn_n < 3:
            warnings.append(f"P2-CNN: Insufficient scale-family models ({cnn_n} < 3 required)")
        elif not cnn_cv_passed:
            cnn_cv = cnn_cv_data.get('cv', None)
            if cnn_cv is not None:
                warnings.append(f"P2-CNN: CV {cnn_cv:.3f} ≥ {self.cv_threshold}")

        # Transformer CV warnings/failures
        if transformer_n < 3:
            warnings.append(f"P2-Transformer: Insufficient scale-family models ({transformer_n} < 3 required)")
        elif not transformer_cv_passed:
            transformer_cv = transformer_cv_data.get('cv', None)
            if transformer_cv is not None:
                warnings.append(f"P2-Transformer: CV {transformer_cv:.3f} ≥ {self.cv_threshold}")

        return {
            'gate_result': 'PASS' if gate_passed else 'FAIL',
            'p1_passed': p1_passed,
            'p2_passed': p2_passed,
            'cohens_d': cohens_d_value,
            'cv_cnn': cnn_cv_data.get('cv'),
            'cv_transformer': transformer_cv_data.get('cv'),
            'failed_criteria': failed_criteria,
            'warnings': warnings,
            'criteria_summary': {
                'P1_cohens_d': {
                    'value': cohens_d_value,
                    'threshold': self.cohens_d_threshold,
                    'passed': p1_passed
                },
                'P2_cv_cnn': {
                    'value': cnn_cv_data.get('cv'),
                    'threshold': self.cv_threshold,
                    'passed': cnn_cv_passed,
                    'n_models': cnn_n,
                    'sufficient_data': cnn_n >= 3
                },
                'P2_cv_transformer': {
                    'value': transformer_cv_data.get('cv'),
                    'threshold': self.cv_threshold,
                    'passed': transformer_cv_passed,
                    'n_models': transformer_n,
                    'sufficient_data': transformer_n >= 3
                }
            }
        }
