"""Gate Checking Module

Evaluates SHOULD_WORK gate criteria for hypothesis validation.
"""

from typing import Dict


class GateChecker:
    """Checks gate criteria for H-M1 hypothesis."""

    def __init__(
        self,
        primary_threshold: float = 0.30,
        secondary_threshold: float = 0.25,
        alpha: float = 0.05
    ):
        """Initialize gate checker.

        Args:
            primary_threshold: Minimum ρ for primary gate (Spearman)
            secondary_threshold: Minimum ρ for secondary gate (partial correlation)
            alpha: Significance level (default 0.05)
        """
        self.primary_threshold = primary_threshold
        self.secondary_threshold = secondary_threshold
        self.alpha = alpha

    def check_primary_gate(self, rho: float, p_value: float) -> Dict[str, bool]:
        """Check primary gate: Spearman ρ ≥ 0.30, p < 0.05.

        Args:
            rho: Spearman correlation coefficient
            p_value: One-tailed p-value

        Returns:
            Dict with keys: passed, rho_sufficient, p_significant
        """
        rho_sufficient = rho >= self.primary_threshold
        p_significant = p_value < self.alpha

        passed = rho_sufficient and p_significant

        return {
            'passed': passed,
            'rho_sufficient': rho_sufficient,
            'p_significant': p_significant,
            'rho': rho,
            'p_value': p_value,
            'threshold': self.primary_threshold
        }

    def check_secondary_gate(self, partial_rho: float, partial_p: float) -> Dict[str, bool]:
        """Check secondary gate: Partial ρ ≥ 0.25, p < 0.05.

        Args:
            partial_rho: Partial correlation coefficient (age-controlled)
            partial_p: Partial correlation p-value

        Returns:
            Dict with keys: passed, rho_sufficient, p_significant
        """
        rho_sufficient = partial_rho >= self.secondary_threshold
        p_significant = partial_p < self.alpha

        passed = rho_sufficient and p_significant

        return {
            'passed': passed,
            'rho_sufficient': rho_sufficient,
            'p_significant': p_significant,
            'rho': partial_rho,
            'p_value': partial_p,
            'threshold': self.secondary_threshold
        }

    def determine_routing(self, results: Dict) -> Dict:
        """Determine routing based on gate results.

        Args:
            results: Dict with 'primary' and 'secondary' gate results

        Returns:
            Dict with routing decision and recommendation
        """
        primary_passed = results.get('primary', {}).get('passed', False)
        secondary_passed = results.get('secondary', {}).get('passed', False)

        primary_rho = results.get('primary', {}).get('rho', 0.0)

        # Both gates pass: VALIDATED
        if primary_passed and secondary_passed:
            routing = {
                'status': 'PASS',
                'route_to': None,
                'recommendation': 'H-M1 validated: Community pressure mechanism confirmed',
                'next_step': 'Proceed to Phase 5 (Baseline Comparison)'
            }

        # Weak correlation (0.10 ≤ ρ < 0.30): MODIFY
        elif 0.10 <= primary_rho < self.primary_threshold:
            routing = {
                'status': 'PARTIAL',
                'route_to': 'Phase 2A (Modify)',
                'recommendation': 'Weak correlation detected. Modify hypothesis to test alternative activity metrics or confounders',
                'next_step': 'Redesign with different engagement metrics (stars, forks, PR activity)'
            }

        # No correlation (ρ < 0.10): FAIL → New mechanism
        else:
            routing = {
                'status': 'FAIL',
                'route_to': 'Phase 2A-Dialogue',
                'recommendation': 'Community pressure mechanism not supported. Explore alternative mechanisms (framework design, tool availability, training gaps)',
                'next_step': 'Generate new mechanism hypotheses'
            }

        return routing
