"""Gate condition evaluation module."""

from typing import Dict, List, Tuple


class GateConditionEvaluator:
    """Evaluate SHOULD_WORK gate condition for h-m1."""

    def __init__(self, correlations: Dict[str, Dict[str, float]], divergences: Dict[str, float]):
        """
        Initialize with correlation and divergence results.

        Args:
            correlations: Dict mapping pair_name to {"rho": float, "p_value": float}
            divergences: Dict mapping pair_name to kl_divergence value
        """
        self.correlations = correlations
        self.divergences = divergences

    def check_correlation_threshold(self, threshold: float = 0.8) -> Dict[str, any]:
        """
        Check if any benchmark pair has ρ < threshold.

        Args:
            threshold: Correlation threshold (default 0.8)

        Returns:
            Dictionary with check results
        """
        low_corr_pairs = []

        for pair_name, corr_data in self.correlations.items():
            rho = corr_data['rho']
            if rho < threshold:
                low_corr_pairs.append({
                    'pair': pair_name,
                    'rho': rho,
                    'p_value': corr_data['p_value']
                })

        return {
            'satisfied': len(low_corr_pairs) > 0,
            'threshold': threshold,
            'satisfying_pairs': low_corr_pairs
        }

    def check_divergence_threshold(self, threshold: float = 0.1) -> Dict[str, any]:
        """
        Check if any benchmark pair has KL divergence > threshold.

        Args:
            threshold: Divergence threshold (default 0.1)

        Returns:
            Dictionary with check results
        """
        high_div_pairs = []

        for pair_name, kl_value in self.divergences.items():
            if kl_value > threshold:
                high_div_pairs.append({
                    'pair': pair_name,
                    'kl_divergence': kl_value
                })

        return {
            'satisfied': len(high_div_pairs) > 0,
            'threshold': threshold,
            'satisfying_pairs': high_div_pairs
        }

    def evaluate_gate(
        self, corr_threshold: float = 0.8, div_threshold: float = 0.1
    ) -> Dict[str, any]:
        """
        Evaluate gate condition: (∃ pair: ρ < 0.8) AND (∃ pair: KL > 0.1).

        Args:
            corr_threshold: Correlation threshold
            div_threshold: Divergence threshold

        Returns:
            Dictionary with gate evaluation results
        """
        corr_check = self.check_correlation_threshold(corr_threshold)
        div_check = self.check_divergence_threshold(div_threshold)

        gate_satisfied = corr_check['satisfied'] and div_check['satisfied']

        return {
            'gate_satisfied': gate_satisfied,
            'gate_type': 'SHOULD_WORK',
            'correlation_check': corr_check,
            'divergence_check': div_check,
            'supporting_evidence': self._generate_evidence(corr_check, div_check, gate_satisfied)
        }

    def _generate_evidence(
        self, corr_check: Dict, div_check: Dict, gate_satisfied: bool
    ) -> List[str]:
        """Generate supporting evidence strings."""
        evidence = []

        if corr_check['satisfied']:
            pairs = [p['pair'] for p in corr_check['satisfying_pairs']]
            evidence.append(f"Low correlation pairs (ρ < {corr_check['threshold']}): {pairs}")

        if div_check['satisfied']:
            pairs = [p['pair'] for p in div_check['satisfying_pairs']]
            evidence.append(f"High divergence pairs (KL > {div_check['threshold']}): {pairs}")

        if gate_satisfied:
            evidence.append("Both conditions satisfied: Benchmarks show distinctive evaluation signatures")
        else:
            evidence.append("Gate condition NOT satisfied")

        return evidence
