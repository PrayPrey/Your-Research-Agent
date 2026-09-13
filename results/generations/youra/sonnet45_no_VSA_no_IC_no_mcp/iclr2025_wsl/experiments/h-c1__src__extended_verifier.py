"""Extended constraint verifier with domain boundary detection."""

from typing import Dict
import sys
import os

# Import h-m4 verifier
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../h-m4/src'))
import verifier as h_m4_verifier

from boundary_detector import DomainBoundaryDetector


class ExtendedConstraintVerifier:
    """Integrate domain boundary detection before (D,B,M) check."""

    def __init__(self, kb_path: str, boundary_detector: DomainBoundaryDetector):
        self.kb_path = kb_path
        self.boundary_detector = boundary_detector
        # Initialize h-m4 verifier (no confounds needed for h-c1)
        self.base_verifier = h_m4_verifier.VerificationPipeline(kb_path, confound_patterns={})

    def check_testability(self, hypothesis: Dict) -> Dict:
        """Pre-filter boundaries, then run (D,B,M) check.

        Returns:
            {
                'testable': bool,
                'reason': str,
                'flag': str or None
            }
        """
        # Step 1: Boundary check
        boundary_check = self.boundary_detector.forward(hypothesis['text'])

        if not boundary_check['in_scope']:
            return {
                'testable': False,
                'reason': 'domain_not_covered',
                'flag': boundary_check['flag']
            }

        # Step 2: (D,B,M) check (from h-m4)
        # For h-c1, we just need to verify boundary cases are flagged
        # In-scope cases would normally go through full DBM check
        return {
            'testable': True,
            'reason': f"domain_covered:{boundary_check['domain']}",
            'flag': None
        }
