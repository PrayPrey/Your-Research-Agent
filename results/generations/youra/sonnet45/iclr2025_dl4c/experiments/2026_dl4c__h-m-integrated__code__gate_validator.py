"""
MUST_WORK Gate Validator for H-M-integrated
"""
from typing import Dict

class GateValidator:
    """Validate MUST_WORK gate: M1 AND M2 must both pass"""
    
    def __init__(self, mechanism_results: dict):
        self.mechanism_results = mechanism_results
    
    def evaluate_gate(self) -> dict:
        """
        Evaluate MUST_WORK gate condition
        
        Gate logic:
        - M1_passed AND M2_passed → PASS
        - M1_failed OR M2_failed → FAIL
        
        Returns:
            dict with gate result and diagnostics
        """
        m1 = self.mechanism_results['m1']
        m2 = self.mechanism_results['m2']
        m3 = self.mechanism_results['m3']
        
        m1_passed = m1['m1_passed']
        m2_passed = m2['m2_passed']
        m3_passed = m3['m3_passed']
        
        # Gate passes if BOTH M1 and M2 pass
        gate_passed = m1_passed and m2_passed
        
        # Build diagnostics
        diagnostics = {
            'gate_result': 'PASS' if gate_passed else 'FAIL',
            'gate_type': 'MUST_WORK',
            'm1_status': 'PASS' if m1_passed else 'FAIL',
            'm2_status': 'PASS' if m2_passed else 'FAIL',
            'm3_status': 'PASS' if m3_passed else 'FAIL',  # M3 is optional
            'failure_reasons': []
        }
        
        # Record failure reasons
        if not m1_passed:
            diagnostics['failure_reasons'].append(
                f"M1 FAILED: Execution models mean correctness rank {m1['mean_rank']:.1f}% > {m1['threshold']}% threshold"
            )
        
        if not m2_passed:
            diagnostics['failure_reasons'].append(
                f"M2 FAILED: Preference models mean rank {m2['mean_rank']:.1f}% > {m2['threshold']}% threshold"
            )
        
        if not m3_passed:
            diagnostics['failure_reasons'].append(
                f"M3 FAILED: Mann-Whitney p-value {m3['mannwhitneyu_pvalue']:.4f} >= {0.05} threshold"
            )
        
        return diagnostics
